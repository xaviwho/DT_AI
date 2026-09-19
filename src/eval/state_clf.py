"""State detection: is this 35-minute window an exam or pre-exam baseline?

Three pre-specified specifications, in increasing order of how much they
rule out:

1. `all`      - the five pre-specified features. Shows the effect exists,
                but cannot separate arousal from posture.
2. `eda`      - the two EDA features only. Electrodermal activity is
                largely posture-independent, so this isolates sympathetic
                arousal from the movement confound in Result 2.
3. `eda_adj`  - EDA features residualised on activity counts (within
                subject). The strictest test: any remaining signal cannot
                be explained by how much the person was moving.

Validation is leave-one-subject-out with predictions pooled before
scoring. Windows are duration-matched (35 min each) and time-anchored on
exam onset, so neither length nor drift can drive the result.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ALL = ["hrv_rmssd", "hr_mean", "eda_scr_rate", "eda_tonic", "acc_counts"]
EDA = ["eda_scr_rate", "eda_tonic"]
SPECS = {"all": ALL, "eda": EDA, "eda_adj": EDA}


def prepare(df: pd.DataFrame, spec: str) -> tuple[pd.DataFrame, list[str]]:
    cols = list(SPECS[spec])
    d = df.dropna(subset=cols + ["acc_counts"]).copy()
    # within-subject centring: the model must not win by learning who this is
    for c in set(cols + ["acc_counts"]):
        d[c] = d[c] - d.groupby("sid")[c].transform("mean")
    if spec == "eda_adj":
        # residualise each EDA feature on activity counts
        for c in cols:
            lr = LinearRegression().fit(d[["acc_counts"]], d[c])
            d[c] = d[c] - lr.predict(d[["acc_counts"]])
    return d, cols


def loso(d: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = []
    for s in sorted(d.sid.unique()):
        tr, te = d[d.sid != s], d[d.sid == s]
        if tr.y.nunique() < 2 or te.empty:
            continue
        m = make_pipeline(StandardScaler(),
                          LogisticRegression(max_iter=2000, class_weight="balanced"))
        m.fit(tr[cols], tr.y)
        out.append(pd.DataFrame({"sid": te.sid.values, "y": te.y.values,
                                 "p": m.predict_proba(te[cols])[:, 1]}))
    return pd.concat(out, ignore_index=True)


def score(res: pd.DataFrame) -> dict:
    return dict(n=len(res), auroc=float(roc_auc_score(res.y, res.p)),
                auprc=float(average_precision_score(res.y, res.p)),
                acc=float(((res.p > .5).astype(int) == res.y).mean()))


def permutation(d, cols, n=1000, seed=0):
    rng = np.random.default_rng(seed)
    obs = score(loso(d, cols))["auroc"]
    null = []
    for _ in range(n):
        p = d.copy()
        p["y"] = p.groupby("sid").y.transform(lambda v: rng.permutation(v.values))
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
