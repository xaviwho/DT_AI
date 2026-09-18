"""H1 on the exam corpus: does physiological state predict performance?

Design decisions, all made to protect a small-n result from itself:

- Outcome is `grade_dev`: each session's grade minus that student's own mean
  across their three exams. This removes ability, the dominant between-
  subject confound, and makes the question within-subject: on a day this
  student was more physiologically aroused, did they underperform *relative
  to themselves*?

- Predictors are within-subject centred for the same reason. Without this,
  between-subject physiology (resting HR differs hugely between people)
  leaks in and the model learns who the student is, not their state.

- Validation is leave-one-SUBJECT-out. Leaving out single sessions would
  let the model see a student's other exams and exploit the fact that
  within-subject deviations sum to zero.

- The feature set is PRE-SPECIFIED (5 features, chosen from stress
  physiology, not from looking at these outcomes) because n=30 with 57
  available features would otherwise guarantee an overfit result.

- Significance is assessed by permutation of the outcome WITHIN subject,
  which respects the design; and uncertainty by subject-level bootstrap.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import RidgeCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# Pre-specified: parasympathetic withdrawal, arousal, sympathetic drive,
# tonic arousal, motor restlessness.
PRESPEC = ["hrv_rmssd", "hr_mean", "eda_scr_rate", "eda_tonic", "acc_counts"]


def prepare(df: pd.DataFrame, block: str = "d_") -> tuple:
    cols = [f"{block}{c}" for c in PRESPEC]
    d = df.dropna(subset=cols + ["grade_dev"]).copy()
    # within-subject centring of predictors
    for c in cols:
        d[c] = d[c] - d.groupby("sid")[c].transform("mean")
    return d, cols


def loso(d: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    preds = []
    for s in sorted(d.sid.unique()):
        tr, te = d[d.sid != s], d[d.sid == s]
        if len(tr) < 6 or te.empty:
            continue
        m = make_pipeline(StandardScaler(),
                          RidgeCV(alphas=np.logspace(-2, 3, 30)))
        m.fit(tr[cols], tr.grade_dev)
        p = m.predict(te[cols])
        preds.append(pd.DataFrame({"sid": te.sid.values, "exam": te.exam.values,
                                   "y": te.grade_dev.values, "yhat": p}))
    return pd.concat(preds, ignore_index=True)


def metrics(y: np.ndarray, yhat: np.ndarray) -> dict:
    ss_res = float(((y - yhat) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    rho, p = stats.spearmanr(y, yhat)
    return dict(r2=r2, rmse=float(np.sqrt(((y - yhat) ** 2).mean())),
                spearman=float(rho), spearman_p=float(p),
                mae=float(np.abs(y - yhat).mean()))


def permutation_test(d, cols, n=2000, seed=0) -> float:
    """Shuffle grade_dev WITHIN subject; recompute LOSO Spearman."""
    rng = np.random.default_rng(seed)
    obs = metrics(*loso(d, cols)[["y", "yhat"]].values.T)["spearman"]
    null = []
    for _ in range(n):
        p = d.copy()
        p["grade_dev"] = p.groupby("sid").grade_dev.transform(
            lambda v: rng.permutation(v.values))
        try:
            r = loso(p, cols)
            null.append(metrics(r.y.values, r.yhat.values)["spearman"])
        except Exception:
            continue
    null = np.array(null)
    return float((np.sum(null >= obs) + 1) / (len(null) + 1)), obs, null


def bootstrap_ci(res: pd.DataFrame, n=2000, seed=0) -> tuple:
    rng = np.random.default_rng(seed)
    subs = res.sid.unique()
    vals = []
    for _ in range(n):
        pick = rng.choice(subs, len(subs), replace=True)
        b = pd.concat([res[res.sid == s] for s in pick], ignore_index=True)
        if b.y.nunique() < 3:
            continue
        vals.append(metrics(b.y.values, b.yhat.values)["spearman"])
    v = np.array(vals)
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))
