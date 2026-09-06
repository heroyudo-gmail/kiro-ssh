#!/usr/bin/env python3
"""
T10 UNSW-NB15 — Extract (NFStream 9-fitur SFM) + Inferensi XGBoost, di ANALYZER.
================================================================================
Dua mode:
  far     : Fase 1 (TANPA serangan). Semua benign -> tiap prediksi attack = false alarm.
            Hitung FAR + latensi inferensi single-thread (@1 vCPU) untuk Tabel efisiensi.
  detect  : Fase 2 (DENGAN serangan). Ground-truth dari timeline -> MCC/F1/Precision/Recall.

Model & meta offline diletakkan di /opt/unsw/models/:
  - modelA_9feat.json
  - deploy_meta_9feat.json  { "scaler_mean":[9], "scaler_scale":[9] }

Usage (di Analyzer, setelah download pcap dari S3):
  python3 unsw_extract_infer.py far    /opt/unsw/captures/far_20260101_00.pcap
  python3 unsw_extract_infer.py detect /opt/unsw/captures/detect_clean.pcap
"""
import sys, os, json, time
from datetime import datetime, timezone
import numpy as np, pandas as pd

MODEL_DIR = "/opt/unsw/models"
RESULTS_DIR = "/opt/unsw/results"
CANON = ["duration", "fwd_pkts", "bwd_pkts", "fwd_bytes", "bwd_bytes",
         "fwd_mean", "bwd_mean", "src_load", "dst_load"]

# Ground-truth timeline Fase 2 (menit) — pola attack_scenario.sh (~7 menit)
GT = [(0, 1, "benign"), (1, 3, "attack"), (3, 5, "attack"),
      (5, 6, "attack"), (6, 7, "benign")]


def extract9(pcap):
    from nfstream import NFStreamer
    print(f"[1] NFStream: {pcap} ({os.path.getsize(pcap)/1e6:.1f} MB)")
    t0 = time.time()
    df = NFStreamer(source=pcap, statistical_analysis=True).to_pandas()
    print(f"    {len(df)} flow, {time.time()-t0:.1f}s")
    if len(df) == 0:
        return None, None
    dur_ms = df.get("bidirectional_duration_ms", pd.Series(np.zeros(len(df))))
    # FIX satuan: training Model A memakai duration dalam DETIK (UNSW dur = CIC Flow Duration).
    # dur_feat_s -> nilai fitur duration (detik), flow durasi-0 tetap 0 (bukan NaN).
    # dur_s      -> pembagi untuk src_load/dst_load, 0 diganti NaN agar tak div-by-zero.
    dur_feat_s = (dur_ms / 1000.0)
    dur_s = dur_feat_s.replace(0, np.nan)
    out = pd.DataFrame({
        "duration": dur_feat_s.fillna(0),
        "fwd_pkts": df.get("src2dst_packets", 0).fillna(0),
        "bwd_pkts": df.get("dst2src_packets", 0).fillna(0),
        "fwd_bytes": df.get("src2dst_bytes", 0).fillna(0),
        "bwd_bytes": df.get("dst2src_bytes", 0).fillna(0),
        "fwd_mean": df.get("src2dst_mean_ps", 0).fillna(0),
        "bwd_mean": df.get("dst2src_mean_ps", 0).fillna(0),
        "src_load": (df.get("src2dst_bytes", 0) / dur_s).replace([np.inf, -np.inf], 0).fillna(0),
        "dst_load": (df.get("dst2src_packets", 0) / dur_s).replace([np.inf, -np.inf], 0).fillna(0),
    })[CANON].replace([np.inf, -np.inf], 0).fillna(0).astype(float)
    # elapsed detik dari flow pertama (utk ground-truth Fase 2)
    fs = df.get("bidirectional_first_seen_ms")
    elapsed = ((fs - fs.min()) / 1000.0).values if fs is not None else np.arange(len(df)) * 0.5
    return out, elapsed


def infer(feats):
    import xgboost as xgb
    with open(os.path.join(MODEL_DIR, "deploy_meta_9feat.json")) as f:
        meta = json.load(f)
    mean = np.asarray(meta["scaler_mean"], float)
    scale = np.asarray(meta["scaler_scale"], float)
    Xs = np.nan_to_num(((feats.values.astype(np.float32) - mean) / scale),
                       nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)
    b = xgb.Booster(); b.load_model(os.path.join(MODEL_DIR, "modelA_9feat.json"))
    b.set_param({"nthread": 1})            # single-thread = edge 1 vCPU
    t0 = time.time()
    prob = b.predict(xgb.DMatrix(Xs))
    infer_s = time.time() - t0
    return (prob >= 0.5).astype(int), prob, infer_s


def gt_label(elapsed_sec):
    m = elapsed_sec / 60.0
    for a, z, lab in GT:
        if a <= m < z:
            return lab
    return "benign"


def main():
    if len(sys.argv) < 3:
        print("Usage: unsw_extract_infer.py <far|detect> <pcap>"); sys.exit(1)
    mode, pcap = sys.argv[1], sys.argv[2]
    os.makedirs(RESULTS_DIR, exist_ok=True)
    feats, elapsed = extract9(pcap)
    if feats is None:
        print("    0 flow — capture harus -i <iface>, BUKAN -i any."); sys.exit(0)

    pred, prob, infer_s = infer(feats)
    n = len(pred)
    lat_us = (infer_s / n) * 1e6 if n else 0.0
    base = os.path.splitext(os.path.basename(pcap))[0]
    res = feats.copy(); res["pred"] = pred; res["prob_attack"] = prob

    if mode == "far":
        n_alert = int(pred.sum())          # semua benign -> alert = false alarm
        far = n_alert / n if n else 0.0
        res.to_csv(os.path.join(RESULTS_DIR, f"{base}_flows.csv"), index=False)
        rec = dict(ts=datetime.now(timezone.utc).isoformat(), mode="far",
                   pcap=os.path.basename(pcap), n_flow=n, n_false_alarm=n_alert,
                   far=round(far, 6), infer_latency_us_per_flow=round(lat_us, 2),
                   throughput_fps=round(n / infer_s) if infer_s else None)
        with open(os.path.join(RESULTS_DIR, "far_log.jsonl"), "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(f"[FAR] n_flow={n} false_alarm={n_alert} FAR={far:.4%} "
              f"lat={lat_us:.1f}us/flow(single-thread)")

    elif mode == "detect":
        from sklearn.metrics import (matthews_corrcoef, f1_score,
                                     precision_score, recall_score, accuracy_score)
        y_true = np.array([1 if gt_label(e) == "attack" else 0 for e in elapsed])
        res["ground_truth"] = y_true
        res.to_csv(os.path.join(RESULTS_DIR, f"{base}_flows.csv"), index=False)
        m = dict(mode="detect", pcap=os.path.basename(pcap), n_flow=n,
                 mcc=round(float(matthews_corrcoef(y_true, pred)), 4),
                 f1=round(float(f1_score(y_true, pred, zero_division=0)), 4),
                 precision=round(float(precision_score(y_true, pred, zero_division=0)), 4),
                 recall=round(float(recall_score(y_true, pred, zero_division=0)), 4),
                 accuracy=round(float(accuracy_score(y_true, pred)), 4),
                 infer_latency_us_per_flow=round(lat_us, 2))
        with open(os.path.join(RESULTS_DIR, f"{base}_metrics.json"), "w") as f:
            json.dump(m, f, indent=2)
        print(f"[DETECT] MCC={m['mcc']} F1={m['f1']} P={m['precision']} R={m['recall']} "
              f"(n={n}, attack_gt={int(y_true.sum())})")
    else:
        print("mode harus 'far' atau 'detect'"); sys.exit(1)

    bucket = os.environ.get("S3_BUCKET", "")
    if bucket:
        import subprocess
        subprocess.run(["aws", "s3", "cp", RESULTS_DIR,
                        f"s3://{bucket}/unsw-far/results/", "--recursive"],
                       capture_output=True)
        print(f"    diunggah ke s3://{bucket}/unsw-far/results/")


if __name__ == "__main__":
    main()
