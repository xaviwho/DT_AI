"""Paper figure for the nurse-corpus H1 analysis."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd
from sklearn.metrics import roc_curve, roc_auc_score
from scipy import stats
from .h1_nurse import prepare, loso, score, bootstrap, PRESPEC

ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "reports" / "figures"
LAB = {"hrv_rmssd": "HRV RMSSD", "hr_mean": "Heart rate",
       "eda_scr_rate": "SCR rate", "eda_tonic": "EDA tonic",
       "acc_counts": "Activity counts"}


def fig3(df):
    d, cols = prepare(df, "x_", True)
    res = loso(d, cols); s = score(res)
    lo, hi = bootstrap(res, n=1000, seed=0)

    fig, ax = plt.subplots(1, 3, figsize=(13.5, 4))

    # attrition waterfall
    stages = [("all reports", len(df)),
              ("labelled", int(df.labelled.sum())),
              ("+ signal covered", int(df.usable.sum())),
              ("binary 0 vs 2", int((df.usable & df.lvl.isin([0, 2])).sum())),
              ("both classes\nper nurse", len(d))]
    ax[0].bar(range(len(stages)), [v for _, v in stages], color="steelblue")
    for i, (_, v) in enumerate(stages):
        ax[0].text(i, v + 5, str(v), ha="center", fontsize=9)
    ax[0].set_xticks(range(len(stages)))
    ax[0].set_xticklabels([k for k, _ in stages], fontsize=7.5, rotation=30, ha="right")
    ax[0].set_ylabel("reports")
    ax[0].set_title("Attrition: 358 → %d" % len(d), fontsize=10)
    ax[0].spines[["top", "right"]].set_visible(False)

    # ROC
    fpr, tpr, _ = roc_curve(res.y, res.p)
    ax[1].plot(fpr, tpr, color="crimson", lw=2)
    ax[1].plot([0, 1], [0, 1], "--", color="0.6", lw=1)
    ax[1].set_xlabel("false positive rate"); ax[1].set_ylabel("true positive rate")
    ax[1].set_title(f"Leave-one-nurse-out ROC\nAUROC={s['auroc']:.3f} "
                    f"[{lo:.2f}, {hi:.2f}]", fontsize=10)
    ax[1].spines[["top", "right"]].set_visible(False)

    # univariate
    rows = []
    for c in PRESPEC:
        rho, p = stats.spearmanr(d[f"x_{c}"], d.y)
        rows.append((LAB[c], rho, p))
    rows.sort(key=lambda r: r[1])
    y = np.arange(len(rows))
    ax[2].barh(y, [r[1] for r in rows],
               color=["crimson" if r[2] < .05 else "0.7" for r in rows])
    ax[2].axvline(0, color="0.3", lw=.8)
    ax[2].set_yticks(y); ax[2].set_yticklabels([r[0] for r in rows], fontsize=8)
    ax[2].set_xlim(-.6, .6)
    ax[2].set_xlabel("Spearman rho vs reported stress")
    ax[2].set_title("No feature reaches p<.05", fontsize=10)
    ax[2].spines[["top", "right"]].set_visible(False)

    fig.suptitle("Fig 3. Nurse corpus: physiology does not discriminate "
                 "self-reported stress", y=1.03)
    fig.tight_layout()
    fig.savefig(FIG / "fig3_nurse_null.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    fig3(pd.read_csv(ROOT / "data" / "processed" / "nurse_features.csv"))
    print("wrote fig3_nurse_null.png")
