#!/usr/bin/env python3
"""Figures for the FL-NIDS SURVEY paper (paper-survey.md).

English labels (reusable for the English version). Output: federated/figure-fed/*.png
Run locally:
  python make_survey_figures.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figure-fed")
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({"font.size": 10, "figure.dpi": 160, "savefig.bbox": "tight"})


def _box(ax, x, y, w, h, text, fc, ec="#333", fs=9, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                                linewidth=1.3, edgecolor=ec, facecolor=fc))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", color="#111")


def _arrow(ax, p0, p1, color="#333", style="-|>", lw=1.5, rad=0.0):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=13,
                                 lw=lw, color=color,
                                 connectionstyle=f"arc3,rad={rad}"))


def fig_architecture():
    """Core FL model: 1 aggregator + 2 clients exchanging weights (FedAvg)."""
    fig, ax = plt.subplots(figsize=(9.0, 5.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Aggregator - center top
    _box(ax, 3.7, 7.1, 2.6, 1.3, "Aggregator\nFedAvg\n(weighted by data size)",
         "#cfe8d6", ec="#2e8b57", fs=9, bold=True)

    # Client CIC - bottom left
    _box(ax, 0.5, 2.0, 3.0, 1.7,
         "Client-CIC\nCSE-CIC-IDS2018\nlocal training\n(local z-score)", "#d6e4f5",
         ec="#3a6ea5", fs=8.8, bold=True)
    # Client UNSW - bottom right
    _box(ax, 6.5, 2.0, 3.0, 1.7,
         "Client-UNSW\nUNSW-NB15\nlocal training\n(local z-score)", "#d6e4f5",
         ec="#3a6ea5", fs=8.8, bold=True)

    # aggregator -> client (send global model)
    _arrow(ax, (4.3, 7.1), (1.9, 3.7), color="#2e8b57", rad=0.18)
    _arrow(ax, (5.7, 7.1), (8.1, 3.7), color="#2e8b57", rad=-0.18)
    # client -> aggregator (send local update)
    _arrow(ax, (2.6, 3.7), (4.6, 7.1), color="#3a6ea5", rad=0.18)
    _arrow(ax, (7.4, 3.7), (5.4, 7.1), color="#3a6ea5", rad=-0.18)

    # edge labels
    ax.text(2.1, 5.6, "global\nmodel", fontsize=8, color="#2e8b57", ha="center")
    ax.text(3.75, 5.6, "local\nupdate", fontsize=8, color="#3a6ea5", ha="center")
    ax.text(7.9, 5.6, "global\nmodel", fontsize=8, color="#2e8b57", ha="center")
    ax.text(6.25, 5.6, "local\nupdate", fontsize=8, color="#3a6ea5", ha="center")

    fig.savefig(os.path.join(FIG, "fig_fl_architecture.png"))
    plt.close(fig)
    print("  figure-fed/fig_fl_architecture.png")


def fig_feature_alignment():
    """Only the 9-feature 1:1 intersection of the two extractors is used."""
    fig, ax = plt.subplots(figsize=(9.4, 5.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # left: CIC raw features
    _box(ax, 0.3, 6.1, 2.9, 2.9,
         "CSE-CIC-IDS2018\n(CICFlowMeter)\n~80 raw features\ne.g. Flow Duration,\nTot Fwd Pkts, flags ...",
         "#d6e4f5", ec="#3a6ea5", fs=8.3)
    # right: UNSW raw features
    _box(ax, 6.8, 6.1, 2.9, 2.9,
         "UNSW-NB15\n(Argus/Bro)\n42 raw features\ne.g. dur, spkts,\nsttl, ct_srv_src ...",
         "#d6e4f5", ec="#3a6ea5", fs=8.3)

    # center: 9 aligned features
    _box(ax, 3.5, 5.9, 3.0, 3.1,
         "9 aligned features\n(1:1 name mapping)\n\nduration, fwd_pkts,\nbwd_pkts, fwd_bytes,\nbwd_bytes, fwd_mean,\nbwd_mean, src_load,\ndst_load",
         "#cfe8d6", ec="#2e8b57", fs=8.2, bold=False)

    # arrows: raw -> aligned (keep only the intersection)
    _arrow(ax, (3.2, 7.4), (3.5, 7.4), color="#2e8b57")
    _arrow(ax, (6.8, 7.4), (6.5, 7.4), color="#2e8b57")

    # dropped note (below the shortened boxes, with clear gap)
    ax.text(1.75, 5.55, "extractor-specific\nfeatures dropped", fontsize=7.5,
            color="#b03030", ha="center", style="italic")
    ax.text(8.25, 5.55, "extractor-specific\nfeatures dropped", fontsize=7.5,
            color="#b03030", ha="center", style="italic")

    # bottom: feeds each client
    _box(ax, 0.6, 1.2, 3.4, 1.6,
         "Client-CIC\ntrains on its own rows,\nrestricted to the 9 features",
         "#eef4fb", ec="#3a6ea5", fs=8.3)
    _box(ax, 6.0, 1.2, 3.4, 1.6,
         "Client-UNSW\ntrains on its own rows,\nrestricted to the 9 features",
         "#eef4fb", ec="#3a6ea5", fs=8.3)
    _arrow(ax, (4.3, 5.9), (2.3, 2.8), color="#3a6ea5", rad=0.15)
    _arrow(ax, (5.7, 5.9), (7.7, 2.8), color="#3a6ea5", rad=-0.15)

    ax.text(5.0, 9.4,
            "Shared feature schema: only the 9 features present in BOTH extractors "
            "are kept; each client applies it to its own data.",
            ha="center", fontsize=8.2, color="#333")

    fig.savefig(os.path.join(FIG, "fig_feature_alignment.png"))
    plt.close(fig)
    print("  figure-fed/fig_feature_alignment.png")


def fig_results():
    """(a) R2: MCC vs Dirichlet alpha per domain; (b) R3: cross-dataset collapse.

    Values copied from the measured CSVs (survey_out/r2_noniid_sweep_{cic,unsw}.csv
    and survey_out/r3_crossdataset.csv); error bars are the std over 3 seeds.
    """
    import numpy as np

    alphas = [100, 10, 1, 0.5, 0.1, 0.05]
    cic_m = [0.5121, 0.5159, 0.5032, 0.5411, 0.3869, 0.3936]
    cic_s = [0.0040, 0.0059, 0.0233, 0.0126, 0.2737, 0.2792]
    unsw_m = [0.6205, 0.6241, 0.6448, 0.6384, 0.6552, 0.6477]
    unsw_s = [0.0117, 0.0078, 0.0126, 0.0289, 0.0136, 0.0300]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.4, 2.7),
                                   gridspec_kw={"width_ratios": [1, 1.2]})
    x = np.arange(len(alphas))
    ax1.errorbar(x, cic_m, yerr=cic_s, marker="o", capsize=3, lw=1.6,
                 color="#d1495b", label="Client-CIC")
    ax1.errorbar(x, unsw_m, yerr=unsw_s, marker="s", capsize=3, lw=1.6,
                 color="#3a6ea5", label="Client-UNSW")
    ax1.set_xticks(x)
    ax1.set_xticklabels([str(a) for a in alphas], fontsize=8)
    ax1.set_xlabel("Dirichlet concentration (high = IID, low = non-IID)", fontsize=8)
    ax1.set_ylabel("MCC", fontsize=8)
    ax1.set_ylim(0.0, 0.8)
    ax1.tick_params(labelsize=8)
    ax1.legend(fontsize=8, loc="lower left")
    ax1.set_title("(a) Non-IID impact per domain", fontsize=9)

    # (b) R3 on the union test set (values from survey_out/r3_crossdataset.csv, single run)
    labels = ["Central.\n(pooled)", "Central.\n(local norm)", "Local-only\n(CIC)",
              "Local-only\n(UNSW)", "Federated\n(local norm)", "Federated\n(pooled eval)"]
    vals = [0.5446, 0.6047, 0.2078, 0.0017, 0.6504, -0.0264]
    cols = ["#9a9a9a", "#6b6b6b", "#d1495b", "#3a6ea5", "#2e8b57", "#bfe3cb"]
    bars = ax2.bar(range(6), vals, color=cols, width=0.68)
    bars[5].set_hatch("//")
    bars[5].set_edgecolor("#2e8b57")
    ax2.axhline(0, color="#333", lw=0.8)
    for b, v in zip(bars, vals):
        ax2.text(b.get_x() + b.get_width() / 2, v + (0.03 if v >= 0 else -0.07),
                 f"{v:.2f}", ha="center", fontsize=7.5)
    ax2.set_xticks(range(6))
    ax2.set_xticklabels(labels, fontsize=6.3)
    ax2.set_ylabel("MCC (union test)", fontsize=8)
    ax2.set_ylim(-0.2, 0.8)
    ax2.tick_params(axis="y", labelsize=8)
    ax2.set_title("(b) Cross-dataset FL", fontsize=9)

    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig_results.png"))
    plt.close(fig)
    print("  figure-fed/fig_results.png")


if __name__ == "__main__":
    fig_feature_alignment()
    fig_architecture()
    fig_results()
