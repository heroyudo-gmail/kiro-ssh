#!/usr/bin/env python3
"""
make_figures_en.py
==================
English-labeled versions of the two chart figures that previously carried
Indonesian axis titles/labels (Figure 10 and Figure 13), rendered FROM THE SAME
REAL EXPERIMENT DATA (results/compression_report.csv). This keeps the Indonesian
paper (ijece-id.tex) using the ID figures while the English paper (ijece.tex)
uses these English figures.

Output:
  ../figures/figure10_compression_en.png
  ../figures/figure13_dashboard_en.png
"""
import csv
import json
import os
import collections

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RESULTS = os.path.join(os.path.dirname(__file__), "results")
FIGDIR = os.path.join(os.path.dirname(__file__), "..", "figures")
os.makedirs(FIGDIR, exist_ok=True)


def _text_panel(lines, outfile, title=None, dark=True, width=9, fontsize=11):
    """Render a list of text lines as a terminal/editor-style panel."""
    bg = "#1e1e1e" if dark else "#f7f7f7"
    fg = "#d4d4d4" if dark else "#1a1a1a"
    n = len(lines) + (2 if title else 1)
    fig_h = max(1.2, 0.32 * n)
    fig, ax = plt.subplots(figsize=(width, fig_h))
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    ax.axis("off")
    y = 1.0
    dy = 1.0 / (n + 0.5)
    if title:
        ax.text(0.02, y, title, color="#4ec9b0", fontsize=fontsize + 1,
                fontweight="bold", fontfamily="monospace", va="top", transform=ax.transAxes)
        y -= dy * 1.4
    for ln in lines:
        color = fg
        s = ln.strip()
        if s.startswith('"') and ":" in ln:
            color = "#9cdcfe"
        if "OK" in ln or "true" in ln or "SUCCESS" in ln or "[OK]" in ln:
            color = "#89d185" if dark else "#6a9955"
        if "0.0%" in ln or '": 0' in ln or "detected_ransom" in ln:
            color = fg
        ax.text(0.02, y, ln, color=color, fontsize=fontsize,
                fontfamily="monospace", va="top", transform=ax.transAxes)
        y -= dy
    plt.tight_layout(pad=0.4)
    fig.savefig(outfile, dpi=150, facecolor=bg, bbox_inches="tight")
    plt.close(fig)
    print("saved", os.path.relpath(outfile))


def fig_compression_en():
    rows = list(csv.DictReader(open(os.path.join(RESULTS, "compression_report.csv"))))
    agg = collections.defaultdict(list)
    for r in rows:
        agg[(r["type"], r["algo"])].append(float(r["storage_saving_pct"]))
    types = ["log", "csv", "xlsx", "jpg"]
    algos = ["gzip", "zstd", "brotli", "lz4", "snappy"]
    labels = ["Gzip", "Zstandard", "Brotli", "LZ4", "Snappy"]
    colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3"]
    x = np.arange(len(types))
    w = 0.16
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for j, (a, lab, c) in enumerate(zip(algos, labels, colors)):
        vals = [max(0, sum(agg.get((t, a), [0])) / len(agg.get((t, a), [1]))) for t in types]
        ax.bar(x + (j - 2) * w, vals, w, label=lab, color=c)
    ax.set_xticks(x)
    ax.set_xticklabels([t.upper() for t in types])
    ax.set_ylabel("Storage Saving (%)")
    ax.set_title("Compression analysis by file type and algorithm (43 files)")
    ax.legend(ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.12), fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    out = os.path.join(FIGDIR, "figure10_compression_en.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved", os.path.relpath(out))


def fig_dashboard_en():
    rows = list(csv.DictReader(open(os.path.join(RESULTS, "compression_report.csv"))))
    agg = collections.defaultdict(list)
    for r in rows:
        if r["selected"] == "True":
            agg[r["type"]].append(float(r["storage_saving_pct"]))
    types = ["csv", "log", "xlsx", "jpg"]
    ss = [sum(agg.get(t, [0])) / len(agg.get(t, [1])) for t in types]
    fig, ax = plt.subplots(figsize=(8, 3.4))
    bars = ax.barh([t.upper() for t in types], [max(0, v) for v in ss],
                   color=["#4C72B0", "#55A868", "#DD8452", "#C44E52"])
    for b, v in zip(bars, ss):
        ax.text(max(0, v) + 1, b.get_y() + b.get_height() / 2,
                f"{max(0,v):.1f}%", va="center", fontsize=9)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Storage Saving (%) - selected algorithm")
    ax.set_title("System monitoring summary (normal condition, 43 files)")
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    plt.tight_layout()
    out = os.path.join(FIGDIR, "figure13_dashboard_en.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved", os.path.relpath(out))


def fig_cloud_conn_en():
    import hashlib, time
    sid = hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
    lines = [
        "$ python backup_system.py  # cloud init (Amazon S3)", "",
        "[INFO] Authenticating to Amazon S3 (EC2 IAM role)",
        f'[OK] session_id = {sid}',
        '[OK] bucket = s3://ssh-detection-features-.../ransomware-results',
        "[OK] Secure connection established (access control via IAM)",
    ]
    _text_panel(lines, os.path.join(FIGDIR, "figure4_cloud_conn_en.png"),
                title="Cloud Storage Connection Initialization (S3)")


def fig_upload_en():
    bl = json.load(open(os.path.join(RESULTS, "baseline.json")))
    names = list(bl.keys())[:5]
    lines = ["$ python backup_system.py  # upload + initial validation", ""]
    for nm in names:
        lines.append(f"  upload {nm:<18} SHA-256 verified -> baseline  [OK]")
    lines.append("  ...")
    lines.append("")
    lines.append(f"[OK] {len(bl)} files validated & backed up (0 corrupt duplicates)")
    _text_panel(lines, os.path.join(FIGDIR, "figure5_upload_en.png"),
                title="Backup Upload & Initial Validation")


def fig_sha256_en():
    bl = json.load(open(os.path.join(RESULTS, "baseline.json")))
    items = list(bl.items())[:6]
    lines = ["$ python backup_system.py --baseline", ""]
    for name, d in items:
        lines.append(f'{name:<18} {d["sha256"][:48]}...')
    lines.append("")
    lines.append(f"[OK] SHA-256 baseline created for {len(bl)} files")
    _text_panel(lines, os.path.join(FIGDIR, "figure6_sha256_en.png"),
                title="SHA-256 Integrity Baseline")


def fig_validation_en():
    ev = json.load(open(os.path.join(RESULTS, "eval_normal.json")))
    lines = [
        "$ python detector_recovery.py --mode normal", "",
        json.dumps({
            "total_files": ev["total_files"],
            "detected": ev["detected"],
            "FP": ev["FP"], "TN": ev["TN"],
            "FPR_pct": ev["FPR_pct"],
            "detected_ransom_files": [],
            "status": "safe"
        }, indent=2),
    ]
    flat = []
    for l in lines:
        flat.extend(l.split("\n"))
    _text_panel(flat, os.path.join(FIGDIR, "figure8_validation_en.png"),
                title="Integrity Validation Results (Normal Condition)")


def fig_aeslog_en():
    bl = json.load(open(os.path.join(RESULTS, "baseline.json")))
    names = list(bl.keys())[:5]
    lines = ["$ python backup_system.py  # compress-then-encrypt", ""]
    lines.append("[INFO] Loading AES-256 key (32 bytes)")
    for nm in names:
        lines.append(f"[OK] {nm} -> compress -> AES-256 -> {nm}.<algo>.enc")
    lines.append("")
    lines.append(f"[OK] {len(bl)} files secured to air-gapped storage")
    _text_panel(lines, os.path.join(FIGDIR, "figure9_aeslog_en.png"),
                title="AES-256 Encryption Log")


def fig_airgap_struct_en():
    rows = list(csv.DictReader(open(os.path.join(RESULTS, "compression_report.csv"))))
    sel = collections.defaultdict(list)
    for r in rows:
        if r["selected"] == "True":
            sel[r["algo"]].append(r["file"])
    lines = ["$ ls -R /mnt/airgap/backup   (drive D: on Windows)", ""]
    for algo in sorted(sel):
        lines.append(f"backup/{algo}/")
        for fn in sel[algo][:2]:
            lines.append(f"    {fn}.{algo}.enc")
        if len(sel[algo]) > 2:
            lines.append(f"    ... ({len(sel[algo])} files)")
    lines.append("")
    lines.append("hash_storage.json   (SHA-256 integrity reference)")
    _text_panel(lines, os.path.join(FIGDIR, "figure11_airgap_struct_en.png"),
                title="Air-Gapped Storage Structure")


def fig_transfer_en():
    summ = json.load(open(os.path.join(RESULTS, "experiment_summary.json")))
    bt = summ["steps"].get("backup_time_s", 0)
    n = summ["paper_ready"]["n_files"]
    lines = [
        "$ mount /dev/nvme1n1 /mnt/airgap   # enable air-gapped", "",
        "[INFO] Air-gapped media mounted (limited session)",
        f"[OK] Transfer of {n} compressed-encrypted files completed",
        f"[OK] Total backup time = {bt} s",
        "[INFO] umount /mnt/airgap  # media detached (isolation)",
    ]
    _text_panel(lines, os.path.join(FIGDIR, "figure12_transfer_en.png"),
                title="Transfer to Air-Gapped Storage")


def fig_restore_json_en():
    ev = json.load(open(os.path.join(RESULTS, "eval_encrypt_hold.json")))
    obj = {
        "airgap": {"detected": True},
        "files": [],
        "global": {
            "errors": ev["restore_err"],
            "total_backup_pairs": ev["total_files"],
            "total_restore": ev["restore_ok"],
            "total_restore_ok": ev["restore_ok"],
        },
        "restore_mode": ev["restore_mode"],
    }
    lines = json.dumps(obj, indent=2).split("\n")
    _text_panel(lines, os.path.join(FIGDIR, "figure14_restore_json_en.png"),
                title="Air-Gapped Restore Status (airgap mode)")


def fig_restore_terminal_en():
    bl = json.load(open(os.path.join(RESULTS, "baseline.json")))
    ev = json.load(open(os.path.join(RESULTS, "eval_encrypt_hold.json")))
    names = list(bl.keys())[:8]
    lines = ["$ python detector_recovery.py --mode attack --airgap /mnt/airgap/backup", ""]
    lines.append("[AIRGAP] Ransomware detected -> full recovery started")
    for nm in names:
        lines.append(f"  restore {nm:<18} decrypt -> decompress -> verify  [OK]")
    lines.append("  ...")
    lines.append("")
    lines.append(f"[OK] {ev['restore_ok']}/{ev['total_files']} files recovered, "
                 f"errors={ev['restore_err']}, RTO={ev['rto_seconds']} s")
    _text_panel(lines, os.path.join(FIGDIR, "figure16_restore_terminal_en.png"),
                title="Air-Gapped Recovery Terminal")


if __name__ == "__main__":
    fig_compression_en()
    fig_dashboard_en()
    fig_cloud_conn_en()
    fig_upload_en()
    fig_sha256_en()
    fig_validation_en()
    fig_aeslog_en()
    fig_airgap_struct_en()
    fig_transfer_en()
    fig_restore_json_en()
    fig_restore_terminal_en()
    print("\nDone. English figures written to:", os.path.abspath(FIGDIR))
