# make_fig_p2.py -- regenerate publication-ready Figure 2 & 3 for Paper 2.
# Clean English titles (NO "Paper 2" draft label), English legend/axis.
# Output: figure-p2/paper2_CIC_to_UNSW.png and figure-p2/paper2_UNSW_to_CIC.png
#
# Run:  python make_fig_p2.py
# Loads paper2_eval_results.json if available (searched in common dirs);
# otherwise uses embedded REAL numbers (identical to tab:p2main).

import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SEARCH = [".", "paper2_reviewer_out", os.path.join("..","paper2_reviewer_out"),
          "paper2_eval_out", "..", os.path.join("..","unswnb-15")]
OUTDIR_CANDIDATES = [os.path.join("..","figure-p2"), "figure-p2",
                     os.path.join("..","unswnb-15","figure-p2")]

def find(name):
    for d in SEARCH:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return None

def outdir():
    for d in OUTDIR_CANDIDATES:
        if os.path.isdir(d):
            return d
    os.makedirs("figure-p2", exist_ok=True)
    return "figure-p2"

# REAL fallback (paper2_eval_results.json, notebook 12) == tab:p2main
FALLBACK = {
    "CIC->UNSW": {  # variant: (clean_target, adaptive_pcfs_eps0.1)
        "baseline": (-0.074, 0.370), "few-shot": (0.650, 0.343),
        "adv": (-0.010, -0.440), "few-shot+adv": (0.696, 0.495)},
    "UNSW->CIC": {
        "baseline": (-0.060, -0.462), "few-shot": (0.897, -0.121),
        "adv": (-0.067, 0.002), "few-shot+adv": (0.897, -0.025)},
}

def load_points():
    p = find("paper2_eval_results.json")
    if not p:
        print("  (fallback) using embedded real numbers")
        return FALLBACK
    rows = json.load(open(p)).get("rows", [])
    if not rows:
        return FALLBACK
    out = {"CIC->UNSW": {}, "UNSW->CIC": {}}
    namemap = {"baseline":"baseline","fewshot":"few-shot","adv":"adv","fewshot_adv":"few-shot+adv"}
    for r in rows:
        d = r.get("arah") or r.get("direction")
        m = namemap.get(r.get("model"), r.get("model"))
        adv = r.get("adaptive_pcfs_eps0.1", r.get("adaptive_functional_eps0.1"))
        if d in out:
            out[d][m] = (r.get("clean_target"), adv)
    print("  loaded:", p)
    return out

ORDER = ["baseline", "few-shot", "adv", "few-shot+adv"]
BLUE, RED = "#4C72B0", "#C44E52"

def make_fig(direction, pts, fname, note=None):
    labels = ORDER
    gen = [pts[d][0] for d in labels]
    adv = [pts[d][1] for d in labels]
    x = np.arange(len(labels)); w = 0.38
    fig, ax = plt.subplots(figsize=(7, 4.0))
    ax.bar(x - w/2, gen, w, label="Clean (Cross-Network)", color=BLUE, edgecolor="k", linewidth=0.6)
    ax.bar(x + w/2, adv, w, label=r"Adaptive PCFS Evasion ($\epsilon=0.1$)", color=RED, edgecolor="k", linewidth=0.6)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel("MCC"); ax.set_ylim(-0.6, 1.0)
    ax.grid(axis="y", alpha=0.3)
    ax.set_title(f"{direction}: Generalization vs. Evasion Robustness")
    ax.legend(fontsize=9, framealpha=0.9)
    if note:
        ax.text(0.5, -0.22, note, transform=ax.transAxes, ha="center", va="top", fontsize=7.5, color="#444")
    fig.tight_layout()
    out = os.path.join(outdir(), fname)
    fig.savefig(out, dpi=200, bbox_inches="tight"); plt.close(fig)
    print("  wrote:", out)

def main():
    pts = load_points()
    make_fig("CIC $\\rightarrow$ UNSW".replace("$\\rightarrow$","->") if False else "CIC -> UNSW",
             pts["CIC->UNSW"], "paper2_CIC_to_UNSW.png")
    make_fig("UNSW -> CIC", pts["UNSW->CIC"], "paper2_UNSW_to_CIC.png")
    print("done.")

if __name__ == "__main__":
    main()
