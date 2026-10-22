#!/usr/bin/env python3
"""
NIDS01 Real-Traffic Extract + Inference
========================================
Pipeline lengkap untuk 1 skenario (RT-S1..RT-S4):

  1. Extract flow dari pcap dengan NFStream (statistical_analysis=True)
     + custom plugin InitWindowPlugin (Init Fwd/Bwd Win Byts).
  2. Map field NFStream -> Top-10 fitur CIC-IDS2018.
  3. Standardize dengan scaler dari deploy_meta.json.
  4. Predict dengan model sesuai skenario (baseline / robust).
  5. Ground-truth label per flow (timestamp phase + attacker IP).
  6. Hitung metrik: MCC, F1, Precision, Recall, Accuracy (binary: attack vs benign).
  7. Simpan hasil CSV.

Usage:
  python extract_and_infer.py --scenario RT-S1 \
      --pcap /opt/nids/captures/RT-S1.pcap \
      --models-dir /opt/nids/models \
      --schedule /opt/nids/scripts/schedule-nids01.json \
      --output-dir /opt/nids/results
"""
import argparse
import json
import os
import sys
import time
import numpy as np
import pandas as pd
from nfstream import NFStreamer, NFPlugin
from sklearn.metrics import (matthews_corrcoef, f1_score, precision_score,
                             recall_score, accuracy_score, confusion_matrix)
import xgboost as xgb


# ---------------------------------------------------------------------------
# Custom NFPlugin: ekstrak TCP window size paket pertama tiap arah
# ---------------------------------------------------------------------------
def _tcp_window_from_ip_packet(ip_packet, protocol):
    if protocol != 6 or ip_packet is None:
        return -1
    try:
        b = ip_packet
        if len(b) < 20:
            return -1
        version = b[0] >> 4
        if version == 4:
            ihl = (b[0] & 0x0F) * 4
        elif version == 6:
            ihl = 40
        else:
            return -1
        tcp_off = ihl
        if len(b) < tcp_off + 16:
            return -1
        return (b[tcp_off + 14] << 8) | b[tcp_off + 15]
    except Exception:
        return -1


class InitWindowPlugin(NFPlugin):
    def on_init(self, packet, flow):
        flow.udps.init_fwd_win_byts = -1
        flow.udps.init_bwd_win_byts = -1
        win = _tcp_window_from_ip_packet(packet.ip_packet, packet.protocol)
        if packet.direction == 0:
            flow.udps.init_fwd_win_byts = win
        else:
            flow.udps.init_bwd_win_byts = win

    def on_update(self, packet, flow):
        if packet.direction == 1 and flow.udps.init_bwd_win_byts == -1:
            flow.udps.init_bwd_win_byts = _tcp_window_from_ip_packet(
                packet.ip_packet, packet.protocol)
        elif packet.direction == 0 and flow.udps.init_fwd_win_byts == -1:
            flow.udps.init_fwd_win_byts = _tcp_window_from_ip_packet(
                packet.ip_packet, packet.protocol)


# ---------------------------------------------------------------------------
# Mapping NFStream -> Top-10 CIC-IDS2018
# Urutan HARUS sama dengan feature_names di deploy_meta.json
# ---------------------------------------------------------------------------
def build_feature_matrix(df, feature_names):
    """Bangun matriks fitur Top-10 dari DataFrame NFStream."""
    fmap = {
        "Fwd Seg Size Min":  df["src2dst_min_ps"],
        "URG Flag Cnt":      df["bidirectional_urg_packets"],
        "Tot Bwd Pkts":      df["dst2src_packets"],
        "Fwd Act Data Pkts": df["src2dst_packets"],
        "Fwd Pkt Len Max":   df["src2dst_max_ps"],
        "Fwd Pkt Len Mean":  df["src2dst_mean_ps"],
        "Bwd Pkt Len Mean":  df["dst2src_mean_ps"],
        "Init Bwd Win Byts": df["udps.init_bwd_win_byts"],
        "TotLen Bwd Pkts":   df["dst2src_bytes"],
        "Init Fwd Win Byts": df["udps.init_fwd_win_byts"],
    }
    cols = []
    for feat in feature_names:
        if feat not in fmap:
            raise KeyError(f"Feature '{feat}' tidak ada di mapping NFStream")
        cols.append(pd.to_numeric(fmap[feat], errors="coerce").fillna(0.0).values)
    X = np.column_stack(cols).astype(float)
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
    return X


# ---------------------------------------------------------------------------
# Ground truth labeling
# ---------------------------------------------------------------------------
def label_flows(df, schedule, test_start_ms):
    """Beri label ground truth per flow berdasarkan fase waktu + attacker IP."""
    attacker_ip = schedule["attacker_ip"]
    phases = schedule["phases"]
    labels = []
    for _, row in df.iterrows():
        # waktu flow relatif ke awal test (menit)
        elapsed_min = (row["bidirectional_first_seen_ms"] - test_start_ms) / 60000.0
        phase_label = "Benign"
        for ph in phases:
            if ph["start_min"] <= elapsed_min < ph["end_min"]:
                phase_label = ph["label"]
                break
        # attack hanya jika attacker IP terlibat DAN fase = attack
        if phase_label != "Benign":
            involves_attacker = (row["src_ip"] == attacker_ip or
                                 row["dst_ip"] == attacker_ip)
            labels.append(phase_label if involves_attacker else "Benign")
        else:
            labels.append("Benign")
    return labels


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", required=True, help="RT-S1|RT-S2|RT-S3|RT-S4")
    ap.add_argument("--pcap", required=True)
    ap.add_argument("--models-dir", default="/opt/nids/models")
    ap.add_argument("--schedule", default="/opt/nids/scripts/schedule-nids01.json")
    ap.add_argument("--output-dir", default="/opt/nids/results")
    args = ap.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print("=" * 60)
    print(f"NIDS01 INFERENCE - {args.scenario}")
    print("=" * 60)

    # 1. Load metadata
    with open(os.path.join(args.models_dir, "deploy_meta.json")) as f:
        meta = json.load(f)
    feature_names = meta["feature_names"]
    scaler_mean = np.array(meta["scaler"]["mean"])
    scaler_scale = np.array(meta["scaler"]["scale"])
    inverse_map = meta["inverse_label_mapping"]

    # pilih model berdasarkan skenario
    if args.scenario in ("RT-S1", "RT-S2"):
        model_file = meta["models"]["baseline"]
        model_kind = "baseline"
    else:
        model_file = meta["models"]["robust"]
        model_kind = "robust"
    print(f"[model] {model_kind} -> {model_file}")

    # 2. Extract flows
    print(f"[1] Extract flows dari {args.pcap} ...")
    t0 = time.time()
    streamer = NFStreamer(source=args.pcap, statistical_analysis=True,
                          udps=[InitWindowPlugin()])
    df = streamer.to_pandas()
    print(f"    {len(df)} flows dalam {time.time()-t0:.1f}s")
    if len(df) == 0:
        print("ERROR: 0 flows. Pastikan pcap valid dan di-capture per-interface (bukan -i any).")
        sys.exit(1)

    # 3. Feature matrix + scaling
    print("[2] Bangun fitur Top-10 + scaling ...")
    X = build_feature_matrix(df, feature_names)
    X_scaled = (X - scaler_mean) / scaler_scale
    X_scaled = np.nan_to_num(X_scaled, nan=0.0, posinf=0.0, neginf=0.0)

    # 4. Load model + predict
    print("[3] Load model + prediksi ...")
    model = xgb.XGBClassifier()
    model.load_model(os.path.join(args.models_dir, model_file))
    pred_idx = model.predict(X_scaled)
    pred_labels = [inverse_map.get(str(int(i)), f"Unknown_{i}") for i in pred_idx]

    # 5. Ground truth
    print("[4] Ground truth labeling ...")
    with open(args.schedule) as f:
        schedule = json.load(f)
    test_start_ms = df["bidirectional_first_seen_ms"].min()
    gt_labels = label_flows(df, schedule, test_start_ms)

    # 6. Metrik (binary: attack vs benign)
    print("[5] Hitung metrik (binary attack vs benign) ...")
    y_true_bin = np.array([0 if l == "Benign" else 1 for l in gt_labels])
    y_pred_bin = np.array([0 if l == "Benign" else 1 for l in pred_labels])

    mcc = matthews_corrcoef(y_true_bin, y_pred_bin) if len(set(y_true_bin)) > 1 else 0.0
    f1 = f1_score(y_true_bin, y_pred_bin, zero_division=0)
    prec = precision_score(y_true_bin, y_pred_bin, zero_division=0)
    rec = recall_score(y_true_bin, y_pred_bin, zero_division=0)
    acc = accuracy_score(y_true_bin, y_pred_bin)
    cm = confusion_matrix(y_true_bin, y_pred_bin, labels=[0, 1])

    # 7. Simpan hasil
    df_out = df[["src_ip", "dst_ip", "src_port", "dst_port", "protocol",
                 "bidirectional_packets", "bidirectional_first_seen_ms"]].copy()
    df_out["ground_truth"] = gt_labels
    df_out["predicted"] = pred_labels
    df_out["gt_bin"] = y_true_bin
    df_out["pred_bin"] = y_pred_bin
    out_csv = os.path.join(args.output_dir, f"{args.scenario}_results.csv")
    df_out.to_csv(out_csv, index=False)

    metrics = {
        "scenario": args.scenario,
        "model": model_kind,
        "total_flows": int(len(df)),
        "attack_flows_gt": int(y_true_bin.sum()),
        "benign_flows_gt": int((y_true_bin == 0).sum()),
        "MCC": round(float(mcc), 4),
        "F1": round(float(f1), 4),
        "Precision": round(float(prec), 4),
        "Recall": round(float(rec), 4),
        "Accuracy": round(float(acc), 4),
        "confusion_matrix": {"TN": int(cm[0, 0]), "FP": int(cm[0, 1]),
                             "FN": int(cm[1, 0]), "TP": int(cm[1, 1])},
    }
    out_json = os.path.join(args.output_dir, f"{args.scenario}_metrics.json")
    with open(out_json, "w") as f:
        json.dump(metrics, f, indent=2)

    # Ringkasan
    print("\n" + "=" * 60)
    print(f"HASIL {args.scenario} (model={model_kind})")
    print("=" * 60)
    print(f"  Total flows      : {metrics['total_flows']}")
    print(f"  Attack (GT)      : {metrics['attack_flows_gt']}")
    print(f"  Benign (GT)      : {metrics['benign_flows_gt']}")
    print(f"  MCC              : {metrics['MCC']}")
    print(f"  F1               : {metrics['F1']}")
    print(f"  Precision        : {metrics['Precision']}")
    print(f"  Recall           : {metrics['Recall']}")
    print(f"  Accuracy         : {metrics['Accuracy']}")
    print(f"  Confusion (TN,FP,FN,TP): {cm[0,0]},{cm[0,1]},{cm[1,0]},{cm[1,1]}")
    print(f"  Detail CSV       : {out_csv}")
    print(f"  Metrics JSON     : {out_json}")
    print("=" * 60)


if __name__ == "__main__":
    main()
