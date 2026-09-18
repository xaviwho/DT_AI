"""Build the analysis table for the Nurse Stress corpus.

Design notes:

- Timezone is UTC-5, inferred by maximising survey/signal overlap (see
  docs/DATASETS.md). It is an assumption, not documented by the authors,
  so `build()` takes `offset_h` and results should be checked against it.

- Only reports with a real label (not the string 'na') AND >=90% E4
  coverage enter the table. Both filters are recorded per row so the
  attrition is auditable rather than silent.

- A pre-report baseline is taken from the BASELINE_MIN minutes immediately
  before the report window, from the same session, so reactivity features
  mirror the exam corpus. Where the session does not extend that far back,
  baseline features are NaN rather than imputed.

- Reports are short (median ~6-10 min), so HRV from the E4's IBI stream is
  often too sparse to be reliable; `hrv_n` is retained so models can see
  how many beats a feature rested on.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .e4 import read_zip
from ..features.physio import window_features, FEATURE_COLS

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "nurse_stress"
SURVEY = RAW / "SurveyResults.xlsx"

OFFSET_H = -5.0       # see docs/DATASETS.md
BASELINE_MIN = 30.0
MIN_COVERAGE = 0.90


def _windows(sv: pd.DataFrame, offset_h: float) -> pd.DataFrame:
    a, b = [], []
    for _, r in sv.iterrows():
        d = pd.Timestamp(r["date"])
        s = pd.Timestamp.combine(d.date(), pd.to_datetime(str(r["Start time"])).time())
        e = pd.Timestamp.combine(d.date(), pd.to_datetime(str(r["End time"])).time())
        if e < s:
            e += pd.Timedelta(days=1)      # overnight shift wrap
        a.append(s.value / 1e9 - offset_h * 3600)
        b.append(e.value / 1e9 - offset_h * 3600)
    out = sv.copy()
    out["t_start"], out["t_end"] = a, b
    return out


def build(offset_h: float = OFFSET_H) -> pd.DataFrame:
    sv = _windows(pd.read_excel(SURVEY), offset_h)
    sess = pd.read_csv(ROOT / "data" / "interim" / "e4_sessions.csv")

    rows = []
    for _, r in sv.iterrows():
        nid, a, b = r["ID"], r["t_start"], r["t_end"]
        cand = sess[(sess.ID == nid) & (sess.t0 <= b) & (sess.t1 >= a)]
        cov = 0.0
        if len(cand):
            ov = np.clip(np.minimum(cand.t1, b) - np.maximum(cand.t0, a), 0, None).sum()
            cov = float(ov / (b - a)) if b > a else 0.0

        row = {"sid": nid, "lvl_raw": r["Stress level"], "coverage": cov,
               "win_min": (b - a) / 60, "date": r["date"]}

        if cov >= MIN_COVERAGE and len(cand):
            # the session covering the most of this window
            best = cand.assign(
                ov=np.clip(np.minimum(cand.t1, b) - np.maximum(cand.t0, a), 0, None)
            ).sort_values("ov").iloc[-1]
            s = read_zip(Path(best["zip"]), nid, Path(best["zip"]).stem)
            for k, v in window_features(s, a, b).items():
                row[f"x_{k}"] = v
            ba = a - BASELINE_MIN * 60
            if s.t0 <= ba:
                for k, v in window_features(s, ba, a).items():
                    row[f"b_{k}"] = v
                row["baseline_min"] = BASELINE_MIN
            else:
                for k in FEATURE_COLS:
                    row[f"b_{k}"] = np.nan
                row["baseline_min"] = max(0.0, (a - s.t0) / 60)
        else:
            for k in FEATURE_COLS:
                row[f"x_{k}"] = np.nan
                row[f"b_{k}"] = np.nan
            row["baseline_min"] = np.nan
        rows.append(row)

    df = pd.DataFrame(rows)
    df["labelled"] = df.lvl_raw != "na"
    df["lvl"] = pd.to_numeric(df.lvl_raw, errors="coerce")
    df["usable"] = df.labelled & (df["coverage"] >= MIN_COVERAGE)
    for c in FEATURE_COLS:
        df[f"d_{c}"] = df[f"x_{c}"] - df[f"b_{c}"]
    return df


if __name__ == "__main__":
    df = build()
    out = ROOT / "data" / "processed" / "nurse_features.csv"
    df.to_csv(out, index=False)
    print(f"{len(df)} reports -> {out}")
    print(f"  labelled          : {df.labelled.sum()}")
    print(f"  usable (>={MIN_COVERAGE:.0%} cov): {df.usable.sum()}  "
          f"nurses={df[df.usable].sid.nunique()}")
    u = df[df.usable]
    print("  class counts      :", u.lvl.value_counts().to_dict())
    print("  binary 0 vs 2     :", int(((u.lvl == 0) | (u.lvl == 2)).sum()))
    print("  baseline available:", u.b_eda_mean.notna().sum(), "of", len(u))
    print("  HRV available     :", u.x_hrv_rmssd.notna().sum(), "of", len(u))
