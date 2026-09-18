"""Paper figures for the exam-corpus H1 analysis."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd
from scipy import stats
from .h1 import prepare, loso, metrics, PRESPEC

ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "reports" / "figures"
LAB = {"hrv_rmssd": "HRV RMSSD (ms)", "hr_mean": "Heart rate (bpm)",
       "eda_scr_rate": "SCR rate (/min)", "eda_tonic": "EDA tonic (uS)",
       "acc_counts": "Activity counts"}


def fig1_manipulation(df):
    fig, ax = plt.subplots(1, 5, figsize=(15, 3.4))
    for i, c in enumerate(PRESPEC):
        b, x = df[f"b_{c}"], df[f"x_{c}"]
        ok = b.notna() & x.notna()
        for bb, xx in zip(b[ok], x[ok]):
            ax[i].plot([0, 1], [bb, xx], color="0.6", lw=.8, alpha=.7)
        ax[i].plot([0, 1], [b[ok].mean(), x[ok].mean()], "o-", color="crimson", lw=2.5, ms=7)
        t, p = stats.ttest_rel(x[ok], b[ok])
        ax[i].set_xticks([0, 1]); ax[i].set_xticklabels(["baseline", "exam"])
        ax[i].set_title(f"{LAB[c]}\nt={t:.2f}, p={p:.4f}", fontsize=9)
        ax[i].spines[["top", "right"]].set_visible(False)
    fig.suptitle("Fig 1. Features separate exam from pre-exam baseline (paired, n=30)", y=1.04)
    fig.tight_layout(); fig.savefig(FIG / "fig1_manipulation_check.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig2_null(df):
    d, cols = prepare(df, "d_")
    res = loso(d, cols); m = metrics(res.y.values, res.yhat.values)
    fig, ax = plt.subplots(1, 2, figsize=(9.5, 4))
    ax[0].axhline(0, color="0.8", lw=.8); ax[0].axvline(0, color="0.8", lw=.8)
    for s in res.sid.unique():
        r = res[res.sid == s]
        ax[0].scatter(r.yhat, r.y, s=42, alpha=.85, label=s)
    lim = np.array([-1, 1]) * max(abs(res.y).max(), abs(res.yhat).max()) * 1.1
    ax[0].plot(lim, lim, "--", color="0.5", lw=1)
    ax[0].set_xlabel("predicted grade deviation (pp)")
    ax[0].set_ylabel("actual grade deviation (pp)")
    ax[0].set_title(f"Leave-one-subject-out\nrho={m['spearman']:.3f}, R2={m['r2']:.3f}", fontsize=10)
    ax[0].spines[["top", "right"]].set_visible(False)

    rows = []
    for c in PRESPEC:
        v = d[f"d_{c}"]
        rho, p = stats.spearmanr(v, d.grade_dev)
        rows.append((LAB[c], rho, p))
    rows.sort(key=lambda r: r[1])
    y = np.arange(len(rows))
    ax[1].barh(y, [r[1] for r in rows], color=["crimson" if r[2] < .05 else "0.7" for r in rows])
    ax[1].axvline(0, color="0.3", lw=.8)
    ax[1].set_yticks(y); ax[1].set_yticklabels([r[0] for r in rows], fontsize=8)
    ax[1].set_xlabel("Spearman rho vs grade deviation\n(red = nominal p<.05, uncorrected)")
    ax[1].set_xlim(-.6, .6)
    n_sig = sum(1 for r in rows if r[2] < .05)
    ax[1].set_title(f"{n_sig} of 5 nominally p<.05\n(neither survives Holm correction)",
                    fontsize=10)
    ax[1].spines[["top", "right"]].set_visible(False)
    fig.suptitle("Fig 2. EDA arousal tracks lower relative performance, but the\n"
                 "multivariate model does not generalise out-of-subject", y=1.06, fontsize=11)
    fig.tight_layout(); fig.savefig(FIG / "fig2_h1_null.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(ROOT / "data" / "processed" / "exam_features.csv")
    fig1_manipulation(df); fig2_null(df)
    print("wrote", *(p.name for p in sorted(FIG.glob("*.png"))))
