#!/usr/bin/env python3
"""
benchmark_stats.py
==================
Analisis statistik tambahan (menjawab Reviewer A5/C5):
  - Repeated trials (default 5x) per algoritma pada seluruh dataset primer
  - Rata-rata (mean) & standar deviasi (std) waktu kompresi
  - Throughput (MB/s)
  - Utilisasi CPU (%) dan RAM (MB) selama kompresi (via psutil)

Mengompresi PLAINTEXT (konsisten dgn pipeline compress-then-encrypt).
Output: results/benchmark_stats.csv + benchmark_stats.json

Pemakaian:
  python3 benchmark_stats.py --dataset ./dataset_primer --outdir ./results --trials 5
"""
import argparse
import csv
import gc
import json
import os
import statistics
import time

# psutil untuk CPU/RAM
try:
    import psutil
    _HAS_PSUTIL = True
except Exception:
    _HAS_PSUTIL = False

from backup_system import compress, ALGO_LIST, _ALGOS


def load_dataset(dataset_dir):
    """Muat isi semua berkas dataset ke memori (agar I/O tidak mengganggu ukur waktu kompresi)."""
    blobs = []
    total = 0
    for name in sorted(os.listdir(dataset_dir)):
        p = os.path.join(dataset_dir, name)
        if not os.path.isfile(p) or name.endswith(".json"):
            continue
        with open(p, "rb") as f:
            data = f.read()
        blobs.append((name, data))
        total += len(data)
    return blobs, total


def bench(dataset_dir, outdir, trials):
    os.makedirs(outdir, exist_ok=True)
    blobs, total_bytes = load_dataset(dataset_dir)
    total_mb = total_bytes / 1024 / 1024
    print(f"Dataset: {len(blobs)} berkas, total {total_mb:.1f} MB, trials={trials}")

    proc = psutil.Process(os.getpid()) if _HAS_PSUTIL else None
    algos = [a for a in ALGO_LIST if a == "gzip" or _ALGOS.get(a, False)]

    rows = []
    detail = {}
    for algo in algos:
        times = []       # detik total kompresi seluruh dataset per trial
        cpu_samples = []
        ram_samples = []
        for t in range(trials):
            gc.collect()
            if proc:
                proc.cpu_percent(None)  # reset baseline
                ram_before = proc.memory_info().rss
            t0 = time.perf_counter()
            out_bytes = 0
            for _name, data in blobs:
                c = compress(data, algo)
                if c is not None:
                    out_bytes += len(c)
            dt = time.perf_counter() - t0
            times.append(dt)
            if proc:
                cpu_samples.append(proc.cpu_percent(None))
                ram_samples.append((proc.memory_info().rss - ram_before) / 1024 / 1024)
        mean_t = statistics.mean(times)
        std_t = statistics.pstdev(times) if len(times) > 1 else 0.0
        throughput = total_mb / mean_t if mean_t > 0 else 0.0
        cpu = statistics.mean(cpu_samples) if cpu_samples else None
        ram = statistics.mean(ram_samples) if ram_samples else None
        row = {
            "algo": algo,
            "trials": trials,
            "mean_time_s": round(mean_t, 4),
            "std_time_s": round(std_t, 4),
            "throughput_mb_s": round(throughput, 2),
            "cpu_pct": round(cpu, 1) if cpu is not None else "n/a",
            "ram_mb": round(ram, 1) if ram is not None else "n/a",
        }
        rows.append(row)
        detail[algo] = {"times_s": [round(x, 4) for x in times]}
        print(f"  {algo:8} mean={mean_t:.3f}s std={std_t:.3f}s "
              f"thr={throughput:.1f}MB/s cpu={row['cpu_pct']}% ram={row['ram_mb']}MB")

    csv_path = os.path.join(outdir, "benchmark_stats.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    json_path = os.path.join(outdir, "benchmark_stats.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"dataset_files": len(blobs), "dataset_mb": round(total_mb, 2),
                   "trials": trials, "psutil": _HAS_PSUTIL,
                   "results": rows, "detail": detail}, f, indent=2)
    print(f"\nSelesai. {csv_path} & {json_path}")
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="./dataset_primer")
    ap.add_argument("--outdir", default="./results")
    ap.add_argument("--trials", type=int, default=5)
    args = ap.parse_args()
    bench(args.dataset, args.outdir, args.trials)
