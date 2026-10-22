#!/usr/bin/env python3
"""
make_nids_eval_figures_bilingual.py
===================================
Regenerate the NIDS evaluation figures (confusion 2x2, radar, grouped bar)
in TWO languages: Indonesian (id) and English (en), from the REAL trained
models and data. Intended to be run in the same environment as Notebook 08
(e.g., SageMaker), where the .pkl results and model artifacts exist.

Output:
  ../data/id/<name>_id.png   (Indonesian labels)
  ../data/en/<name>_en.png   (English labels)

Numbers are NOT hardcoded: the script loads the actual models and recomputes
S1-S4 exactly as Notebook 08 does, so both language versions share identical
real values -- only the labels differ.
"""
import os
import pickle
import time
import warnings
import subprocess
import sys
import importlib


def _ensure(pkg, import_name=None):
    """Ensure a package is importable; pip-install it if missing.
    SageMaker resets pip packages on instance stop/start, so we self-heal here.
    """
    name = import_name or pkg
    try:
        importlib.import_module(name)
    except ImportError:
        print(f"[setup] Installing missing package: {pkg} ...", flush=True)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pkg])


for _pkg, _imp in [("numpy", "numpy"), ("matplotlib", "matplotlib"),
                   ("scikit-learn", "sklearn"), ("xgboost", "xgboost")]:
    _ensure(_pkg, _imp)

import numpy as np
import matplotlib
matplotlib.use("Agg")  # no display needed on SageMaker terminal
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, matthews_corrcoef, confusion_matrix,
)
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")
for _style in ("seaborn-v0_8-whitegrid", "seaborn-whitegrid", "ggplot", "default"):
    try:
        plt.style.use(_style)
        break
    except (OSError, ValueError):
        continue
plt.rcParams.update({"font.size": 10, "figure.dpi": 150, "axes.grid": True})

DATA_DIR = "../data/"
MODEL_DIR = "../models/"
RANDOM_SEED = 42
TEST_SIZE = 0.20
EPSILON = 0.1

OUT = {"id": os.path.join(DATA_DIR, "id"), "en": os.path.join(DATA_DIR, "en")}
for d in OUT.values():
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------------------
# Bilingual label dictionary
# ---------------------------------------------------------------------------
T = {
    "id": {
        "predicted": "Prediksi", "actual": "Aktual",
        "confusion_suptitle": "Confusion Matrix \u2014 Skenario Evaluasi 2\u00d72\n(XGBoost Top-10, \u03b5={eps})",
        "s1": "S1: Baseline + Bersih", "s2": "S2: Baseline + Adversarial",
        "s3": "S3: Robust + Bersih", "s4": "S4: Robust + Adversarial",
        "radar_title": "Radar Multi-Metrik: Skenario 2\u00d72\n(XGBoost Top-10)",
        "radar_labels": {"S1": "Baseline+Bersih", "S2": "Baseline+Adv",
                          "S3": "Robust+Bersih", "S4": "Robust+Adv"},
        "bar_title": "Evaluasi Komprehensif: Skenario 2\u00d72\n(XGBoost Top-10, CSE-CIC-IDS2018, \u03b5={eps})",
        "bar_xlabel": "Metrik", "bar_ylabel": "Skor",
        "categories": ["MCC", "F1-Score", "Presisi", "Recall", "Akurasi"],
        "bar_metrics": ["MCC", "F1-Score", "Presisi", "Recall"],
    },
    "en": {
        "predicted": "Predicted", "actual": "Actual",
        "confusion_suptitle": "Confusion Matrices \u2014 2\u00d72 Evaluation Scenarios\n(XGBoost Top-10, \u03b5={eps})",
        "s1": "S1: Baseline + Clean", "s2": "S2: Baseline + Adversarial",
        "s3": "S3: Robust + Clean", "s4": "S4: Robust + Adversarial",
        "radar_title": "Multi-Metric Radar: 2\u00d72 Scenarios\n(XGBoost Top-10)",
        "radar_labels": {"S1": "Baseline+Clean", "S2": "Baseline+Adv",
                         "S3": "Robust+Clean", "S4": "Robust+Adv"},
        "bar_title": "Comprehensive Evaluation: 2\u00d72 Scenarios\n(XGBoost Top-10, CSE-CIC-IDS2018, \u03b5={eps})",
        "bar_xlabel": "Metric", "bar_ylabel": "Score",
        "categories": ["MCC", "F1-Score", "Precision", "Recall", "Accuracy"],
        "bar_metrics": ["MCC", "F1-Score", "Precision", "Recall"],
    },
}


def draw_heatmap(ax, matrix, xlabels, ylabels, cmap, title, xlab, ylab):
    """Normalized confusion-matrix heatmap using pure matplotlib (no seaborn)."""
    im = ax.imshow(matrix, cmap=cmap, vmin=0.0, vmax=1.0, aspect="auto")
    ax.figure.colorbar(im, ax=ax, shrink=0.8)
    ax.set_xticks(np.arange(len(xlabels)))
    ax.set_yticks(np.arange(len(ylabels)))
    ax.set_xticklabels(xlabels, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(ylabels, fontsize=8)
    thresh = 0.5
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = matrix[i, j]
            ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                    color="white" if val > thresh else "black", fontsize=7)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)


def compute_saliency(model, X, y, h=0.01):
    n_samples, n_features = X.shape
    saliency = np.zeros((n_samples, n_features))
    for i in range(n_features):
        X_plus = X.copy(); X_plus[:, i] += h
        X_minus = X.copy(); X_minus[:, i] -= h
        eps_c = 1e-15
        p_plus = model.predict_proba(X_plus)
        p_minus = model.predict_proba(X_minus)
        loss_plus = -np.log(np.clip(p_plus[np.arange(n_samples), y.astype(int)], eps_c, 1.0))
        loss_minus = -np.log(np.clip(p_minus[np.arange(n_samples), y.astype(int)], eps_c, 1.0))
        saliency[:, i] = (loss_plus - loss_minus) / (2 * h)
    return saliency


def full_eval(model, X, y):
    y_pred = model.predict(X)
    return {
        "y_pred": y_pred,
        "mcc": matthews_corrcoef(y, y_pred),
        "f1": f1_score(y, y_pred, average="weighted", zero_division=0),
        "precision": precision_score(y, y_pred, average="weighted", zero_division=0),
        "recall": recall_score(y, y_pred, average="weighted", zero_division=0),
        "accuracy": accuracy_score(y, y_pred),
        "cm": confusion_matrix(y, y_pred),
    }


def load_everything():
    print("[1/5] Loading experiment_results_03.pkl ...", flush=True)
    with open(os.path.join(DATA_DIR, "experiment_results_03.pkl"), "rb") as f:
        exp = pickle.load(f)
    top10 = exp["top10_features"]
    names = exp["feature_names"]
    label_mapping = exp["label_mapping"]
    inv = {v: k for k, v in label_mapping.items()}

    print("[2/5] Loading cleaned_100.pkl (may take a while) ...", flush=True)
    with open(os.path.join(DATA_DIR, "cleaned_100.pkl"), "rb") as f:
        data = pickle.load(f)
    X_all, y_all = data["X"], data["y"]
    print(f"      dataset loaded: X={getattr(X_all, 'shape', '?')}", flush=True)
    idx = [names.index(f) for f in top10 if f in names]
    X_top10 = X_all[:, idx]
    X_train, X_test, y_train, y_test = train_test_split(
        X_top10, y_all, test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=y_all
    )
    y_train = y_train if isinstance(y_train, np.ndarray) else y_train.values
    y_test = y_test if isinstance(y_test, np.ndarray) else y_test.values
    n_classes = len(np.unique(y_all))

    deploy = os.path.join(MODEL_DIR, "deploy")
    files = os.listdir(deploy) if os.path.exists(deploy) else []
    base_file = [f for f in files if "xgboost" in f and "top-10" in f and f.endswith(".json")]
    base = XGBClassifier()
    if base_file:
        print(f"[3/5] Loading baseline model: {base_file[0]}", flush=True)
        base.load_model(os.path.join(deploy, base_file[0]))
    else:
        print("[3/5] Baseline model not found -> retraining (this is slow) ...", flush=True)
        base = XGBClassifier(n_estimators=200, max_depth=8, learning_rate=0.1,
                             subsample=0.8, colsample_bytree=0.8,
                             objective="multi:softprob", num_class=n_classes,
                             eval_metric="mlogloss", random_state=RANDOM_SEED,
                             n_jobs=-1, tree_method="hist")
        base.fit(X_train, y_train)
    print("[4/5] Loading robust model: robust_xgboost_top10.json", flush=True)
    robust = XGBClassifier()
    robust.load_model(os.path.join(MODEL_DIR, "robust_xgboost_top10.json"))
    print("[5/5] Models ready.", flush=True)
    return top10, inv, X_test, y_test, base, robust


def main():
    import sys
    max_n = int(sys.argv[1]) if len(sys.argv) > 1 else 50000
    top10, inv, X_test, y_test, base, robust = load_everything()
    N = min(max_n, len(X_test))
    X_eval, y_eval = X_test[:N], y_test[:N]
    print(f"Computing saliency on {N:,} samples (10 features x 2 x predict_proba)...", flush=True)
    t0 = time.time()
    sal = compute_saliency(base, X_eval, y_eval)
    print(f"  saliency done in {time.time()-t0:.1f}s", flush=True)
    X_adv = X_eval + EPSILON * np.sign(sal)

    print("Evaluating scenarios S1-S4 ...", flush=True)
    S = {"S1": full_eval(base, X_eval, y_eval),
         "S2": full_eval(base, X_adv, y_eval),
         "S3": full_eval(robust, X_eval, y_eval),
         "S4": full_eval(robust, X_adv, y_eval)}
    print(f"  MCC: S1={S['S1']['mcc']:.4f} S2={S['S2']['mcc']:.4f} "
          f"S3={S['S3']['mcc']:.4f} S4={S['S4']['mcc']:.4f}", flush=True)
    class_names = [inv.get(int(c), f"C{c}") for c in sorted(np.unique(y_eval))]

    for lang in ("id", "en"):
        t = T[lang]
        # --- Confusion 2x2 ---
        fig, axes = plt.subplots(2, 2, figsize=(16, 14))
        titles = [f'{t["s1"]}\nMCC={S["S1"]["mcc"]:.4f}',
                  f'{t["s2"]}\nMCC={S["S2"]["mcc"]:.4f}',
                  f'{t["s3"]}\nMCC={S["S3"]["mcc"]:.4f}',
                  f'{t["s4"]}\nMCC={S["S4"]["mcc"]:.4f}']
        cmaps = ["Blues", "Reds", "Greens", "Oranges"]
        for ax, title, cmap, key in zip(axes.flat, titles, cmaps, ["S1", "S2", "S3", "S4"]):
            cm = S[key]["cm"].astype(float)
            cmn = cm / cm.sum(axis=1)[:, None]
            draw_heatmap(ax, cmn, class_names, class_names, cmap, title,
                         t["predicted"], t["actual"])
        plt.suptitle(t["confusion_suptitle"].format(eps=EPSILON), fontsize=14, fontweight="bold", y=1.01)
        plt.tight_layout()
        plt.savefig(os.path.join(OUT[lang], f"evaluation_confusion_2x2_{lang}.png"), bbox_inches="tight", dpi=150)
        plt.close(fig)

        # --- Radar ---
        cats = t["categories"]; n = len(cats)
        vals = {k: [S[k]["mcc"], S[k]["f1"], S[k]["precision"], S[k]["recall"], S[k]["accuracy"]] for k in S}
        angles = [i / float(n) * 2 * np.pi for i in range(n)]; angles += angles[:1]
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        colors = {"S1": "steelblue", "S2": "crimson", "S3": "forestgreen", "S4": "darkorange"}
        for k in ["S1", "S2", "S3", "S4"]:
            v = vals[k] + vals[k][:1]
            ax.plot(angles, v, "o-", linewidth=2, color=colors[k], label=t["radar_labels"][k])
            ax.fill(angles, v, alpha=0.05, color=colors[k])
        ax.set_xticks(angles[:-1]); ax.set_xticklabels(cats, fontsize=11); ax.set_ylim([0, 1.05])
        ax.set_title(t["radar_title"], fontsize=12, fontweight="bold", pad=20)
        ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join(OUT[lang], f"evaluation_radar_2x2_{lang}.png"), bbox_inches="tight", dpi=150)
        plt.close(fig)

        # --- Grouped bar ---
        mets = t["bar_metrics"]; x = np.arange(len(mets)); w = 0.2
        series = {k: [S[k]["mcc"], S[k]["f1"], S[k]["precision"], S[k]["recall"]] for k in S}
        fig, ax = plt.subplots(figsize=(10, 6))
        specs = [("S1", -1.5, "steelblue"), ("S2", -0.5, "crimson"),
                 ("S3", 0.5, "forestgreen"), ("S4", 1.5, "darkorange")]
        for k, off, col in specs:
            ax.bar(x + off * w, series[k], w, label=t["radar_labels"][k], color=col, edgecolor="black", linewidth=0.5)
        ax.set_xlabel(t["bar_xlabel"]); ax.set_ylabel(t["bar_ylabel"])
        ax.set_title(t["bar_title"].format(eps=EPSILON), fontsize=12, fontweight="bold")
        ax.set_xticks(x); ax.set_xticklabels(mets, fontsize=11)
        ax.legend(loc="lower left", fontsize=10); ax.set_ylim([0, 1.15]); ax.grid(True, alpha=0.3, axis="y")
        plt.tight_layout()
        plt.savefig(os.path.join(OUT[lang], f"evaluation_grouped_bar_2x2_{lang}.png"), bbox_inches="tight", dpi=150)
        plt.close(fig)
        print(f"[{lang}] saved 3 figures to {OUT[lang]}", flush=True)

    print("Done. Bilingual evaluation figures generated.", flush=True)


if __name__ == "__main__":
    main()
