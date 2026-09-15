#!/usr/bin/env python3
"""
Paper 2 (Adversarial) - Extract (NFStream 9-fitur SFM) + Inferensi 4 model +
evaluasi ketahanan adversarial di TRAFIK AWS NYATA, di ANALYZER.
================================================================================
Melengkapi eksperimen benchmark (notebook 11/12) dengan validasi di trafik cloud
nyata. Untuk sebuah pcap AWS berlabel-timeline, notebook ini:
  1. Ekstrak 9 fitur SFM (sama seperti Paper 1 unsw_extract_infer.py).
  2. Ground-truth per-flow dari timeline serangan (benign/attack).
  3. Skor dengan KEEMPAT model Paper 2 (baseline/fewshot/adv/fewshot_adv).
  4. Untuk tiap model, hitung MCC pada:
       - clean (trafik AWS apa adanya),
       - FGSM functional-preserving eps in {0.05,0.1,0.2} pada fitur AWS
         (adaptive white-box: saliency dari model itu sendiri; proyeksi ke
         ruang valid protokol/fisik + monotonik add-only).
  Catatan: EVASION NETWORK-LEVEL (tc netem/window/rate) ditangani di sisi
  serangan (adv-attack-scenario.sh varian evasion) dan tercermin langsung pada
  pcap "evasion"; skrip ini mengukur MCC-nya sebagai 'clean' pada pcap tsb.
  FGSM di sini = lapisan evasion feature-space TAMBAHAN pada fitur yang diekstrak.

Model & scaler diletakkan di /opt/adv/models/<ARAH>/ :
  baseline.json, fewshot.json, adv.json, fewshot_adv.json, scaler.pkl
  (scaler.pkl: {'mean':[9], 'scale':[9], 'features':[...]}) - dari notebook 11.
ARAH default = CIC_to_UNSW (model sumber CIC; UNSW sbagai proxy target). Bisa
diganti via argumen; pilih arah yang scaler-nya sesuai domain pelatihan.

Usage (di Analyzer, setelah pcap ada):
  python3 adv-extract-infer.py <pcap> [ARAH]
  # contoh:
  python3 adv-extract-infer.py /opt/adv/captures/detect_evasion.pcap CIC_to_UNSW
"""
import sys, os, json, time, pickle
from datetime import datetime, timezone
import numpy as np, pandas as pd

MODEL_DIR = "/opt/adv/models"
RESULTS_DIR = "/opt/adv/results"
CANON = ["duration", "fwd_pkts", "bwd_pkts", "fwd_bytes", "bwd_bytes",
         "fwd_mean", "bwd_mean", "src_load", "dst_load"]
IX = {c: i for i, c in enumerate(CANON)}
VARIANTS = ["baseline", "fewshot", "adv", "fewshot_adv"]
EPS_EVAL = [0.05, 0.1, 0.2]
H = 0.01
SEED = 42

# Ground-truth timeline (menit) - pola adv-attack-scenario.sh (~7 menit)
GT = [(0, 1, "benign"), (1, 3, "attack"), (3, 5, "attack"),
      (5, 6, "attack"), (6, 7, "benign")]


def gt_label(elapsed_sec):
    m = elapsed_sec / 60.0
    for a, z, lab in GT:
        if a <= m < z:
            return lab
    return "benign"


def extract9(pcap):
    from nfstream import NFStreamer
    print(f"[1] NFStream: {pcap} ({os.path.getsize(pcap)/1e6:.1f} MB)")
    t0 = time.time()
    df = NFStreamer(source=pcap, statistical_analysis=True).to_pandas()
    print(f"    {len(df)} flow, {time.time()-t0:.1f}s")
    if len(df) == 0:
        return None, None
    dur_ms = df.get("bidirectional_duration_ms", pd.Series(np.zeros(len(df))))
    dur_feat_us = (dur_ms * 1000.0)                 # fitur duration -> mikrodetik (samakan CIC)
    dur_s = (dur_ms / 1000.0).replace(0, np.nan)    # pembagi laju -> detik
    out = pd.DataFrame({
        "duration": dur_feat_us.fillna(0),
        "fwd_pkts": df.get("src2dst_packets", 0).fillna(0),
        "bwd_pkts": df.get("dst2src_packets", 0).fillna(0),
        "fwd_bytes": df.get("src2dst_bytes", 0).fillna(0),
        "bwd_bytes": df.get("dst2src_bytes", 0).fillna(0),
        "fwd_mean": df.get("src2dst_mean_ps", 0).fillna(0),
        "bwd_mean": df.get("dst2src_mean_ps", 0).fillna(0),
        "src_load": (df.get("src2dst_bytes", 0) / dur_s).replace([np.inf, -np.inf], 0).fillna(0),
        "dst_load": (df.get("dst2src_packets", 0) / dur_s).replace([np.inf, -np.inf], 0).fillna(0),
    })[CANON].replace([np.inf, -np.inf], 0).fillna(0).astype(float)
    fs = df.get("bidirectional_first_seen_ms")
    elapsed = ((fs - fs.min()) / 1000.0).values if fs is not None else np.arange(len(df)) * 0.5
    return out, elapsed


def load_models(arah):
    import xgboost as xgb
    dd = os.path.join(MODEL_DIR, arah)
    with open(os.path.join(dd, "scaler.pkl"), "rb") as f:
        scd = pickle.load(f)
    mean = np.asarray(scd["mean"], float)
    scale = np.asarray(scd["scale"], float)
    models = {}
    for v in VARIANTS:
        p = os.path.join(dd, f"{v}.json")
        if os.path.exists(p):
            m = xgb.XGBClassifier() if _is_sklearn_json(p) else None
            try:
                from xgboost import XGBClassifier
                m = XGBClassifier(); m.load_model(p)
            except Exception:
                b = xgb.Booster(); b.load_model(p); m = b
            models[v] = m
    return models, mean, scale


def _is_sklearn_json(_p):
    return True  # XGBClassifier.load_model menangani kedua format; helper disederhanakan


def predict(model, Xs):
    """Prediksi label 1D, kompatibel XGBClassifier atau Booster."""
    import xgboost as xgb
    if hasattr(model, "predict_proba"):
        p = model.predict_proba(Xs)[:, 1]
    elif isinstance(model, xgb.Booster):
        p = model.predict(xgb.DMatrix(Xs))
    else:
        p = np.asarray(model.predict(Xs), float)
    return (p >= 0.5).astype(int), p


def loss_bin(model, Xs, y):
    _, p = predict(model, Xs)
    p = np.clip(p, 1e-15, 1 - 1e-15); y = y.astype(float)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def saliency(model, Xs, y, h=H):
    n, m = Xs.shape; S = np.zeros((n, m))
    for i in range(m):
        Xp = Xs.copy(); Xp[:, i] += h
        Xm = Xs.copy(); Xm[:, i] -= h
        S[:, i] = (loss_bin(model, Xp, y) - loss_bin(model, Xm, y)) / (2 * h)
    return S


def project_functional(Xadv_scaled, mean, scale):
    """Proyeksi ke ruang valid protokol/fisik (un-scale -> constraint -> re-scale)."""
    Xo = Xadv_scaled * scale + mean
    Xo = np.clip(Xo, 0.0, None)
    Xo[:, IX["fwd_pkts"]] = np.round(Xo[:, IX["fwd_pkts"]])
    Xo[:, IX["bwd_pkts"]] = np.round(Xo[:, IX["bwd_pkts"]])
    Xo[:, IX["fwd_bytes"]] = np.maximum(Xo[:, IX["fwd_bytes"]], Xo[:, IX["fwd_pkts"]])
    Xo[:, IX["bwd_bytes"]] = np.maximum(Xo[:, IX["bwd_bytes"]], Xo[:, IX["bwd_pkts"]])
    with np.errstate(divide="ignore", invalid="ignore"):
        fm = np.where(Xo[:, IX["fwd_pkts"]] > 0, Xo[:, IX["fwd_bytes"]] / Xo[:, IX["fwd_pkts"]], 0.0)
        bm = np.where(Xo[:, IX["bwd_pkts"]] > 0, Xo[:, IX["bwd_bytes"]] / Xo[:, IX["bwd_pkts"]], 0.0)
    Xo[:, IX["fwd_mean"]] = fm
    Xo[:, IX["bwd_mean"]] = bm
    return (Xo - mean) / scale


def fgsm_functional(Xs, S, eps, mean, scale):
    """FGSM + monotonik add-only (paket/byte/durasi hanya bertambah) + proyeksi valid."""
    Xadv = Xs + eps * np.sign(S)
    Xo = Xadv * scale + mean
    Xr = Xs * scale + mean
    for j in [IX[c] for c in ["fwd_pkts", "bwd_pkts", "fwd_bytes", "bwd_bytes", "duration"]]:
        Xo[:, j] = np.maximum(Xo[:, j], Xr[:, j])
    return project_functional((Xo - mean) / scale, mean, scale)


def main():
    if len(sys.argv) < 2:
        print("Usage: adv-extract-infer.py <pcap> [ARAH=CIC_to_UNSW]"); sys.exit(1)
    pcap = sys.argv[1]
    arah = sys.argv[2] if len(sys.argv) > 2 else "CIC_to_UNSW"
    os.makedirs(RESULTS_DIR, exist_ok=True)
    from sklearn.metrics import matthews_corrcoef, f1_score, precision_score, recall_score

    feats, elapsed = extract9(pcap)
    if feats is None:
        print("    0 flow - capture harus -i <iface>, BUKAN -i any."); sys.exit(0)
    y = np.array([1 if gt_label(e) == "attack" else 0 for e in elapsed])
    print(f"[2] ground-truth: attack={int(y.sum())} benign={int((y==0).sum())} (n={len(y)})")

    models, mean, scale = load_models(arah)
    if not models:
        print(f"    Tidak ada model di {os.path.join(MODEL_DIR, arah)} - lihat prasyarat."); sys.exit(1)
    Xs = ((feats.values.astype(float) - mean) / scale)
    Xs = np.nan_to_num(Xs, nan=0.0, posinf=0.0, neginf=0.0)

    base = os.path.splitext(os.path.basename(pcap))[0]
    rows = []
    for v, m in models.items():
        pred, _ = predict(m, Xs)
        row = {"pcap": os.path.basename(pcap), "arah": arah, "model": v, "n_flow": int(len(y)),
               "clean_mcc": round(float(matthews_corrcoef(y, pred)), 4) if len(set(y)) > 1 else None,
               "clean_recall": round(float(recall_score(y, pred, zero_division=0)), 4),
               "clean_precision": round(float(precision_score(y, pred, zero_division=0)), 4)}
        # FGSM functional-preserving (adaptive: saliency dari model m sendiri)
        S = saliency(m, Xs, y)
        for e in EPS_EVAL:
            Xf = fgsm_functional(Xs, S, e, mean, scale)
            predf, _ = predict(m, Xf)
            row[f"fgsm_functional_mcc_eps{e}"] = round(float(matthews_corrcoef(y, predf)), 4) if len(set(y)) > 1 else None
        rows.append(row)
        print(f"    [{v:12s}] clean MCC={row['clean_mcc']} | "
              f"fgsm eps0.1 MCC={row.get('fgsm_functional_mcc_eps0.1')}")

    out = {"generated": datetime.now(timezone.utc).isoformat(), "pcap": os.path.basename(pcap),
           "arah": arah, "features": CANON, "eps_eval": EPS_EVAL, "rows": rows}
    outp = os.path.join(RESULTS_DIR, f"{base}_advmetrics.json")
    json.dump(out, open(outp, "w"), indent=2)
    pd.DataFrame(rows).to_csv(os.path.join(RESULTS_DIR, f"{base}_advmetrics.csv"), index=False)
    print(f"[3] tersimpan {outp}")

    bucket = os.environ.get("S3_BUCKET", "")
    if bucket:
        import subprocess
        subprocess.run(["aws", "s3", "cp", RESULTS_DIR,
                        f"s3://{bucket}/unsw-far/paper2_aws/", "--recursive"],
                       capture_output=True)
        print(f"    diunggah ke s3://{bucket}/unsw-far/paper2_aws/")


if __name__ == "__main__":
    main()
