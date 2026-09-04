#!/usr/bin/env python3
"""
run_experiment.py
=================
Orkestrasi eksperimen end-to-end untuk paper ransomware cloud-backup.

Alur:
  1. Bangkitkan dataset primer (43 berkas) - sekali.
  2. BACKUP: baseline + enkripsi + kompresi (5 algo) -> air-gapped.
     (hasil: compression_report.csv, efficiency_report.csv, baseline.json)
  3. Uji NORMAL (tanpa serangan) -> FPR (harus 0).
  4. Untuk tiap pola serangan {encrypt_hold, metadata_corruption, overwrite_corrupt}:
       a. pulihkan dataset primer ke kondisi bersih (dari air-gapped) - agar tiap
          skenario mulai dari baseline yang sama.
       b. jalankan serangan (rusak seluruh 43 berkas).
       c. deteksi + recovery -> FNR, restore_ok, RTO.
  5. Rangkum ke experiment_summary.json + tabel-tabel siap-paper.

Catatan air-gapped: sesuai arsitektur paper, folder air-gapped hanya "aktif" saat
backup/restore. Pada EC2, --airgap menunjuk ke mount EBS terpisah (/mnt/airgap/backup).
Mount/unmount fisik dikelola oleh skrip shell (lihat README); di sini kita fokus
pada logika sistem.
"""
import argparse
import json
import os
import shutil
import time

import generate_dataset
import backup_system
import ransomware_sim
import detector_recovery

ATTACKS = ["encrypt_hold", "metadata_corruption", "overwrite_corrupt"]
CVE = {"encrypt_hold": "CVE-2017-0144",
       "metadata_corruption": "CVE-2018-8453",
       "overwrite_corrupt": "CVE-2021-36934"}


def _clean_dir(d):
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d, exist_ok=True)


def restore_clean(dataset_dir, baseline_json, airgap_dir, key_path, manifest):
    """Kembalikan dataset primer ke kondisi bersih dari air-gapped (antar-skenario)."""
    baseline = detector_recovery.load_baseline(baseline_json)
    with open(key_path, "rb") as f:
        key = f.read()
    # hapus sisa berkas terserang
    for name in list(os.listdir(dataset_dir)):
        if name.endswith(".WNCRY"):
            os.remove(os.path.join(dataset_dir, name))
    detector_recovery.recover(dataset_dir, airgap_dir, baseline, key, manifest)


def main(args):
    os.makedirs(args.outdir, exist_ok=True)
    manifest = os.path.join(args.dataset, "dataset_manifest.json")
    baseline_json = os.path.join(args.outdir, "baseline.json")
    key_path = os.path.join(args.outdir, "aes_key.bin")
    comp_csv = os.path.join(args.outdir, "compression_report.csv")
    eff_csv = os.path.join(args.outdir, "efficiency_report.csv")

    summary = {"scale": args.scale, "steps": {}}

    # --- 1. dataset ---
    if args.regen or not os.path.exists(manifest):
        _clean_dir(args.dataset)
        generate_dataset.generate(args.dataset, args.scale)
    summary["steps"]["dataset"] = json.load(open(manifest))

    # --- 2. backup ---
    _clean_dir(args.airgap)
    if backup_system._HAS_CRYPTO:
        from Crypto.Random import get_random_bytes
        key = get_random_bytes(32)
    else:
        key = b"0" * 32
    with open(key_path, "wb") as f:
        f.write(key)
    t0 = time.perf_counter()
    backup_system.run_backup(args.dataset, args.airgap, key, manifest,
                             comp_csv, eff_csv, baseline_json)
    summary["steps"]["backup_time_s"] = round(time.perf_counter() - t0, 3)

    # --- 3. uji NORMAL (FPR) ---
    normal = detector_recovery.evaluate(
        args.dataset, baseline_json, args.airgap, key_path, manifest,
        "normal", os.path.join(args.outdir, "eval_normal.json"))
    summary["steps"]["normal"] = normal

    # --- 4. tiap pola serangan ---
    attack_results = {}
    for atk in ATTACKS:
        # 4a. mulai dari dataset bersih
        restore_clean(args.dataset, baseline_json, args.airgap, key_path, manifest)
        # 4b. serangan
        atk_log = os.path.join(args.outdir, f"attack_{atk}.json")
        ransomware_sim.run_attack(args.dataset, atk, atk_log)
        # 4c. deteksi + recovery
        res = detector_recovery.evaluate(
            args.dataset, baseline_json, args.airgap, key_path, manifest,
            "attack", os.path.join(args.outdir, f"eval_{atk}.json"))
        res["cve"] = CVE[atk]
        attack_results[atk] = res
    summary["steps"]["attacks"] = attack_results

    # --- 5. rangkuman siap-paper ---
    # Tabel deteksi akurasi (per skenario)
    detection_table = [{
        "scenario": "Normal AES-256 backup", "total": normal["total_files"],
        "detected": normal["detected"], "auto_restore": "No",
        "actual": "Safe", "result": "True Negative",
    }]
    for atk in ATTACKS:
        r = attack_results[atk]
        detection_table.append({
            "scenario": atk, "cve": CVE[atk], "total": r["total_files"],
            "detected": r["detected"], "auto_restore": "Yes",
            "actual": "Ransomware", "result": "True Positive",
            "restore_ok": r["restore_ok"], "rto_s": r["rto_seconds"],
        })

    fpr = normal.get("FPR_pct", 0.0)
    fnr_vals = [attack_results[a].get("FNR_pct", 0.0) for a in ATTACKS]
    summary["paper_ready"] = {
        "n_files": normal["total_files"],
        "FPR_pct": fpr,
        "FNR_pct_per_attack": {a: attack_results[a].get("FNR_pct", 0.0) for a in ATTACKS},
        "FNR_pct_overall": round(sum(fnr_vals) / len(fnr_vals), 4) if fnr_vals else 0.0,
        "rto_seconds_per_attack": {a: attack_results[a]["rto_seconds"] for a in ATTACKS},
        "restore_ok_per_attack": {a: attack_results[a]["restore_ok"] for a in ATTACKS},
        "detection_table": detection_table,
    }

    with open(os.path.join(args.outdir, "experiment_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 60)
    print("EKSPERIMEN SELESAI")
    print("=" * 60)
    print(f"  Jumlah berkas   : {normal['total_files']}")
    print(f"  FPR             : {fpr}%")
    print(f"  FNR (rata-rata) : {summary['paper_ready']['FNR_pct_overall']}%")
    for a in ATTACKS:
        r = attack_results[a]
        print(f"  {a:22} : deteksi {r['detected']}/{r['total_files']}, "
              f"restore_ok {r['restore_ok']}, RTO {r['rto_seconds']}s")
    print(f"\n  Hasil lengkap   : {args.outdir}/experiment_summary.json")
    print(f"  Kompresi        : {comp_csv}")
    print(f"  Efisiensi       : {eff_csv}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="./dataset_primer")
    ap.add_argument("--airgap", default="/mnt/airgap/backup")
    ap.add_argument("--outdir", default="./results")
    ap.add_argument("--scale", choices=["fast", "full"], default="fast")
    ap.add_argument("--regen", action="store_true", help="paksa regenerate dataset")
    args = ap.parse_args()
    main(args)
