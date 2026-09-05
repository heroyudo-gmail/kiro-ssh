#!/usr/bin/env python3
"""
Pembangkit gambar paper Q1 dari hasil eksperimen NYATA (T3-T9).
Membaca file *.json di folder ini, menghasilkan PNG di figures/.

Semua angka bersumber dari eksekusi nyata di SageMaker (bukan ilustratif).
Jalankan: python make_figures.py
Butuh: matplotlib, numpy
"""
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({"font.size": 11, "figure.dpi": 150, "axes.grid": True,
                     "grid.alpha": 0.3, "savefig.bbox": "tight"})


def load(name):
    with open(os.path.join(HERE, name), "r") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Fig 1 — Generalization gap: in-domain vs cross-dataset (T3)
# ---------------------------------------------------------------------------
def fig_generalization_gap():
    d = load("cross_dataset_baseline.json")
    A = d["results"]["model_A"]
    labels = ["Same-CIC", "Same-UNSW", "CIC\u2192UNSW", "UNSW\u2192CIC"]
    mcc = [A["same_cic"]["mcc"], A["same_unsw"]["mcc"],
           A["cic2unsw"]["mcc"], A["unsw2cic"]["mcc"]]
    colors = ["#2a7", "#2a7", "#c33", "#c33"]

    fig, ax = plt.subplots(figsize=(7, 4.2))
    bars = ax.bar(labels, mcc, color=colors, edgecolor="black", linewidth=0.6)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("MCC")
    ax.set_title("In-domain vs Cross-dataset Detection (XGBoost, Model A)\n"
                 "Cross-network generalization collapses to ~0")
    ax.set_ylim(-0.15, 1.0)
    for b, v in zip(bars, mcc):
        ax.text(b.get_x() + b.get_width() / 2, v + (0.02 if v >= 0 else -0.06),
                f"{v:.3f}", ha="center", fontsize=10, fontweight="bold")
    fig.savefig(os.path.join(FIG, "fig1_generalization_gap.png"))
    plt.close(fig)
    print("  fig1_generalization_gap.png")


# ---------------------------------------------------------------------------
# Fig 2 — Few-shot target adaptation curve (T7)
# ---------------------------------------------------------------------------
def fig_fewshot_curve():
    d = load("domain_adaptation.json")
    fs = d["fewshot"]
    fr = [x["frac"] * 100 for x in fs["cic2unsw"]]
    c2u = [x["mcc"] for x in fs["cic2unsw"]]
    u2c = [x["mcc"] for x in fs["unsw2cic"]]
    mix = d["mixup"]

    fig, ax = plt.subplots(figsize=(7, 4.4))
    ax.plot(fr, c2u, "o-", color="#c33", linewidth=2, markersize=7, label="CIC\u2192UNSW")
    ax.plot(fr, u2c, "s-", color="#26a", linewidth=2, markersize=7, label="UNSW\u2192CIC")
    ax.axhline(mix["cic2unsw"]["mcc"], color="#c33", linestyle=":", alpha=0.7,
               label="CIC\u2192UNSW mixup (no target label)")
    ax.axhline(mix["unsw2cic"]["mcc"], color="#26a", linestyle=":", alpha=0.7,
               label="UNSW\u2192CIC mixup (no target label)")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Target labels used for calibration (%)")
    ax.set_ylabel("Cross-network MCC")
    ax.set_title("Few-shot Target Adaptation\n"
                 "1% target labels recover MCC from ~0 to 0.65\u20130.90")
    ax.legend(fontsize=9, loc="center right")
    ax.set_ylim(-0.15, 1.0)
    fig.savefig(os.path.join(FIG, "fig2_fewshot_curve.png"))
    plt.close(fig)
    print("  fig2_fewshot_curve.png")


# ---------------------------------------------------------------------------
# Fig 3 — Cross-network alignment: baseline vs CORAL vs joint (T6)
# ---------------------------------------------------------------------------
def fig_alignment():
    d = load("cross_network_alignment.json")
    base = d["results"]["baseline"]
    coral = d["results"]["coral"]
    joint = d["joint"]

    groups = ["CIC\u2192UNSW", "UNSW\u2192CIC"]
    base_v = [base["cic2unsw"]["mcc"], base["unsw2cic"]["mcc"]]
    coral_v = [coral["cic2unsw"]["mcc"], coral["unsw2cic"]["mcc"]]
    joint_v = [joint["unsw_test_mcc"], joint["cic_test_mcc"]]  # test target masing-masing

    x = np.arange(len(groups)); w = 0.26
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.bar(x - w, base_v, w, label="Baseline (single-source)", color="#c33", edgecolor="black", linewidth=0.5)
    ax.bar(x, coral_v, w, label="CORAL (unsup. DA)", color="#e90", edgecolor="black", linewidth=0.5)
    ax.bar(x + w, joint_v, w, label="Joint training (multi-source)", color="#2a7", edgecolor="black", linewidth=0.5)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x); ax.set_xticklabels(groups)
    ax.set_ylabel("MCC on target")
    ax.set_title("Cross-network Alignment Strategies\n"
                 "Joint training \u2248 in-domain; CORAL helps asymmetrically")
    ax.legend(fontsize=9)
    ax.set_ylim(-0.25, 1.0)
    fig.savefig(os.path.join(FIG, "fig3_alignment.png"))
    plt.close(fig)
    print("  fig3_alignment.png")


# ---------------------------------------------------------------------------
# Fig 4 — Functional vs unconstrained evasion (T8)
# ---------------------------------------------------------------------------
def fig_functional_evasion():
    d = load("functional_preserving_evasion.json")
    rows = d["summary_eps01"]
    labels = [r["model"] for r in rows]
    clean = [r["clean"] for r in rows]
    unc = [r["unconstrained"] for r in rows]
    fun = [r["functional"] for r in rows]

    x = np.arange(len(labels)); w = 0.26
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    ax.bar(x - w, clean, w, label="Clean", color="#2a7", edgecolor="black", linewidth=0.5)
    ax.bar(x, unc, w, label="Unconstrained FGSM", color="#c33", edgecolor="black", linewidth=0.5)
    ax.bar(x + w, fun, w, label="Functional-preserving", color="#e90", edgecolor="black", linewidth=0.5)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=15, ha="right")
    ax.set_ylabel("MCC (\u03b5=0.1)")
    ax.set_title("Functional-preserving vs Unconstrained Evasion\n"
                 "Unconstrained attacks overstate the threat")
    ax.legend(fontsize=9)
    ax.set_ylim(-0.3, 1.0)
    fig.savefig(os.path.join(FIG, "fig4_functional_evasion.png"))
    plt.close(fig)
    print("  fig4_functional_evasion.png")


# ---------------------------------------------------------------------------
# Fig 5 — Transfer vs adaptive white-box (T9)
# ---------------------------------------------------------------------------
def fig_adaptive_whitebox():
    d = load("adaptive_whitebox.json")
    rows = d["summary_eps01"]
    labels = [r["arah"].upper() for r in rows]
    clean = [r["robust_clean"] for r in rows]
    transfer = [r["robust_transfer"] for r in rows]
    adaptive = [r["robust_adaptive"] for r in rows]

    x = np.arange(len(labels)); w = 0.26
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.bar(x - w, clean, w, label="Robust / Clean", color="#2a7", edgecolor="black", linewidth=0.5)
    ax.bar(x, transfer, w, label="Robust / Transfer attack", color="#69c", edgecolor="black", linewidth=0.5)
    ax.bar(x + w, adaptive, w, label="Robust / Adaptive white-box", color="#c33", edgecolor="black", linewidth=0.5)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel("MCC (\u03b5=0.1)")
    ax.set_title("Adaptive White-box Evaluation\n"
                 "Defense strong vs transfer (0.99) but collapses vs adaptive (0.25\u20130.43)")
    ax.legend(fontsize=9)
    ax.set_ylim(-0.05, 1.05)
    fig.savefig(os.path.join(FIG, "fig5_adaptive_whitebox.png"))
    plt.close(fig)
    print("  fig5_adaptive_whitebox.png")


if __name__ == "__main__":
    print("Membangkitkan gambar paper Q1 dari hasil nyata:")
    fig_generalization_gap()
    fig_fewshot_curve()
    fig_alignment()
    fig_functional_evasion()
    fig_adaptive_whitebox()
    print(f"Selesai. Semua PNG di: {FIG}")
