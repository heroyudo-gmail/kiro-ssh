#!/usr/bin/env python3
"""
benchmark_baseline.py
=====================
Perbandingan KUANTITATIF strategi kompresi (menjawab Reviewer A5):
membandingkan mekanisme ADAPTIF (rule-based) yang diusulkan terhadap beberapa
strategi BASELINE pada seluruh dataset (43 berkas):

  1. No-Compression       : tanpa kompresi (baseline penyimpanan)
  2. Static-Gzip          : satu algoritma statis untuk semua berkas (praktik umum)
  3. Static-Zstandard     : satu algoritma statis (rasio tinggi)
  4. Adaptive (proposed)  : seleksi rule-based per tipe/ukuran berkas

Untuk tiap strategi diukur: total ukuran setelah kompresi, penghematan penyimpanan
(%), total waktu proses (s), dan throughput agregat (MB/s).

Output: results/baseline_comparison.csv + .json
"""
import argparse
import csv
import json
import os
import time

from backup_system import compress, rule_based_select, _ALGOS


def load_dataset_with_types(dataset_dir, manifest_path):
    ftype = {}
    if os.path.exists(manifest_path):
        man = json.load(open(manifest_path))
        ftype = {m["file"]: m["type"] for m in man["files"]}
    items = []
    for name in sorted(os.listdir(dataset_dir)):
        p = os.path.join(dataset_dir, name)
        if not os.path.isfile(p) or name.endswith(".json"):
            continue
        with open(p, "rb") as f:
            data = f.read()
        t = ftype.get(name, os.path.splitext(name)[1].lstrip(".").lower())
        items.append((name, t, data))
    return items


def run_strategy(items, mode):
    """mode: 'none' | 'gzip' | 'zstd' | 'adaptive'. Return (bytes_after, seconds)."""
    total_after = 0
    t0 = time.perf_counter()
    for _name, ftype, data in items:
        if mode == "none":
            total_after += len(data)
            continue
        if mode == "adaptive":
            algo = rule_based_select(ftype, len(data))
        else:
            algo = mode  # 'gzip' atau 'zstd'
        if algo == "zstd" and not _ALGOS.get("zstd", False):
            algo = "gzip"
        comp = compress(data, algo)
        total_after += len(comp) if comp is not None else len(data)
    dt = time.perf_counter() - t0
    return total_after, dt


def main(dataset_dir, outdir, manifest_path):
    os.makedirs(outdir, exist_ok=True)
    items = load_dataset_with_types(dataset_dir, manifest_path)
    total_before = sum(len(d) for _, _, d in items)
    total_mb = total_before / 1024 / 1024
    print(f"Dataset: {len(items)} berkas, total {total_mb:.1f} MB")

    strategies = [
        ("No-Compression", "none"),
        ("Static-Gzip", "gzip"),
        ("Static-Zstandard", "zstd"),
        ("Adaptive (proposed)", "adaptive"),
    ]
    rows = []
    for label, mode in strategies:
        after, dt = run_strategy(items, mode)
        ss = (1 - after / total_before) * 100 if total_before else 0
        thr = total_mb / dt if dt > 0 else 0
        rows.append({
            "strategy": label,
            "size_before_mb": round(total_mb, 2),
            "size_after_mb": round(after / 1024 / 1024, 2),
            "storage_saving_pct": round(ss, 2),
            "time_s": round(dt, 3),
            "throughput_mb_s": round(thr, 1),
        })
        print(f"  {label:22} after={after/1024/1024:7.2f}MB  SS={ss:6.2f}%  "
              f"t={dt:6.2f}s  thr={thr:6.1f}MB/s")

    csv_path = os.path.join(outdir, "baseline_comparison.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    with open(os.path.join(outdir, "baseline_comparison.json"), "w", encoding="utf-8") as f:
        json.dump({"dataset_files": len(items), "dataset_mb": round(total_mb, 2),
                   "results": rows}, f, indent=2)
    print(f"\nSelesai -> {csv_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="./dataset_primer")
    ap.add_argument("--outdir", default="./results")
    ap.add_argument("--manifest", default="./dataset_primer/dataset_manifest.json")
    args = ap.parse_args()
    main(args.dataset, args.outdir, args.manifest)
