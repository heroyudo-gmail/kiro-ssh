#!/usr/bin/env python3
"""
benchmark_scalability.py
========================
Uji skalabilitas RTO (menjawab keraguan reviewer soal skala enterprise):
mengukur waktu siklus backup+recovery pada beberapa TOTAL UKURAN dataset yang
berbeda untuk membuktikan bahwa waktu pemulihan meningkat kira-kira LINEAR
terhadap volume data.

Untuk tiap ukuran target, dibangkitkan berkas CSV+LOG sintetis (pola realistis,
entropi rendah), lalu diukur:
  - waktu backup  : kompresi (rule-based) + AES-256 -> tulis air-gapped
  - waktu recovery: baca -> dekripsi -> dekompresi -> verifikasi hash

Output: results/scalability_rto.csv + .json
"""
import argparse
import csv
import hashlib
import json
import os
import shutil
import time

from backup_system import (compress, decompress, aes256_encrypt, aes256_decrypt,
                           rule_based_select, sha256_file)

try:
    from Crypto.Random import get_random_bytes
    KEY = get_random_bytes(32)
except Exception:
    KEY = b"0" * 32


def gen_csv(path, target_bytes):
    import random
    rows_batch = ("TXN{i:010d},2025-01-01 00:00:{s:02d},ACC{a:07d},TRANSFER,"
                  "{n}.00,IDR,JKT01,SUCCESS\n")
    with open(path, "w", encoding="utf-8") as f:
        i = 0
        while f.tell() < target_bytes:
            buf = []
            for _ in range(2000):
                i += 1
                buf.append(rows_batch.format(i=i, s=i % 60, a=random.randint(1, 5000),
                                             n=random.randint(1000, 99999999)))
            f.write("".join(buf))


def bench_size(workdir, airgap, target_mb):
    """Bangkitkan dataset ~target_mb, ukur waktu backup & recovery. Return dict."""
    ds = os.path.join(workdir, f"ds_{target_mb}")
    ag = os.path.join(airgap, f"ag_{target_mb}")
    for d in (ds, ag):
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(d)
    # bangkitkan beberapa berkas CSV mencapai target
    target_bytes = target_mb * 1024 * 1024
    n_files = 8
    per = target_bytes // n_files
    names = []
    for k in range(n_files):
        p = os.path.join(ds, f"data_{k:02d}.csv")
        gen_csv(p, per)
        names.append(p)

    # baseline hash + total ukuran
    baseline = {os.path.basename(p): {"sha256": sha256_file(p),
                "size": os.path.getsize(p)} for p in names}
    total_bytes = sum(v["size"] for v in baseline.values())

    # --- BACKUP: kompresi -> enkripsi -> air-gapped ---
    t0 = time.perf_counter()
    for p in names:
        with open(p, "rb") as f:
            plain = f.read()
        algo = rule_based_select("csv", len(plain))
        comp = compress(plain, algo)
        enc = aes256_encrypt(comp, KEY)
        with open(os.path.join(ag, os.path.basename(p) + f".{algo}.enc"), "wb") as f:
            f.write(enc)
    t_backup = time.perf_counter() - t0

    # --- RECOVERY: baca -> dekripsi -> dekompresi -> verifikasi ---
    t0 = time.perf_counter()
    ok = 0
    for p in names:
        base = os.path.basename(p)
        algo = rule_based_select("csv", baseline[base]["size"])
        blob_path = os.path.join(ag, base + f".{algo}.enc")
        with open(blob_path, "rb") as f:
            blob = f.read()
        comp = aes256_decrypt(blob, KEY)
        plain = decompress(comp, algo)
        out = os.path.join(ds, base)
        with open(out, "wb") as f:
            f.write(plain)
        if hashlib.sha256(plain).hexdigest() == baseline[base]["sha256"]:
            ok += 1
    t_recovery = time.perf_counter() - t0

    # bersihkan agar hemat disk
    shutil.rmtree(ds); shutil.rmtree(ag)
    return {
        "target_mb": target_mb,
        "actual_mb": round(total_bytes / 1024 / 1024, 1),
        "files": n_files,
        "backup_s": round(t_backup, 3),
        "recovery_rto_s": round(t_recovery, 3),
        "recovered_ok": ok,
    }


def main(outdir, sizes):
    workdir = "/tmp/scal_ds" if os.name != "nt" else "./_scal_ds"
    airgap = "/tmp/scal_ag" if os.name != "nt" else "./_scal_ag"
    os.makedirs(workdir, exist_ok=True); os.makedirs(airgap, exist_ok=True)
    os.makedirs(outdir, exist_ok=True)
    rows = []
    for mb in sizes:
        r = bench_size(workdir, airgap, mb)
        rows.append(r)
        print(f"  {mb:5} MB target -> {r['actual_mb']}MB  backup={r['backup_s']}s  "
              f"RTO={r['recovery_rto_s']}s  ok={r['recovered_ok']}/{r['files']}")
    with open(os.path.join(outdir, "scalability_rto.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    with open(os.path.join(outdir, "scalability_rto.json"), "w", encoding="utf-8") as f:
        json.dump({"results": rows}, f, indent=2)
    # koefisien linear kasar (RTO per MB)
    if len(rows) >= 2:
        import statistics
        rates = [r["recovery_rto_s"] / r["actual_mb"] for r in rows if r["actual_mb"] > 0]
        print(f"\nRTO rata-rata per MB: {statistics.mean(rates):.5f} s/MB "
              f"(std {statistics.pstdev(rates):.5f}) -> indikasi linear")
    print("Selesai -> scalability_rto.csv/json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="./results")
    ap.add_argument("--sizes", default="50,100,250,500,1000",
                    help="daftar ukuran MB dipisah koma")
    args = ap.parse_args()
    sizes = [int(x) for x in args.sizes.split(",")]
    main(args.outdir, sizes)
