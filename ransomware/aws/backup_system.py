#!/usr/bin/env python3
"""
backup_system.py
================
Pipeline cadangan sesuai arsitektur 3 lapisan paper:

  Lapisan aplikasi        : hitung SHA-256 + ekstraksi metadata -> baseline JSON
  Lapisan proteksi/kompresi: enkripsi AES-256 -> kompresi (5 algoritma, rule-based)
  Lapisan penyimpanan     : simpan ke penyimpanan air-gapped (folder yang di-mount)

Menghasilkan:
  - baseline.json         : hash + metadata tiap berkas (referensi integritas)
  - <airgap>/<algo>/*.enc.<algo> : berkas terenkripsi+terkompresi di air-gapped
  - compression_report.csv: rasio & waktu kompresi per algoritma/berkas
  - efficiency_report.csv : skor efisiensi gabungan MCDM/WSM per algoritma

Metrik (sesuai paper):
  CR = S_after/S_before ; SS% = (1 - CR)*100 ; waktu kompresi (s)
  E  = alpha*(1-CR) + beta*(1/T), alpha=beta=0.5 ; dinormalisasi E(%) = E/Emax*100

Kompresi rule-based (berdasar tipe & ukuran) menentukan algoritma "terpilih",
tetapi SEMUA algoritma tetap diukur agar bisa dibandingkan (Tabel 6 paper).
"""
import csv
import hashlib
import json
import mimetypes
import os
import time
import gzip

# Library kompresi (opsional; jika salah satu tak ada, dilewati dgn peringatan)
_ALGOS = {}
try:
    import zstandard as zstd
    _ALGOS["zstd"] = True
except Exception:
    _ALGOS["zstd"] = False
try:
    import brotli
    _ALGOS["brotli"] = True
except Exception:
    _ALGOS["brotli"] = False
try:
    import lz4.frame as lz4frame
    _ALGOS["lz4"] = True
except Exception:
    _ALGOS["lz4"] = False
try:
    import snappy
    _ALGOS["snappy"] = True
except Exception:
    _ALGOS["snappy"] = False
_ALGOS["gzip"] = True  # selalu ada

# Kripto AES-256
try:
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes
    _HAS_CRYPTO = True
except Exception:
    _HAS_CRYPTO = False

CHUNK = 1024 * 1024


# ----------------------------------------------------------------------------
# Lapisan aplikasi: hash + metadata
# ----------------------------------------------------------------------------
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(CHUNK), b""):
            h.update(blk)
    return h.hexdigest()


def extract_metadata(path):
    st = os.stat(path)
    mime, _ = mimetypes.guess_type(path)
    return {
        "size": st.st_size,
        "mtime": int(st.st_mtime),
        "mime": mime or "application/octet-stream",
        "ext": os.path.splitext(path)[1].lower(),
    }


def build_baseline(dataset_dir, out_json):
    baseline = {}
    for name in sorted(os.listdir(dataset_dir)):
        p = os.path.join(dataset_dir, name)
        if not os.path.isfile(p) or name.endswith(".json"):
            continue
        baseline[name] = {"sha256": sha256_file(p), "metadata": extract_metadata(p)}
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(baseline, f, indent=2)
    print(f"[baseline] {len(baseline)} berkas -> {out_json}")
    return baseline


# ----------------------------------------------------------------------------
# Lapisan proteksi: AES-256
# ----------------------------------------------------------------------------
def aes256_encrypt(data, key):
    """AES-256-GCM. Return: nonce(16) + tag(16) + ciphertext."""
    if not _HAS_CRYPTO:
        # fallback XOR (BUKAN aman; hanya agar pipeline jalan tanpa pycryptodome)
        return b"\x00" * 32 + bytes(b ^ 0x5A for b in data)
    cipher = AES.new(key, AES.MODE_GCM, nonce=get_random_bytes(16))
    ct, tag = cipher.encrypt_and_digest(data)
    return cipher.nonce + tag + ct


def aes256_decrypt(blob, key):
    if not _HAS_CRYPTO:
        return bytes(b ^ 0x5A for b in blob[32:])
    nonce, tag, ct = blob[:16], blob[16:32], blob[32:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ct, tag)


# ----------------------------------------------------------------------------
# Lapisan kompresi: 5 algoritma
# ----------------------------------------------------------------------------
def compress(data, algo):
    if algo == "gzip":
        return gzip.compress(data, compresslevel=6)
    if algo == "zstd" and _ALGOS["zstd"]:
        return zstd.ZstdCompressor(level=3).compress(data)
    if algo == "brotli" and _ALGOS["brotli"]:
        return brotli.compress(data, quality=5)
    if algo == "lz4" and _ALGOS["lz4"]:
        return lz4frame.compress(data)
    if algo == "snappy" and _ALGOS["snappy"]:
        return snappy.compress(data)
    return None


def decompress(data, algo):
    if algo == "gzip":
        return gzip.decompress(data)
    if algo == "zstd":
        return zstd.ZstdDecompressor().decompress(data)
    if algo == "brotli":
        return brotli.decompress(data)
    if algo == "lz4":
        return lz4frame.decompress(data)
    if algo == "snappy":
        return snappy.decompress(data)
    raise ValueError(algo)


def _first_available(*prefs):
    """Kembalikan algoritma pertama yang benar-benar tersedia; fallback ke gzip."""
    for a in prefs:
        if _ALGOS.get(a, False):
            return a
    return "gzip"


def rule_based_select(ftype, size_bytes):
    """
    Seleksi algoritma berbasis aturan (tipe & ukuran) - sesuai deskripsi paper.
    Teks kecil-menengah -> Snappy/LZ4 (cepat). Teks besar -> Zstandard (rasio tinggi).
    JPG (sudah terkompresi) -> algoritma ringan. XLSX besar -> LZ4/Zstd.
    Selalu jatuh ke algoritma yang TERSEDIA (fallback gzip) agar berkas pasti tercadangkan.
    """
    mb = size_bytes / 1024 / 1024
    if ftype in ("csv", "log", "txt"):
        if mb <= 100:
            return _first_available("snappy", "lz4", "zstd")
        return _first_available("zstd", "gzip")
    if ftype == "jpg":
        return _first_available("snappy", "lz4", "gzip")
    if ftype == "xlsx":
        if mb <= 250:
            return _first_available("lz4", "zstd")
        return _first_available("zstd", "gzip")
    return "gzip"


ALGO_LIST = ["gzip", "zstd", "brotli", "lz4", "snappy"]


def run_backup(dataset_dir, airgap_dir, key, manifest_path,
               comp_csv, eff_csv, baseline_json):
    """Jalankan backup penuh: baseline -> enkripsi -> kompresi (semua algo) -> air-gapped."""
    baseline = build_baseline(dataset_dir, baseline_json)

    # muat tipe berkas dari manifest bila ada
    ftype_map = {}
    if os.path.exists(manifest_path):
        man = json.load(open(manifest_path))
        ftype_map = {m["file"]: m["type"] for m in man["files"]}

    os.makedirs(airgap_dir, exist_ok=True)
    for algo in ALGO_LIST:
        os.makedirs(os.path.join(airgap_dir, algo), exist_ok=True)

    rows = []
    # akumulasi utk skor efisiensi per algoritma
    agg = {a: {"ss_sum": 0.0, "t_sum": 0.0, "n": 0} for a in ALGO_LIST}

    for name in sorted(baseline.keys()):
        src = os.path.join(dataset_dir, name)
        with open(src, "rb") as f:
            plain = f.read()
        s_before = len(plain)
        ftype = ftype_map.get(name, os.path.splitext(name)[1].lstrip(".").lower())
        # URUTAN: KOMPRESI DULU (mengurangi ukuran plaintext ber-redundansi tinggi),
        # BARU ENKRIPSI hasil kompresi. Ini benar secara teknis: data terenkripsi
        # ber-entropi tinggi tak dapat dikompresi. Rasio kompresi diukur pada tahap
        # kompresi plaintext (inilah penghematan penyimpanan yang sebenarnya).
        selected = rule_based_select(ftype, s_before)

        for algo in ALGO_LIST:
            if algo != "gzip" and not _ALGOS.get(algo, False):
                continue
            t0 = time.perf_counter()
            comp = compress(plain, algo)          # 1) kompresi plaintext
            dt = time.perf_counter() - t0
            if comp is None:
                continue
            s_after = len(comp)                    # ukuran setelah kompresi (untuk CR/SS)
            cr = s_after / s_before if s_before else 1.0
            ss = (1 - cr) * 100
            # simpan berkas terpilih ke air-gapped: kompresi -> lalu enkripsi (compress-then-encrypt)
            if algo == selected:
                enc = aes256_encrypt(comp, key)    # 2) enkripsi hasil kompresi
                dst = os.path.join(airgap_dir, algo, f"{name}.{algo}.enc")
                with open(dst, "wb") as f:
                    f.write(enc)
            rows.append({
                "file": name, "type": ftype, "algo": algo,
                "size_before": s_before, "size_after": s_after,
                "compression_ratio": round(cr, 4),
                "storage_saving_pct": round(ss, 2),
                "time_s": round(dt, 4),
                "selected": (algo == selected),
            })
            agg[algo]["ss_sum"] += (1 - cr)
            agg[algo]["t_sum"] += dt
            agg[algo]["n"] += 1

    # tulis laporan kompresi
    with open(comp_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"[compression] {len(rows)} baris -> {comp_csv}")

    # skor efisiensi gabungan MCDM/WSM (alpha=beta=0.5) lalu normalisasi
    alpha = beta = 0.5
    raw = {}
    for a, d in agg.items():
        if d["n"] == 0:
            continue
        mean_ss = d["ss_sum"] / d["n"]           # rata-rata (1-CR)
        mean_t = d["t_sum"] / d["n"]             # rata-rata waktu (s)
        inv_t = 1.0 / mean_t if mean_t > 0 else 0.0
        raw[a] = alpha * mean_ss + beta * inv_t
    emax = max(raw.values()) if raw else 1.0
    with open(eff_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["algo", "E_raw", "E_pct", "status"])
        for a, e in sorted(raw.items(), key=lambda x: -x[1]):
            epct = e / emax * 100 if emax else 0
            status = ("Excellent" if epct >= 90 else "Good" if epct >= 80
                      else "Fair" if epct >= 70 else "Poor")
            w.writerow([a, round(e, 4), round(epct, 2), status])
    print(f"[efficiency] -> {eff_csv}")
    return rows


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="./dataset_primer")
    ap.add_argument("--airgap", default="/mnt/airgap/backup")
    ap.add_argument("--outdir", default="./results")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    key = (get_random_bytes(32) if _HAS_CRYPTO else b"0" * 32)
    # simpan kunci agar restore bisa memakainya
    with open(os.path.join(args.outdir, "aes_key.bin"), "wb") as f:
        f.write(key)
    run_backup(
        args.dataset, args.airgap,
        key,
        os.path.join(args.dataset, "dataset_manifest.json"),
        os.path.join(args.outdir, "compression_report.csv"),
        os.path.join(args.outdir, "efficiency_report.csv"),
        os.path.join(args.outdir, "baseline.json"),
    )
