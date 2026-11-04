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
    """Testbed architecture: 1 aggregator + 2 clients, weights via S3, SSM access."""
    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # VPC boundary
    ax.add_patch(FancyBboxPatch((0.3, 0.9), 9.4, 8.0,
                                boxstyle="round,pad=0.02,rounding_size=0.1",
                                linewidth=1.2, edgecolor="#8aa", facecolor="#f4f8fa",
                                linestyle="--"))
    ax.text(0.55, 8.6, "AWS VPC  10.7.0.0/16  (region ap-southeast-1)",
            fontsize=8.5, color="#577", style="italic")

    # S3 (weight exchange hub) - center top
    _box(ax, 3.9, 6.8, 2.2, 1.1, "Amazon S3\nglobal / client weights\n(.npz per round)",
         "#ffe9c7", ec="#c8922e", fs=8.5, bold=True)

    # Aggregator - center
    _box(ax, 3.9, 4.0, 2.2, 1.2, "Aggregator (EC2)\nFedAvg\nt3.medium", "#cfe8d6",
         ec="#2e8b57", fs=9, bold=True)

    # Client CIC - left
    _box(ax, 0.8, 1.5, 2.4, 1.5,
         "Client-CIC (EC2)\nCSE-CIC-IDS2018\nlocal train + local z-score", "#d6e4f5",
         ec="#3a6ea5", fs=8.5, bold=True)
    # Client UNSW - right
    _box(ax, 6.8, 1.5, 2.4, 1.5,
         "Client-UNSW (EC2)\nUNSW-NB15\nlocal train + local z-score", "#d6e4f5",
         ec="#3a6ea5", fs=8.5, bold=True)

    # arrows: clients -> S3 (upload updates) and S3 -> clients (download global)
    _arrow(ax, (2.0, 3.0), (4.2, 6.8), color="#3a6ea5", rad=0.15)
    _arrow(ax, (8.0, 3.0), (5.8, 6.8), color="#3a6ea5", rad=-0.15)
    _arrow(ax, (4.4, 6.8), (2.1, 3.05), color="#c8922e", rad=0.30)
    _arrow(ax, (5.6, 6.8), (7.9, 3.05), color="#c8922e", rad=-0.30)

    # aggregator <-> S3
    _arrow(ax, (5.1, 5.2), (5.1, 6.8), color="#2e8b57")
    _arrow(ax, (4.5, 6.8), (4.5, 5.2), color="#2e8b57")

    # labels
    ax.text(2.45, 5.0, "upload\nlocal update", fontsize=7.5, color="#3a6ea5", ha="center")
    ax.text(7.55, 5.0, "upload\nlocal update", fontsize=7.5, color="#3a6ea5", ha="center")
    ax.text(6.15, 6.0, "publish global /\npull updates", fontsize=7.5,
            color="#2e8b57", ha="left")

    # operator via SSM (no public inbound)
    _box(ax, 0.8, 7.1, 2.2, 0.9, "Operator\n(AWS SSM, no SSH)", "#eeeeee", ec="#777", fs=8)
    _arrow(ax, (3.0, 7.55), (3.9, 7.35), color="#777")
    _arrow(ax, (3.0, 7.2), (3.9, 4.9), color="#777", rad=-0.2)

    ax.text(5.0, 0.3,
            "Per round t: aggregator publishes global weights to S3; each client "
            "downloads them, trains locally, and uploads its update;\naggregator "
            "aggregates with FedAvg (weighted by data size), then starts the next "
            "round. No direct socket between nodes; 100 rounds total.",
            ha="center", va="bottom", fontsize=7.6, color="#444")

    fig.savefig(os.path.join(FIG, "fig_fl_architecture.png"))
    plt.close(fig)
    print("  figure-fed/fig_fl_architecture.png")


if __name__ == "__main__":
    fig_architecture()
