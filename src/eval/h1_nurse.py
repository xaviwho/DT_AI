"""H1 on the nurse corpus: does physiological state predict reported stress?

Binary low (0) vs high (2) self-reported stress. The middle class is
dropped: it has 14 usable instances and is absent for most nurses.

Mirrors the exam analysis so the two are comparable:
- same five pre-specified features
- leave-one-SUBJECT-out, predictions pooled across folds before scoring
  (many held-out nurses have only one class, so per-fold AUROC is undefined)
- within-subject centring of predictors, so the model cannot win by
  learning which nurse it is looking at
- AUROC and AUPRC, never accuracy: prevalence is 85% and accuracy is
  therefore meaningless
- significance by within-subject permutation; uncertainty by subject-level
  bootstrap
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

PRESPEC = ["hrv_rmssd", "hr_mean", "eda_scr_rate", "eda_tonic", "acc_counts"]


def prepare(df: pd.DataFrame, block: str = "x_", center: bool = True):
    cols = [f"{block}{c}" for c in PRESPEC]
    d = df[df.usable & df.lvl.isin([0, 2])].dropna(subset=cols).copy()
    d["y"] = (d.lvl == 2).astype(int)
    if center:
        for c in cols:
            d[c] = d[c] - d.groupby("sid")[c].transform("mean")
    # keep only nurses contributing both classes; others cannot inform a
    # within-subject discrimination and only inflate apparent n
    both = d.groupby("sid").y.nunique()
    d = d[d.sid.isin(both[both == 2].index)]
    return d, cols


def loso(d: pd.DataFrame, cols: list[str], C: float = 1.0) -> pd.DataFrame:
    out = []
    for s in sorted(d.sid.unique()):
        tr, te = d[d.sid != s], d[d.sid == s]
        if tr.y.nunique() < 2 or te.empty:
            continue
        m = make_pipeline(
            StandardScaler(),
            LogisticRegression(C=C, class_weight="balanced", max_iter=2000),
        )
        m.fit(tr[cols], tr.y)
        out.append(pd.DataFrame({
            "sid": te.sid.values, "y": te.y.values,
            "p": m.predict_proba(te[cols])[:, 1]}))
    return pd.concat(out, ignore_index=True)


def score(res: pd.DataFrame) -> dict:
    return dict(
        n=len(res), pos=int(res.y.sum()), prevalence=float(res.y.mean()),
        auroc=float(roc_auc_score(res.y, res.p)),
        auprc=float(average_precision_score(res.y, res.p)),
    )


def permutation(d, cols, n=500, seed=0):
    rng = np.random.default_rng(seed)
    obs = score(loso(d, cols))["auroc"]
    null = []
    for _ in range(n):
        p = d.copy()
        p["y"] = p.groupby("sid").y.transform(
            lambda v: rng.permutation(v.values))
        try:
            r = loso(p, cols)
            if r.y.nunique() > 1:
                null.append(score(r)["auroc"])
        except Exception:
            continue
    null = np.array(null)
    return float((np.sum(null >= obs) + 1) / (len(null) + 1)), obs, null


def bootstrap(res, n=2000, seed=0):
    rng = np.random.default_rng(seed)
    subs = res.sid.unique()
    v = []
    for _ in range(n):
        pick = rng.choice(subs, len(subs), replace=True)
        b = pd.concat([res[res.sid == s] for s in pick], ignore_index=True)
        if b.y.nunique() < 2:
            continue
        v.append(roc_auc_score(b.y, b.p))
    v = np.array(v)
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))
