#!/usr/bin/env python3
"""
detector_recovery.py
====================
Lapisan deteksi & pemulihan:
  - Deteksi anomali dgn membandingkan SHA-256 + metadata berkas primer saat ini
    terhadap baseline.json. Berkas yang hash/ukuran/ekstensinya berubah, atau
    hilang (mis. diganti .WNCRY), ditandai sebagai indikasi ransomware.
  - Bila anomali terdeteksi -> aktifkan mode pemulihan air-gapped: dekompresi +
    dekripsi berkas dari air-gapped, kembalikan ke folder primer, verifikasi hash.
  - Hitung metrik: FP, TN, FN, TP -> FPR, FNR ; dan RTO (waktu pemulihan).

Dipakai untuk dua jenis evaluasi:
  * mode "normal"  : tidak ada serangan -> harus 0 deteksi (uji False Positive)
  * mode "attack"  : setelah serangan  -> harus semua terdeteksi (uji False Negative)
"""
import argparse
import json
import os
import time

from backup_system import (sha256_file, extract_metadata, decompress,
                           aes256_decrypt, ALGO_LIST)


def load_baseline(path):
    with open(path) as f:
        return json.load(f)


def detect(dataset_dir, baseline):
    """
    Bandingkan kondisi primer sekarang vs baseline.
    Return: dict {name: is_anomaly(bool)} untuk setiap berkas baseline.
    """
    result = {}
    current = set(os.listdir(dataset_dir))
    for name, ref in baseline.items():
        p = os.path.join(dataset_dir, name)
        if not os.path.exists(p):
            # berkas hilang (mis. diubah jadi name.WNCRY) -> anomali
            result[name] = True
            continue
        cur_hash = sha256_file(p)
        cur_meta = extract_metadata(p)
        anomaly = (cur_hash != ref["sha256"]
                   or cur_meta["size"] != ref["metadata"]["size"]
                   or cur_meta["ext"] != ref["metadata"]["ext"])
        result[name] = bool(anomaly)
    return result


def recover(dataset_dir, airgap_dir, baseline, key, manifest_path):
    """Pulihkan seluruh berkas dari air-gapped. Return (n_ok, n_err, rto_seconds)."""
    from backup_system import rule_based_select
    ftype_map = {}
    if os.path.exists(manifest_path):
        man = json.load(open(manifest_path))
        ftype_map = {m["file"]: m["type"] for m in man["files"]}

    t0 = time.perf_counter()
    n_ok = n_err = 0
    for name, ref in baseline.items():
        ftype = ftype_map.get(name, os.path.splitext(name)[1].lstrip(".").lower())
        algo = rule_based_select(ftype, ref["metadata"]["size"])
        blob_path = os.path.join(airgap_dir, algo, f"{name}.{algo}.enc")
        if not os.path.exists(blob_path):
            # cari di algoritma lain sebagai fallback
            found = None
            for a in ALGO_LIST:
                cand = os.path.join(airgap_dir, a, f"{name}.{a}.enc")
                if os.path.exists(cand):
                    found, algo = cand, a
                    break
            if not found:
                n_err += 1
                continue
            blob_path = found
        try:
            with open(blob_path, "rb") as f:
                blob = f.read()
            # URUTAN PEMULIHAN (kebalikan backup): DEKRIPSI dulu -> lalu DEKOMPRESI
            comp = aes256_decrypt(blob, key)       # 1) dekripsi
            plain = decompress(comp, algo)          # 2) dekompresi
            # bersihkan berkas terserang (mis. .WNCRY) lalu tulis ulang yang bersih
            wncry = os.path.join(dataset_dir, name + ".WNCRY")
            if os.path.exists(wncry):
                os.remove(wncry)
            out = os.path.join(dataset_dir, name)
            with open(out, "wb") as f:
                f.write(plain)
            os.utime(out, (ref["metadata"]["mtime"], ref["metadata"]["mtime"]))
            # verifikasi hash
            if sha256_file(out) == ref["sha256"]:
                n_ok += 1
            else:
                n_err += 1
        except Exception:
            n_err += 1
    rto = time.perf_counter() - t0
    return n_ok, n_err, rto


def evaluate(dataset_dir, baseline_json, airgap_dir, key_path, manifest_path,
             mode, out_json):
    """
    mode='normal': tak ada serangan -> deteksi harusnya 0 (uji FP).
    mode='attack': setelah serangan -> deteksi harusnya semua (uji FN), lalu recover.
    """
    baseline = load_baseline(baseline_json)
    with open(key_path, "rb") as f:
        key = f.read()

    det = detect(dataset_dir, baseline)
    n_total = len(det)
    n_detected = sum(1 for v in det.values() if v)

    result = {"mode": mode, "total_files": n_total, "detected": n_detected}

    if mode == "normal":
        # semua berkas AMAN. deteksi = False Positive.
        FP = n_detected
        TN = n_total - n_detected
        FPR = (FP / (FP + TN) * 100) if (FP + TN) else 0.0
        result.update({"FP": FP, "TN": TN, "FPR_pct": round(FPR, 4),
                       "actual_status": "safe"})
    else:
        # semua berkas TERSERANG. tidak terdeteksi = False Negative.
        TP = n_detected
        FN = n_total - n_detected
        FNR = (FN / (FN + TP) * 100) if (FN + TP) else 0.0
        result.update({"TP": TP, "FN": FN, "FNR_pct": round(FNR, 4),
                       "actual_status": "ransomware"})
        # aktifkan pemulihan air-gapped
        n_ok, n_err, rto = recover(dataset_dir, airgap_dir, baseline, key, manifest_path)
        result.update({"restore_ok": n_ok, "restore_err": n_err,
                       "rto_seconds": round(rto, 3),
                       "restore_mode": {"mode": "airgap",
                                        "reason": "ransomware_detected", "scope": "all"}})

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"[evaluate:{mode}] {json.dumps(result)[:200]}")
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="./dataset_primer")
    ap.add_argument("--baseline", default="./results/baseline.json")
    ap.add_argument("--airgap", default="/mnt/airgap/backup")
    ap.add_argument("--key", default="./results/aes_key.bin")
    ap.add_argument("--manifest", default="./dataset_primer/dataset_manifest.json")
    ap.add_argument("--mode", required=True, choices=["normal", "attack"])
    ap.add_argument("--out", default="./results/eval.json")
    args = ap.parse_args()
    evaluate(args.dataset, args.baseline, args.airgap, args.key, args.manifest,
             args.mode, args.out)
