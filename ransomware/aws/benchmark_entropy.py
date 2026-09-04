#!/usr/bin/env python3
"""
benchmark_entropy.py
====================
Analisis entropi Shannon (menghubungkan teori pada Pendahuluan dengan bukti empiris):

  Bagian A: entropi rata-rata per tipe berkas (CSV, LOG, JPG, XLSX) dan kaitannya
            dengan rasio kompresi (data entropi rendah -> kompresi tinggi).
  Bagian B: entropi berkas SEBELUM vs SESUDAH serangan ransomware (encrypt-and-hold),
            membuktikan lonjakan entropi sebagai indikator enkripsi tidak sah.

Entropi (bit/byte): H = -sum(p_i * log2(p_i)) atas distribusi 256 nilai byte.
Rentang 0..8; makin tinggi makin acak (mendekati terenkripsi/terkompresi).

Output: results/entropy_analysis.csv + .json
"""
import argparse
import csv
import json
import math
import os
import collections

from backup_system import compress, rule_based_select


def shannon_entropy(data):
    """Entropi Shannon (bit per byte) dari sebuah bytes."""
    if not data:
        return 0.0
    freq = collections.Counter(data)
    n = len(data)
    h = 0.0
    for c in freq.values():
        p = c / n
        h -= p * math.log2(p)
    return h


def sample_bytes(path, max_bytes=2_000_000):
    """Baca hingga max_bytes untuk entropi (cukup representatif, hemat waktu berkas besar)."""
    with open(path, "rb") as f:
        return f.read(max_bytes)


def analyze_by_type(dataset_dir, manifest_path):
    ftype = {}
    if os.path.exists(manifest_path):
        man = json.load(open(manifest_path))
        ftype = {m["file"]: m["type"] for m in man["files"]}
    agg = collections.defaultdict(lambda: {"H": [], "ss": []})
    for name in sorted(os.listdir(dataset_dir)):
        p = os.path.join(dataset_dir, name)
        if not os.path.isfile(p) or name.endswith(".json"):
            continue
        t = ftype.get(name, os.path.splitext(name)[1].lstrip(".").lower())
        data = sample_bytes(p)
        H = shannon_entropy(data)
        # rasio kompresi aktual (algoritma terpilih) pada sampel
        algo = rule_based_select(t, len(data))
        comp = compress(data, algo)
        ss = (1 - len(comp) / len(data)) * 100 if comp else 0
        agg[t]["H"].append(H)
        agg[t]["ss"].append(ss)
    rows = []
    for t in ["csv", "log", "xlsx", "jpg"]:
        if t not in agg:
            continue
        d = agg[t]
        rows.append({
            "type": t,
            "entropy_mean_bits": round(sum(d["H"]) / len(d["H"]), 3),
            "storage_saving_pct": round(sum(d["ss"]) / len(d["ss"]), 1),
        })
    return rows


def analyze_attack(dataset_dir, manifest_path):
    """Entropi sebelum vs sesudah 'encrypt-and-hold' (XOR keystream acak) pada sampel tiap tipe."""
    import random
    ftype = {}
    if os.path.exists(manifest_path):
        man = json.load(open(manifest_path))
        ftype = {m["file"]: m["type"] for m in man["files"]}
    # ambil satu berkas mewakili tiap tipe
    seen = {}
    for name in sorted(os.listdir(dataset_dir)):
        p = os.path.join(dataset_dir, name)
        if not os.path.isfile(p) or name.endswith(".json"):
            continue
        t = ftype.get(name, os.path.splitext(name)[1].lstrip(".").lower())
        if t not in seen:
            seen[t] = p
    rows = []
    for t, p in seen.items():
        data = sample_bytes(p)
        H_before = shannon_entropy(data)
        ks = bytes(random.randint(0, 255) for _ in range(min(len(data), 65536)))
        ks = (ks * (len(data) // len(ks) + 1))[:len(data)]
        enc = bytes(b ^ k for b, k in zip(data, ks))
        H_after = shannon_entropy(enc)
        rows.append({
            "type": t,
            "entropy_before": round(H_before, 3),
            "entropy_after_attack": round(H_after, 3),
            "delta": round(H_after - H_before, 3),
        })
    return rows


def main(dataset_dir, outdir, manifest_path):
    os.makedirs(outdir, exist_ok=True)
    import random
    random.seed(42)
    by_type = analyze_by_type(dataset_dir, manifest_path)
    attack = analyze_attack(dataset_dir, manifest_path)

    print("=== Entropi per tipe (bit/byte) vs penghematan kompresi ===")
    for r in by_type:
        print(f"  {r['type']:5} H={r['entropy_mean_bits']:.3f}  SS={r['storage_saving_pct']}%")
    print("\n=== Entropi sebelum vs sesudah serangan (encrypt-and-hold) ===")
    for r in attack:
        print(f"  {r['type']:5} {r['entropy_before']:.3f} -> {r['entropy_after_attack']:.3f}  (delta +{r['delta']:.3f})")

    with open(os.path.join(outdir, "entropy_analysis.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["type", "entropy_mean_bits", "storage_saving_pct"])
        for r in by_type:
            w.writerow([r["type"], r["entropy_mean_bits"], r["storage_saving_pct"]])
        w.writerow([])
        w.writerow(["type", "entropy_before", "entropy_after_attack", "delta"])
        for r in attack:
            w.writerow([r["type"], r["entropy_before"], r["entropy_after_attack"], r["delta"]])
    with open(os.path.join(outdir, "entropy_analysis.json"), "w", encoding="utf-8") as f:
        json.dump({"by_type": by_type, "attack": attack}, f, indent=2)
    print("\nSelesai -> entropy_analysis.csv/json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="./dataset_primer")
    ap.add_argument("--outdir", default="./results")
    ap.add_argument("--manifest", default="./dataset_primer/dataset_manifest.json")
    args = ap.parse_args()
    main(args.dataset, args.outdir, args.manifest)
