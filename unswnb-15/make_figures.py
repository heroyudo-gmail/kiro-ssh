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
FIG = os.path.join(HERE, "figure-q1")
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
               label="CIC\u2192UNSW mixup (train-target labels)")
    ax.axhline(mix["unsw2cic"]["mcc"], color="#26a", linestyle=":", alpha=0.7,
               label="UNSW\u2192CIC mixup (train-target labels)")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Target labels used for calibration (%)")
    ax.set_ylabel("Cross-network MCC")
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


# ---------------------------------------------------------------------------
# Fig 6 — Deployment blueprint AWS (diagram arsitektur, bukan hasil eksperimen)
# ---------------------------------------------------------------------------
def fig_deployment_blueprint():
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

    fig, ax = plt.subplots(figsize=(10, 3.6))
    ax.set_xlim(0, 10); ax.set_ylim(0, 3.4); ax.axis("off")
    ax.grid(False)

    boxes = [
        (0.2, "Live traffic\n(VPC mirror /\nENI capture)", "#dde"),
        (2.15, "Capture sensor\nEC2 + NFStream\n(flow features)", "#cde"),
        (4.1, "Semantic Feature\nMapping (SFM)\n+ z-score", "#cec"),
        (6.05, "Robust XGBoost\n(9 features,\nedge-friendly)", "#fdb"),
        (8.0, "Detection +\nalerting\n(FAR logging)", "#fbb"),
    ]
    w, h, y = 1.75, 1.5, 1.0
    centers = []
    for x, label, color in boxes:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.08",
                             linewidth=1.1, edgecolor="black", facecolor=color)
        ax.add_patch(box)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=9)
        centers.append((x + w, x, y + h / 2))

    for i in range(len(centers) - 1):
        x_end = centers[i][0]
        x_start_next = centers[i + 1][1]
        yy = centers[i][2]
        arr = FancyArrowPatch((x_end, yy), (x_start_next, yy),
                              arrowstyle="-|>", mutation_scale=14, linewidth=1.2, color="black")
        ax.add_patch(arr)

    ax.text(5.0, 3.15, "Long-term Cloud Deployment (AWS) \u2014 continuous 3\u20137 days, measure False Alarm Rate",
            ha="center", va="center", fontsize=10, fontweight="bold")
    ax.text(5.0, 0.35,
            "Planned validation blueprint (future work): quantifies FAR under real daily traffic fluctuation.",
            ha="center", va="center", fontsize=8, style="italic", color="#444")
    fig.savefig(os.path.join(FIG, "fig6_deployment_blueprint.png"))
    plt.close(fig)
    print("  fig6_deployment_blueprint.png")


# ---------------------------------------------------------------------------
# Fig SFM — Semantic Feature Mapping as the intersection of the two schemas
# (concept diagram: CIC 68 features, UNSW 42 features, shared 9 SFM features)
# ---------------------------------------------------------------------------
def fig_shift_wasserstein():
    # Mean 1-Wasserstein distance (unit-corrected shared z-space) across 9 SFM features.
    # Real values from the three-domain shift analysis (notebooks/21_dataset_shift.ipynb).
    pairs = ["CIC vs UNSW", "CIC vs AWS", "UNSW vs AWS"]
    w1 = [0.317, 0.230, 0.372]
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    bars = ax.barh(pairs, w1, color="#4472c4", edgecolor="black", linewidth=0.5)
    ax.set_xlabel(r"Mean $W_1$ (shared z-space)")
    ax.set_xlim(0, 0.42)
    for b, v in zip(bars, w1):
        ax.text(v + 0.008, b.get_y() + b.get_height() / 2, f"{v:.2f}",
                va="center", fontsize=10)
    fig.savefig(os.path.join(FIG, "fig_shift_wasserstein.png"))
    plt.close(fig)
    print("  fig_shift_wasserstein.png")


def fig_aws_fewshot_curve():
    # Few-shot calibration on the live AWS testbed (stratified flow-level split).
    # Real values from the AWS few-shot table.
    frac = [0, 1, 5, 10, 20, 50]
    uns = [0.074, 0.490, 0.479, 0.588, 0.596, 0.574]
    cic = [-0.217, 0.132, 0.370, 0.207, 0.456, 0.136]
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.plot(frac, uns, "o-", color="#e8842a", linewidth=2, markersize=7, label="UNSW + AWS")
    ax.plot(frac, cic, "s-", color="#3a6ab0", linewidth=2, markersize=7, label="CIC + AWS")
    ax.axhline(0.598, color="#2a8", linestyle="--", linewidth=1.5, label="AWS-only = 0.598")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("AWS labels used for calibration (%)")
    ax.set_ylabel("MCC on AWS test")
    ax.set_ylim(-0.3, 1.0)
    ax.legend(fontsize=9, loc="upper right")
    fig.savefig(os.path.join(FIG, "aws_fewshot_curve.png"))
    plt.close(fig)
    print("  aws_fewshot_curve.png")


def fig_sfm_intersection():
    from matplotlib.patches import Circle

    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.set_aspect("equal")
    ax.axis("off"); ax.grid(False)

    # two overlapping circles (radius sized to fit within ylim with margin)
    cic = Circle((4.1, 2.5), 2.2, facecolor="#cde", edgecolor="#26a",
                 linewidth=1.6, alpha=0.55)
    unsw = Circle((5.9, 2.5), 2.2, facecolor="#fdb", edgecolor="#e90",
                  linewidth=1.6, alpha=0.55)
    ax.add_patch(cic); ax.add_patch(unsw)

    # dataset names inside the non-overlapping part of each circle
    ax.text(2.9, 2.65, "CSE-CIC-\nIDS2018", ha="center", va="center",
            fontsize=10.5, fontweight="bold", color="#26a")
    ax.text(2.9, 1.95, "68 features", ha="center", va="center",
            fontsize=9, color="#26a")
    ax.text(7.1, 2.65, "UNSW-\nNB15", ha="center", va="center",
            fontsize=10.5, fontweight="bold", color="#b70")
    ax.text(7.1, 1.95, "42 features", ha="center", va="center",
            fontsize=9, color="#b70")

    # intersection = SFM with 9 features
    ax.text(5.0, 2.75, "SFM", ha="center", va="center",
            fontsize=12.5, fontweight="bold", color="#060")
    ax.text(5.0, 2.15, "9 features", ha="center", va="center",
            fontsize=9.5, color="#060")

    fig.savefig(os.path.join(FIG, "fig_sfm_intersection.png"))
    plt.close(fig)
    print("  fig_sfm_intersection.png")


if __name__ == "__main__":
    print("Membangkitkan gambar paper Q1 dari hasil nyata:")
    fig_generalization_gap()
    fig_fewshot_curve()
    fig_alignment()
    fig_functional_evasion()
    fig_adaptive_whitebox()
    fig_deployment_blueprint()
    fig_sfm_intersection()
    fig_shift_wasserstein()
    fig_aws_fewshot_curve()
    print(f"Selesai. Semua PNG di: {FIG}")


# ---------------------------------------------------------------------------
# Paper 2 — decision-cell schematic (why PCFS evasion is direction-dependent)
# Conceptual 2D sketch; mechanism is quantified empirically in the paper.
# ---------------------------------------------------------------------------
def fig_p2_treeboundary():
    import numpy as np
    from matplotlib.patches import FancyArrowPatch

    FIG_P2 = os.path.join(HERE, "figure-p2")
    os.makedirs(FIG_P2, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.2))
    benign_c = "#2b7bba"
    attack_c = "#d1495b"

    # Same perturbation budget dx in both panels; only the cell width differs.
    # (a) wide cells: the attack sits deep inside a wide attack cell, so the same
    #     shift does NOT reach the boundary -> still detected.
    # (b) thin cells: the boundary is close, so the same shift crosses -> evades.
    dx = 1.4
    for ax, (title, splits, start_off) in zip(
        axes,
        [("(a) high-variance target (UNSW): wide cells",
          [2.2, 4.4, 6.6, 8.8], 1.9),
         ("(b) low-variance target (CIC): thin cells",
          [3.6, 4.1, 4.6, 5.1, 5.6, 6.1], 0.4)],
    ):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
        # staircase decision boundary (axis-parallel splits)
        for s in splits:
            ax.axvline(s, color="#888", lw=1.0, ls="--")
        # benign region (left) and attack region (right) shaded lightly
        ax.axvspan(0, splits[len(splits)//2], color=benign_c, alpha=0.08)
        ax.axvspan(splits[len(splits)//2], 10, color=attack_c, alpha=0.08)
        boundary = splits[len(splits)//2]
        # attack flow start inside the attack cell (farther in for wide cells)
        x0 = boundary + start_off
        ax.scatter([x0], [5], s=90, color=attack_c, zorder=5, edgecolor="k", lw=0.6)
        ax.annotate("attack flow", (x0, 5), textcoords="offset points",
                    xytext=(6, 12), fontsize=9, color=attack_c)
        # same valid epsilon shift (add-only) to the left
        ax.add_patch(FancyArrowPatch((x0, 5), (x0 - dx, 5),
                                     arrowstyle="-|>", mutation_scale=14,
                                     color="#333", lw=1.6, zorder=6))
        landed = x0 - dx
        if landed < boundary:
            ax.scatter([landed], [5], s=90, color=benign_c, zorder=5,
                       edgecolor="k", lw=0.6)
            ax.text(landed, 3.3, "evades\n(crosses boundary)", ha="center",
                    fontsize=8.5, color=benign_c)
        else:
            ax.scatter([landed], [5], s=90, color=attack_c, zorder=5,
                       edgecolor="k", lw=0.6)
            ax.text(landed, 3.3, "still detected\n(stays in cell)", ha="center",
                    fontsize=8.5, color=attack_c)
        ax.text(0.5, 9.3, "benign", fontsize=9, color=benign_c, fontweight="bold")
        ax.text(9.5, 9.3, "attack", fontsize=9, color=attack_c,
                fontweight="bold", ha="right")
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("feature axis (e.g. bytes / load)", fontsize=9)

    fig.tight_layout()
    fig.savefig(os.path.join(FIG_P2, "paper2_treeboundary.png"))
    plt.close(fig)
    print("  figure-p2/paper2_treeboundary.png")
