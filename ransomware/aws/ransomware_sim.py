#!/usr/bin/env python3
"""
ransomware_sim.py
=================
Simulasi serangan ransomware TERKONTROL (tanpa malware nyata) pada dataset PRIMER.
Hanya memodifikasi berkas di folder primer; cadangan di air-gapped TIDAK disentuh.

Tiga pola berbasis CVE (sesuai paper):
  1. encrypt_hold        (CVE-2017-0144 / pola WannaCry) : timpa konten dgn data
                           terenkripsi acak + ubah ekstensi ke .WNCRY + ubah mtime
  2. metadata_corruption (CVE-2018-8453)                : rusak header/awal berkas,
                           sisa berkas dibiarkan (keterbacaan parsial)
  3. overwrite_corrupt   (CVE-2021-36934)               : timpa sebagian isi dgn
                           byte acak (struktur kacau)

Menghasilkan attack_log.json: daftar berkas yang dimodifikasi + tipe serangan.
Catatan: karena ini destruktif pada folder primer, WAJIB dijalankan setelah backup.
"""
import argparse
import json
import os
import random
import time


def _read(path):
    with open(path, "rb") as f:
        return f.read()


def _write(path, data):
    with open(path, "wb") as f:
        f.write(data)


def attack_encrypt_hold(path):
    """WannaCry-like: seluruh konten 'terenkripsi' (acak) + ekstensi .WNCRY."""
    data = _read(path)
    # 'enkripsi' disimulasikan sebagai XOR dengan keystream acak + padding
    keystream = os.urandom(len(data)) if len(data) < 2_000_000 else os.urandom(2_000_000)
    ks = (keystream * (len(data) // len(keystream) + 1))[:len(data)]
    enc = bytes(b ^ k for b, k in zip(data, ks))
    enc += os.urandom(256)  # padding -> ukuran berubah
    new_path = path + ".WNCRY"
    _write(new_path, enc)
    os.remove(path)
    # ubah mtime jauh ke depan (jejak khas ransomware)
    future = time.time() + 86400
    os.utime(new_path, (future, future))
    return {"target": os.path.basename(path), "new_name": os.path.basename(new_path),
            "attack": "encrypt_hold", "cve": "CVE-2017-0144"}


def attack_metadata_corruption(path):
    """Rusak header/awal berkas; sisa dibiarkan (keterbacaan parsial)."""
    data = bytearray(_read(path))
    n = min(512, len(data))
    for i in range(n):
        data[i] = random.randint(0, 255)
    _write(path, bytes(data))
    return {"target": os.path.basename(path), "new_name": os.path.basename(path),
            "attack": "metadata_corruption", "cve": "CVE-2018-8453"}


def attack_overwrite_corrupt(path):
    """Timpa ~30% isi dengan byte acak di posisi tersebar (struktur kacau)."""
    data = bytearray(_read(path))
    size = len(data)
    n_corrupt = int(size * 0.30)
    # timpa blok-blok acak
    pos = 0
    remaining = n_corrupt
    block = max(1, size // 50)
    while remaining > 0 and pos < size:
        start = random.randint(0, max(0, size - block))
        for i in range(start, min(start + block, size)):
            data[i] = random.randint(0, 255)
        remaining -= block
        pos += block
    _write(path, bytes(data))
    return {"target": os.path.basename(path), "new_name": os.path.basename(path),
            "attack": "overwrite_corrupt", "cve": "CVE-2021-36934"}


ATTACKS = {
    "encrypt_hold": attack_encrypt_hold,
    "metadata_corruption": attack_metadata_corruption,
    "overwrite_corrupt": attack_overwrite_corrupt,
}


def run_attack(dataset_dir, attack_type, out_log):
    """Terapkan satu tipe serangan ke SELURUH berkas di dataset primer."""
    if attack_type not in ATTACKS:
        raise ValueError(f"attack_type harus salah satu dari {list(ATTACKS)}")
    fn = ATTACKS[attack_type]
    log = []
    for name in sorted(os.listdir(dataset_dir)):
        p = os.path.join(dataset_dir, name)
        if not os.path.isfile(p) or name.endswith(".json"):
            continue
        try:
            log.append(fn(p))
        except Exception as e:
            log.append({"target": name, "attack": attack_type, "error": str(e)})
    with open(out_log, "w", encoding="utf-8") as f:
        json.dump({"attack_type": attack_type, "count": len(log), "items": log}, f, indent=2)
    print(f"[attack:{attack_type}] {len(log)} berkas dimodifikasi -> {out_log}")
    return log


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="./dataset_primer")
    ap.add_argument("--attack", required=True, choices=list(ATTACKS.keys()))
    ap.add_argument("--out", default="./results/attack_log.json")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    random.seed(args.seed)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    run_attack(args.dataset, args.attack, args.out)
