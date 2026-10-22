#!/usr/bin/env python3
"""
NIDS01 Real-Traffic Testing — Extract Flows + Inference
=========================================================
Dijalankan di EC2 Analyzer setelah capture selesai.

Usage:
    python3 nids01_extract_infer.py clean
    python3 nids01_extract_infer.py evasion

Output:
    /opt/nids/results/nids01_{scenario}_results.csv
    /opt/nids/results/nids01_{scenario}_summary.txt
"""

import sys
import os
import json
import time
import numpy as np
import pandas as pd
from nfstream import NFStreamer
from xgboost import XGBClassifier
from sklearn.metrics import matthews_corrcoef, f1_score, precision_score, recall_score
from datetime import datetime

# === CONFIG ===
MODEL_DIR = "/opt/nids/models/"
CAPTURE_DIR = "/opt/nids/captures/"
RESULTS_DIR = "/opt/nids/results/"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Ground truth timeline (menit)
GROUND_TRUTH = [
    {"start_min": 0, "end_min": 1, "label": "Benign"},
    {"start_min": 1, "end_min": 3, "label": "Brute Force"},      # SSH
    {"start_min": 3, "end_min": 5, "label": "Brute Force"},      # FTP
    {"start_min": 5, "end_min": 7, "label": "DoS"},              # Slowloris
    {"start_min": 7, "end_min": 9, "label": "DoS"},              # HTTP Flood
    {"start_min": 9, "end_min": 10, "label": "DDoS"},            # SYN Flood
    {"start_min": 10, "end_min": 12, "label": "Benign"},         # Cool-down
]

# Top-10 feature mapping: CIC-IDS2018 name → NFStream name
# NOTE: Beberapa fitur mungkin perlu post-processing
FEATURE_MAPPING = {
    "Fwd Seg Size Min": "src2dst_min_ps",
    "Tot Bwd Pkts": "dst2src_packets",
    "Fwd Pkt Len Max": "src2dst_max_ps",
    "Fwd Pkt Len Mean": "src2dst_mean_ps",
    "Bwd Pkt Len Mean": "dst2src_mean_ps",
    "TotLen Bwd Pkts": "dst2src_bytes",
    "Init Fwd Win Byts": "src2dst_first_win",      # Custom: TCP window pertama src→dst
    "Init Bwd Win Byts": "dst2src_first_win",      # Custom: TCP window pertama dst→src
    "URG Flag Cnt": "src2dst_urg_packets",          # Mungkin 0 di kebanyakan flows
    "Fwd Act Data Pkts": "src2dst_packets",         # Approximation
}


def get_ground_truth(elapsed_seconds):
    """Tentukan label berdasarkan elapsed time."""
    elapsed_min = elapsed_seconds / 60.0
    for phase in GROUND_TRUTH:
        if phase["start_min"] <= elapsed_min < phase["end_min"]:
            return phase["label"]
    return "Benign"


def extract_flows(pcap_path):
    """Extract flows dari pcap menggunakan NFStream."""
    print(f"[1] Extracting flows from: {pcap_path}")
    print(f"    File size: {os.path.getsize(pcap_path) / (1024*1024):.1f} MB")
    
    start = time.time()
    streamer = NFStreamer(source=pcap_path, statistical_analysis=True)
    flows_df = streamer.to_pandas()
    elapsed = time.time() - start
    
    print(f"    Done: {len(flows_df)} flows extracted in {elapsed:.1f}s")
    print(f"    Columns: {len(flows_df.columns)}")
    
    return flows_df


def prepare_features(flows_df):
    """Map NFStream columns ke Top-10 features."""
    print(f"[2] Mapping features...")
    
    # Check available columns
    available = set(flows_df.columns)
    print(f"    NFStream columns available: {len(available)}")
    
    features = pd.DataFrame()
    missing = []
    
    for cic_name, nfs_name in FEATURE_MAPPING.items():
        if nfs_name in available:
            features[cic_name] = flows_df[nfs_name].fillna(0)
        else:
            features[cic_name] = 0
            missing.append(f"{cic_name} (→ {nfs_name})")
    
    if missing:
        print(f"    WARNING: {len(missing)} features not found, filled with 0:")
        for m in missing:
            print(f"      - {m}")
    
    print(f"    Feature matrix: {features.shape}")
    return features


def run_inference(features_df, model_path, meta, model_name):
    """Jalankan inference dengan satu model."""
    print(f"    Running: {model_name}...")
    
    # Load model
    model = XGBClassifier()
    model.load_model(model_path)
    
    # Scale features
    scaler_mean = np.array(meta["scaler"]["mean"])
    scaler_scale = np.array(meta["scaler"]["scale"])
    
    X = features_df.values.astype(np.float64)
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
    X_scaled = (X - scaler_mean) / scaler_scale
    X_scaled = np.nan_to_num(X_scaled, nan=0.0, posinf=0.0, neginf=0.0)
    
    # Predict
    y_pred_idx = model.predict(X_scaled)
    
    # Map indices to labels
    inverse_map = meta["inverse_label_mapping"]
    y_pred_labels = [inverse_map.get(str(int(idx)), "Unknown") for idx in y_pred_idx]
    
    return y_pred_labels


def calculate_metrics(y_true, y_pred, scenario_name):
    """Hitung MCC, F1, Precision, Recall."""
    # Convert to numeric for sklearn
    all_labels = sorted(set(y_true) | set(y_pred))
    label_to_num = {l: i for i, l in enumerate(all_labels)}
    
    y_true_num = [label_to_num[l] for l in y_true]
    y_pred_num = [label_to_num[l] for l in y_pred]
    
    mcc = matthews_corrcoef(y_true_num, y_pred_num)
    f1 = f1_score(y_true_num, y_pred_num, average="weighted", zero_division=0)
    prec = precision_score(y_true_num, y_pred_num, average="weighted", zero_division=0)
    rec = recall_score(y_true_num, y_pred_num, average="weighted", zero_division=0)
    
    return {"scenario": scenario_name, "mcc": mcc, "f1": f1, "precision": prec, "recall": rec}


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 nids01_extract_infer.py <clean|evasion>")
        sys.exit(1)
    
    scenario = sys.argv[1]  # "clean" or "evasion"
    pcap_path = os.path.join(CAPTURE_DIR, f"nids01_{scenario}.pcap")
    
    if not os.path.exists(pcap_path):
        print(f"ERROR: {pcap_path} not found!")
        sys.exit(1)
    
    print("=" * 60)
    print(f"  NIDS01 EXTRACT & INFERENCE — Scenario: {scenario.upper()}")
    print("=" * 60)
    
    # 1. Extract flows
    flows_df = extract_flows(pcap_path)
    
    # 2. Prepare features
    features_df = prepare_features(flows_df)
    
    # 3. Assign ground truth based on timestamps
    print(f"[3] Assigning ground truth labels...")
    if "bidirectional_first_seen_ms" in flows_df.columns:
        first_ts = flows_df["bidirectional_first_seen_ms"].min()
        elapsed = (flows_df["bidirectional_first_seen_ms"] - first_ts) / 1000.0
    else:
        # Fallback: assume sequential
        elapsed = pd.Series(range(len(flows_df))) * (12 * 60 / len(flows_df))
    
    y_true = [get_ground_truth(e) for e in elapsed]
    print(f"    Labels assigned: {pd.Series(y_true).value_counts().to_dict()}")
    
    # 4. Load metadata
    print(f"[4] Loading models and metadata...")
    meta_path = os.path.join(MODEL_DIR, "deploy_meta.json")
    with open(meta_path, "r") as f:
        meta = json.load(f)
    
    # 5. Run inference with both models
    baseline_path = os.path.join(MODEL_DIR, "baseline_xgboost_top10.json")
    robust_path = os.path.join(MODEL_DIR, "robust_xgboost_top10.json")
    
    y_pred_baseline = run_inference(features_df, baseline_path, meta, "Baseline")
    y_pred_robust = run_inference(features_df, robust_path, meta, "Robust")
    
    # 6. Calculate metrics
    print(f"\n[5] Calculating metrics...")
    
    if scenario == "clean":
        s_baseline = "RT-S1"  # Baseline + Clean
        s_robust = "RT-S3"    # Robust + Clean
    else:
        s_baseline = "RT-S2"  # Baseline + Evasion
        s_robust = "RT-S4"    # Robust + Evasion
    
    metrics_baseline = calculate_metrics(y_true, y_pred_baseline, s_baseline)
    metrics_robust = calculate_metrics(y_true, y_pred_robust, s_robust)
    
    # 7. Print results
    print(f"\n{'=' * 60}")
    print(f"  RESULTS — {scenario.upper()} SCENARIO")
    print(f"{'=' * 60}")
    print(f"")
    print(f"  {'Skenario':<10} {'Model':<10} {'MCC':>8} {'F1':>8} {'Prec':>8} {'Recall':>8}")
    print(f"  {'-'*52}")
    print(f"  {s_baseline:<10} {'Baseline':<10} {metrics_baseline['mcc']:>8.4f} {metrics_baseline['f1']:>8.4f} {metrics_baseline['precision']:>8.4f} {metrics_baseline['recall']:>8.4f}")
    print(f"  {s_robust:<10} {'Robust':<10} {metrics_robust['mcc']:>8.4f} {metrics_robust['f1']:>8.4f} {metrics_robust['precision']:>8.4f} {metrics_robust['recall']:>8.4f}")
    print(f"")
    print(f"{'=' * 60}")
    
    # 8. Save results
    results_df = pd.DataFrame({
        "flow_id": range(len(y_true)),
        "elapsed_sec": elapsed.values,
        "ground_truth": y_true,
        "pred_baseline": y_pred_baseline,
        "pred_robust": y_pred_robust,
    })
    
    results_path = os.path.join(RESULTS_DIR, f"nids01_{scenario}_results.csv")
    results_df.to_csv(results_path, index=False)
    print(f"\nSaved: {results_path}")
    
    # Save summary
    summary_path = os.path.join(RESULTS_DIR, f"nids01_{scenario}_summary.txt")
    with open(summary_path, "w") as f:
        f.write(f"NIDS01 Real-Traffic Testing — {scenario.upper()}\n")
        f.write(f"Date: {datetime.now().isoformat()}\n")
        f.write(f"Pcap: {pcap_path}\n")
        f.write(f"Flows: {len(flows_df)}\n\n")
        f.write(f"{s_baseline} (Baseline+{scenario}): MCC={metrics_baseline['mcc']:.4f} F1={metrics_baseline['f1']:.4f}\n")
        f.write(f"{s_robust} (Robust+{scenario}):   MCC={metrics_robust['mcc']:.4f} F1={metrics_robust['f1']:.4f}\n")
    print(f"Saved: {summary_path}")


if __name__ == "__main__":
    main()
    
    # Upload semua hasil ke S3
    print("\n[6] Uploading results to S3...")
    import subprocess
    bucket = "ssh-detection-features-232032302717"
    
    cmds = [
        f"aws s3 cp /opt/nids/results/ s3://{bucket}/results/nids01/ --recursive",
        f"aws s3 cp /opt/nids/captures/ s3://{bucket}/captures/nids01/ --recursive",
        f"aws s3 cp /opt/nids/flows/ s3://{bucket}/flows/nids01/ --recursive",
    ]
    
    for cmd in cmds:
        print(f"  {cmd}")
        subprocess.run(cmd.split(), capture_output=True)
    
    print("  Done. All outputs saved to S3.")
    print(f"  Verify: aws s3 ls s3://{bucket}/results/nids01/")
