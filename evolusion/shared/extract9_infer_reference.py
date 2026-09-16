#!/usr/bin/env python3
"""
REFERENSI (disalin dari Paper 1: unswnb-15/aws/unsw_extract_infer.py).
================================================================================
Dipakai ulang di Paper 3 sebagai FONDASI ekstraksi 9-fitur SFM di ANALYZER.

APA YANG DIPAKAI ULANG APA ADANYA (jangan ulang dari nol):
  - `extract9()` — ekstraksi 9 fitur SFM dari pcap via NFStream.
  - AUDIT SATUAN kritis: fitur `duration` = MIKRODETIK (ms*1000) agar cocok scaler
    CIC; pembagi laju `dur_s` tetap DETIK. (Lihat komentar di dalam extract9.)
  - Pola scaling meta (`scaler_mean`, `scaler_scale`) & single-thread timing.

APA YANG BERBEDA UNTUK PAPER 3 (WAJIB diubah, jangan disalin buta):
  - Paper 1 = BINER (attack/normal, `binary:logistic`, threshold 0.5).
  - Paper 3 = MULTI-CLASS + OPEN-SET:
      * model `multi:softprob` (N kelas known).
      * setelah predict, hitung SKOR OPEN-SET (Mahalanobis ke centroid tiap kelas
        / confidence) -> tandai flow "unknown" bila jauh (min jarak > tau).
      * flow unknown -> buffer -> clustering (HDBSCAN) di luar skrip ini.
  - Ground-truth Fase 2 di sini biner; Paper 3 butuh label MULTI-CLASS per jenis
    serangan (dari oracle terjadwal).

Artefak model/meta (`modelA_9feat.json`, `deploy_meta_9feat.json`) TIDAK ikut di
repo (di S3/.gitignore). Untuk Paper 3 akan ada artefak multi-class sendiri
(mis. `model_multiclass_9feat.json` + `deploy_meta_mc.json` berisi juga centroid
& kovarians per-kelas untuk skor Mahalanobis).
"""
import sys, os, json, time
from datetime import datetime, timezone
import numpy as np, pandas as pd

MODEL_DIR = "/opt/evolusion/models"
RESULTS_DIR = "/opt/evolusion/results"
CANON = ["duration", "fwd_pkts", "bwd_pkts", "fwd_bytes", "bwd_bytes",
         "fwd_mean", "bwd_mean", "src_load", "dst_load"]


def extract9(pcap):
    """FONDASI reusable — ekstraksi 9 fitur SFM. Identik Paper 1."""
    from nfstream import NFStreamer
    print(f"[1] NFStream: {pcap} ({os.path.getsize(pcap)/1e6:.1f} MB)")
    t0 = time.time()
    df = NFStreamer(source=pcap, statistical_analysis=True).to_pandas()
    print(f"    {len(df)} flow, {time.time()-t0:.1f}s")
    if len(df) == 0:
        return None, None
    dur_ms = df.get("bidirectional_duration_ms", pd.Series(np.zeros(len(df))))
    # SATUAN (hasil audit 9 fitur): scaler deployment di-fit pada CIC/CICFlowMeter.
    #   - Fitur `duration` <- CIC `Flow Duration` = MIKRODETIK. NFStream memberi ms,
    #     jadi fitur duration = ms * 1000 (=us) agar COCOK dengan scaler CIC (mismatch 1e6 bila detik).
    #   - `src_load` <- CIC `Flow Byts/s` (byte/DETIK); `dst_load` <- CIC `Bwd Pkts/s` (paket/DETIK).
    #     Maka PEMBAGI laju TETAP dalam DETIK (dur_s), BUKAN mikrodetik.
    dur_feat_us = (dur_ms * 1000.0)
    dur_s = (dur_ms / 1000.0).replace(0, np.nan)
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


# --- TODO Paper 3: ganti head inferensi ke multi-class + open-set scorer ---
# def infer_multiclass_openset(feats):
#     1. scale via deploy_meta (scaler_mean/scale)
#     2. prob = booster.predict(DMatrix)  # multi:softprob -> [n, N_known]
#     3. pred_known = argmax(prob); conf = max(prob)
#     4. d_maha = min_k mahalanobis(x, mu_k, Sigma_k)   # dari deploy_meta_mc
#     5. is_unknown = (d_maha > tau) [| (conf < conf_thr)]
#     6. return pred_known, conf, d_maha, is_unknown


if __name__ == "__main__":
    print(__doc__)
    print("Ini berkas REFERENSI. Skrip runtime Paper 3 (multi-class + open-set) "
          "akan dibuat terpisah saat tahap AWS.")
