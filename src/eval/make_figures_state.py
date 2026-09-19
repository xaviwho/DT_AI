"""Figure 4: state detection, and what survives duration matching."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd
from scipy import stats
from sklearn.metrics import roc_curve
from .state_clf import prepare, loso, score, bootstrap

ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "reports" / "figures"
SPEC_LAB = {"all": "All 5 features", "eda": "EDA only",
            "eda_adj": "EDA, activity-adjusted"}
FEATS = ["hr_mean", "acc_counts", "hrv_rmssd", "eda_tonic", "eda_scr_rate"]
LAB = {"hr_mean": "Heart rate", "acc_counts": "Activity", "hrv_rmssd": "HRV RMSSD",
       "eda_tonic": "EDA tonic", "eda_scr_rate": "SCR rate"}


def fig4():
    st = pd.read_csv(ROOT / "data" / "processed" / "exam_state.csv")
    un = pd.read_csv(ROOT / "data" / "processed" / "exam_features.csv")
    fig, ax = plt.subplots(1, 3, figsize=(14, 4.2))

    # ROC curves
    for spec, col in zip(["all", "eda", "eda_adj"], ["crimson", "0.55", "steelblue"]):
        d, cols = prepare(st, spec)
        r = loso(d, cols); s = score(r); lo, hi = bootstrap(r, n=600, seed=0)
        fpr, tpr, _ = roc_curve(r.y, r.p)
        ax[0].plot(fpr, tpr, color=col, lw=2,
                   label=f"{SPEC_LAB[spec]}: {s['auroc']:.2f} [{lo:.2f},{hi:.2f}]")
    ax[0].plot([0, 1], [0, 1], "--", color="0.7", lw=1)
    ax[0].set_xlabel("false positive rate"); ax[0].set_ylabel("true positive rate")
    ax[0].set_title("Exam vs baseline, leave-one-subject-out\n"
                    "(duration-matched 35-min windows)", fontsize=10)
    ax[0].legend(fontsize=8, loc="lower right")
    ax[0].spines[["top", "right"]].set_visible(False)

    # matched vs unmatched effect sizes
    piv = st.pivot_table(index=["sid", "exam"], columns="state", values=FEATS)
    dzm, dzu = [], []
    for f in FEATS:
        b, e = piv[(f, "baseline")], piv[(f, "exam")]
        ok = b.notna() & e.notna()
        dzm.append((e[ok] - b[ok]).mean() / (e[ok] - b[ok]).std(ddof=1))
        bu, eu = un[f"b_{f}"], un[f"x_{f}"]
        ok2 = bu.notna() & eu.notna()
        dzu.append((eu[ok2] - bu[ok2]).mean() / (eu[ok2] - bu[ok2]).std(ddof=1))
    y = np.arange(len(FEATS)); h = 0.38
    ax[1].barh(y + h/2, dzu, h, color="0.75", label="unmatched windows")
    ax[1].barh(y - h/2, dzm, h, color="crimson", label="duration-matched")
    ax[1].axvline(0, color="0.3", lw=.8)
    ax[1].set_yticks(y); ax[1].set_yticklabels([LAB[f] for f in FEATS], fontsize=8)
    ax[1].set_xlabel("paired effect size (dz)")
    ax[1].set_title("EDA effects vanish under matching;\ncardiac and motor do not",
                    fontsize=10)
    ax[1].legend(fontsize=8); ax[1].spines[["top", "right"]].set_visible(False)

    # Result 2 under matching
    g = st[["sid", "exam", "grade_pct"]].drop_duplicates()
    p2 = piv.reset_index(); p2.columns = ["sid", "exam"] + [f"{a}_{b}" for a, b in p2.columns[2:]]
    d2 = p2.merge(g, on=["sid", "exam"])
    d2["grade_dev"] = d2.grade_pct - d2.groupby("sid").grade_pct.transform("mean")
    rows = []
    for f in FEATS:
        v = d2[f"{f}_exam"] - d2[f"{f}_baseline"]
        v = v - v.groupby(d2.sid).transform("mean")
        ok = v.notna() & d2.grade_dev.notna()
        if ok.sum() < 5:
            continue
        rho, p = stats.spearmanr(v[ok], d2.grade_dev[ok])
        rows.append((LAB[f], rho, p))
    rows.sort(key=lambda r: r[1])
    y2 = np.arange(len(rows))
    ax[2].barh(y2, [r[1] for r in rows],
               color=["crimson" if r[2] < .05 else "0.7" for r in rows])
    ax[2].axvline(0, color="0.3", lw=.8)
    ax[2].set_yticks(y2); ax[2].set_yticklabels([r[0] for r in rows], fontsize=8)
    ax[2].set_xlim(-.6, .6)
    ax[2].set_xlabel("Spearman rho vs grade deviation")
    ax[2].set_title("EDA-performance link survives matching\n"
                    "(but not Holm correction)", fontsize=10)
    ax[2].spines[["top", "right"]].set_visible(False)

    fig.suptitle("Fig 4. State detection is strong; the performance link is not", y=1.03)
    fig.tight_layout()
    fig.savefig(FIG / "fig4_state_detection.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    fig4()
    print("wrote fig4_state_detection.png")
