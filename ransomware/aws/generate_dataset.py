#!/usr/bin/env python3
"""
generate_dataset.py
===================
Membangkitkan dataset sintetis 43 berkas (Opsi Cepat, ukuran dikecilkan agar
eksperimen cepat namun POLA/ENTROPI tetap realistis sesuai spesifikasi paper):

  - 9  CSV      : data transaksi finansial berpola berulang (entropi rendah -> kompresi tinggi)
  - 9  LOG/TXT  : log aplikasi/audit berpola (entropi rendah -> kompresi tinggi)
  - 14 JPG      : gambar JPEG (sudah terkompresi -> kompresi lossless rendah)
  - 11 XLSX     : spreadsheet laporan (kontainer ZIP -> kompresi menengah)
  Total = 43 berkas.

Opsi Cepat: ukuran maksimum ~50 MB per berkas. Kolom 'paper_size' pada spesifikasi
(hingga 1 GB) tetap dicatat di manifest untuk keperluan proyeksi RTO di paper.

Pemakaian:
  python3 generate_dataset.py --out /path/ke/dataset_primer [--scale fast|full]

Menghasilkan berkas + 'dataset_manifest.json' (daftar berkas, ukuran nyata, tipe).
"""
import argparse
import csv
import io
import json
import os
import random
import struct
import zlib
from datetime import datetime, timedelta

# ----------------------------------------------------------------------------
# Spesifikasi ukuran. 'paper' = ukuran di paper (untuk proyeksi), 'fast' = Opsi Cepat.
# ----------------------------------------------------------------------------
CSV_SPEC = [  # (nama, ukuran_paper_bytes, ukuran_fast_bytes)
    ("transaksi_01.csv", 500 * 1024,        500 * 1024),
    ("transaksi_02.csv", 1 * 1024**2,       1 * 1024**2),
    ("transaksi_03.csv", 5 * 1024**2,       3 * 1024**2),
    ("transaksi_04.csv", 25 * 1024**2,      6 * 1024**2),
    ("transaksi_05.csv", 100 * 1024**2,     10 * 1024**2),
    ("transaksi_06.csv", 250 * 1024**2,     15 * 1024**2),
    ("transaksi_07.csv", 500 * 1024**2,     25 * 1024**2),
    ("transaksi_08.csv", 750 * 1024**2,     40 * 1024**2),
    ("transaksi_09.csv", 1 * 1024**3,       50 * 1024**2),
]
LOG_SPEC = [
    ("app_01.log",   500 * 1024,      500 * 1024),
    ("app_02.log",   1 * 1024**2,     1 * 1024**2),
    ("app_03.log",   10 * 1024**2,    4 * 1024**2),
    ("app_04.log",   50 * 1024**2,    8 * 1024**2),
    ("audit_01.log", 100 * 1024**2,   12 * 1024**2),
    ("audit_02.log", 250 * 1024**2,   18 * 1024**2),
    ("audit_03.log", 500 * 1024**2,   28 * 1024**2),
    ("sys_01.txt",   750 * 1024**2,   40 * 1024**2),
    ("sys_02.txt",   1 * 1024**3,     50 * 1024**2),
]
# JPG: ukuran sama untuk fast & paper (memang kecil 154-249 KB)
JPG_SIZES_KB = [154, 161, 168, 175, 183, 190, 197, 205, 212, 220, 227, 234, 242, 249]
XLSX_SPEC = [
    ("lap_01.xlsx", 500 * 1024,     500 * 1024),
    ("lap_02.xlsx", 2 * 1024**2,    2 * 1024**2),
    ("lap_03.xlsx", 10 * 1024**2,   4 * 1024**2),
    ("lap_04.xlsx", 50 * 1024**2,   8 * 1024**2),
    ("lap_05.xlsx", 100 * 1024**2,  12 * 1024**2),
    ("lap_06.xlsx", 150 * 1024**2,  16 * 1024**2),
    ("lap_07.xlsx", 250 * 1024**2,  20 * 1024**2),
    ("lap_08.xlsx", 350 * 1024**2,  26 * 1024**2),
    ("lap_09.xlsx", 450 * 1024**2,  32 * 1024**2),
    ("lap_10.xlsx", 550 * 1024**2,  40 * 1024**2),
    ("lap_11.xlsx", 650 * 1024**2,  50 * 1024**2),
]

CURRENCIES = ["IDR", "USD", "SGD", "EUR"]
TXN_TYPES = ["TRANSFER", "PAYMENT", "WITHDRAWAL", "DEPOSIT", "REFUND"]
BRANCHES = ["JKT01", "SBY02", "BDG03", "MDN04", "MKS05"]
STATUS = ["SUCCESS", "PENDING", "FAILED"]
LOG_LEVELS = ["INFO", "WARN", "ERROR", "DEBUG"]
LOG_MODULES = ["auth", "db", "api", "backup", "scheduler", "cache"]
LOG_MSGS = [
    "request processed successfully",
    "connection established to node",
    "cache miss, fetching from origin",
    "transaction committed to ledger",
    "retry attempt for pending job",
    "session token refreshed",
]


def _write_csv(path, target_bytes):
    """CSV transaksi berpola berulang -> redundansi tinggi (entropi rendah)."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "tanggal", "akun", "tipe", "nominal", "mata_uang", "cabang", "status"])
        base = datetime(2025, 1, 1)
        i = 0
        while f.tell() < target_bytes:
            for _ in range(500):  # tulis per batch untuk efisiensi
                i += 1
                row = [
                    f"TXN{i:010d}",
                    (base + timedelta(seconds=i)).strftime("%Y-%m-%d %H:%M:%S"),
                    f"ACC{random.randint(1, 5000):07d}",
                    random.choice(TXN_TYPES),
                    f"{random.randint(1000, 99999999)}.00",
                    random.choice(CURRENCIES),
                    random.choice(BRANCHES),
                    random.choice(STATUS),
                ]
                w.writerow(row)
            if f.tell() >= target_bytes:
                break


def _write_log(path, target_bytes):
    """Log berpola template -> redundansi tinggi."""
    with open(path, "w", encoding="utf-8") as f:
        base = datetime(2025, 1, 1)
        i = 0
        buf = []
        while True:
            for _ in range(1000):
                i += 1
                ts = (base + timedelta(milliseconds=i * 137)).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                line = f"[{ts}] [{random.choice(LOG_LEVELS)}] [{random.choice(LOG_MODULES)}] {random.choice(LOG_MSGS)} (job={i})\n"
                buf.append(line)
            f.write("".join(buf))
            buf.clear()
            if f.tell() >= target_bytes:
                break


def _write_jpg(path, target_bytes):
    """
    Tulis JPEG realistis (sudah terkompresi -> entropi tinggi).
    Pakai Pillow bila ada; jika tidak, fallback ke berkas biner acak berukuran
    sama (juga entropi tinggi, cukup untuk menunjukkan kompresi lossless rendah).
    """
    try:
        from PIL import Image
        import numpy as np
        # gambar noise + gradient agar JPEG tidak terlalu kecil
        side = 900
        arr = (np.random.rand(side, side, 3) * 255).astype("uint8")
        grad = np.tile(np.linspace(0, 255, side, dtype="uint8"), (side, 1))
        arr[:, :, 0] = grad
        img = Image.fromarray(arr, "RGB")
        q = 85
        # kalibrasi kualitas agar dekat target_bytes
        for _ in range(6):
            bio = io.BytesIO()
            img.save(bio, format="JPEG", quality=q)
            size = bio.tell()
            if size >= target_bytes:
                break
            side = int(side * 1.15)
            arr = (np.random.rand(side, side, 3) * 255).astype("uint8")
            img = Image.fromarray(arr, "RGB")
        with open(path, "wb") as f:
            f.write(bio.getvalue())
    except Exception:
        # Fallback: data acak (entropi tinggi) dengan header JPEG minimal
        with open(path, "wb") as f:
            f.write(b"\xff\xd8\xff\xe0")  # SOI + APP0 marker
            f.write(os.urandom(max(0, target_bytes - 4)))


def _write_xlsx(path, target_bytes):
    """
    Spreadsheet .xlsx (kontainer ZIP berisi XML). Pakai openpyxl bila ada.
    Isi angka+teks berulang -> kompresi menengah. Fallback: ZIP berisi XML sintetis.
    """
    # .xlsx dibangun LANGSUNG sebagai ZIP+XML (Open Packaging Convention).
    # Jauh lebih cepat & ukuran terkontrol dibanding openpyxl untuk berkas besar.
    # Hasil tetap berkas .xlsx VALID (dapat dibuka Excel/LibreOffice).
    import zipfile

    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '</Types>')
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '</Relationships>')
    workbook = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="Laporan" sheetId="1" r:id="rId1"/></sheets></workbook>')
    wb_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        '</Relationships>')

    # Bangun sheetData sebagai teks (data berulang -> entropi rendah-menengah).
    # Estimasi jumlah baris dari target berdasarkan ukuran XML mentah (~120 byte/baris);
    # ZIP akan memampatkannya, jadi hasil akhir < target (wajar untuk xlsx).
    def make_row(n):
        return (f'<row r="{n}">'
                f'<c t="inlineStr"><is><t>2025-{(n % 12) + 1:02d}</t></is></c>'
                f'<c t="inlineStr"><is><t>{random.choice(BRANCHES)}</t></is></c>'
                f'<c t="inlineStr"><is><t>PRD{random.randint(1,300):04d}</t></is></c>'
                f'<c><v>{random.randint(1,500)}</v></c>'
                f'<c><v>{random.randint(1000,500000)}</v></c>'
                f'<c><v>{random.randint(10000,9000000)}</v></c>'
                f'<c t="inlineStr"><is><t>{random.choice(STATUS)}</t></is></c>'
                f'</row>')

    # target_bytes adalah ukuran .xlsx (ter-ZIP). Kalibrasi empiris: rasio ZIP ~6,7x,
    # ~150 byte/baris XML mentah -> baris = target * 6.7 / 150.
    est_rows = max(100, int(target_bytes * 6.7 / 150))
    est_rows = min(est_rows, 4_000_000)

    parts = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>']
    parts.append('<row r="1">' + ''.join(
        f'<c t="inlineStr"><is><t>{h}</t></is></c>'
        for h in ["bulan", "cabang", "produk", "unit", "harga", "total", "status"]) + '</row>')
    for n in range(2, est_rows + 2):
        parts.append(make_row(n))
    parts.append('</sheetData></worksheet>')
    sheet_xml = ''.join(parts)

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", root_rels)
        z.writestr("xl/workbook.xml", workbook)
        z.writestr("xl/_rels/workbook.xml.rels", wb_rels)
        z.writestr("xl/worksheets/sheet1.xml", sheet_xml)


def generate(out_dir, scale):
    os.makedirs(out_dir, exist_ok=True)
    idx = 2 if scale == "fast" else 1  # index 2 = fast, 1 = paper
    manifest = []

    def record(name, ftype, paper_bytes):
        p = os.path.join(out_dir, name)
        actual = os.path.getsize(p)
        manifest.append({
            "file": name, "type": ftype,
            "actual_bytes": actual,
            "paper_target_bytes": paper_bytes,
        })
        print(f"  [{ftype:4}] {name:20} {actual/1024/1024:8.2f} MB")

    print(f"Membangkitkan dataset (scale={scale}) ke: {out_dir}")
    print("CSV:")
    for name, paper_b, fast_b in CSV_SPEC:
        _write_csv(os.path.join(out_dir, name), fast_b if scale == "fast" else paper_b)
        record(name, "csv", paper_b)
    print("LOG/TXT:")
    for name, paper_b, fast_b in LOG_SPEC:
        _write_log(os.path.join(out_dir, name), fast_b if scale == "fast" else paper_b)
        record(name, "log", paper_b)
    print("JPG:")
    for i, kb in enumerate(JPG_SIZES_KB, 1):
        name = f"img_{i:02d}.jpg"
        _write_jpg(os.path.join(out_dir, name), kb * 1024)
        record(name, "jpg", kb * 1024)
    print("XLSX:")
    for name, paper_b, fast_b in XLSX_SPEC:
        _write_xlsx(os.path.join(out_dir, name), fast_b if scale == "fast" else paper_b)
        record(name, "xlsx", paper_b)

    total = len(manifest)
    total_mb = sum(m["actual_bytes"] for m in manifest) / 1024 / 1024
    with open(os.path.join(out_dir, "dataset_manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"scale": scale, "count": total, "files": manifest}, f, indent=2)
    print(f"\nSelesai: {total} berkas, total {total_mb:.1f} MB. Manifest disimpan.")
    assert total == 43, f"Jumlah berkas harus 43, tetapi {total}"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="./dataset_primer", help="Folder output dataset")
    ap.add_argument("--scale", choices=["fast", "full"], default="fast",
                    help="fast=Opsi Cepat (maks ~50MB), full=skala paper (sampai 1GB)")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    random.seed(args.seed)
    generate(args.out, args.scale)
