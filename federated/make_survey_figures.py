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


if __name__ == "__main__":
    fig_architecture()
