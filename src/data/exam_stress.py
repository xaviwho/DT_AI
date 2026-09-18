"""Build the analysis table for the Wearable Exam Stress corpus.

Timing, established from the data rather than taken on trust:

- The README states all exams start 09:00 CT. That holds for the midterms:
  recordings begin 07:55 (M1) / 08:16 (M2), and S6 carries an event tag at
  08:54:32, just before a 09:00 start. Midterm tags also cluster at ~10:53
  across students, a synchronised device-return after a 09:00-10:30 exam.

- It does NOT hold for the Final. Every Final recording starts 10:28 local,
  after 09:00, and no Final session carries any tag. Final exams are
  commonly timetabled outside normal class slots, so we treat the Final
  onset as an ASSUMPTION: recording start + FINAL_LEAD_MIN, where
  FINAL_LEAD_MIN is the median midterm lead-in. `sensitivity_grid()` exists
  so any result can be re-run across plausible onsets.

Quality gating uses EDA, not temperature. E4 skin temperature is heavily
ambient-contaminated: Midterm 1 rooms sat at 26-29 C and Midterm 2 at
30-34 C, so Kleckner's >30 C wear criterion rejects all of Midterm 1 even
though EDA shows the device was plainly worn (EDA > 0.05 uS for ~100% of
every midterm window). Temperature is therefore carried as a covariate and
flagged as a session-level confound, never used as a wear gate.
"""

from __future__ import annotations

import glob
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from .e4 import read_dir
from ..features.physio import window_features, FEATURE_COLS

CT = ZoneInfo("America/Chicago")
ROOT = Path(__file__).resolve().parents[2]
BASE = (ROOT / "data" / "raw" /
        "a-wearable-exam-stress-dataset-for-predicting-cognitive-performance-"
        "in-real-world-settings-1.0.0")
DATA = BASE / "Data"

EXAM_HOURS = {"Midterm 1": 1.5, "Midterm 2": 1.5, "Final": 3.0}
FINAL_LEAD_MIN = 53.0     # median midterm lead-in; see module docstring
MIN_BASELINE_MIN = 10.0   # shortest pre-exam segment we will use


def load_grades() -> pd.DataFrame:
    txt = (BASE / "StudentGrades.txt").read_text(encoding="utf-8",
                                                 errors="replace")
    recs = []
    for block in re.split(r"GRADES\s*-\s*", txt)[1:]:
        head = block.splitlines()[0].strip().upper()
        exam = ("Final" if "FINAL" in head
                else "Midterm 1" if "1" in head else "Midterm 2")
        mx = 200.0 if exam == "Final" else 100.0
        for m in re.finditer(r"S(\d+)\D+(\d+)", block):
            recs.append(dict(sid=f"S{int(m.group(1))}", exam=exam,
                             grade_pct=100 * float(m.group(2)) / mx))
    return pd.DataFrame(recs)


def exam_window(sess, exam: str, final_lead_min: float = FINAL_LEAD_MIN):
    """Return (start, end) epoch seconds for the exam itself."""
    t0 = sess.signals["EDA"].t0
    if exam == "Final":
        a = t0 + final_lead_min * 60
    else:
        lt = datetime.fromtimestamp(t0, CT)
        a = datetime(lt.year, lt.month, lt.day, 9, 0, tzinfo=CT).timestamp()
    return a, a + EXAM_HOURS[exam] * 3600


def build(final_lead_min: float = FINAL_LEAD_MIN) -> pd.DataFrame:
    rows = []
    for d in sorted(glob.glob(str(DATA / "S*") + "/*/")):
        p = Path(d)
        sid, exam = p.parent.name, p.name
        sess = read_dir(p, sid, exam)
        a, b = exam_window(sess, exam, final_lead_min)
        rec0, rec1 = sess.signals["EDA"].t0, sess.signals["EDA"].t1

        r = {"sid": sid, "exam": exam,
             "exam_cov": _cov(sess, a, b),
             "rec_start_local": datetime.fromtimestamp(rec0, CT).strftime("%H:%M")}

        # exam-window features
        for k, v in window_features(sess, a, b).items():
            r[f"x_{k}"] = v
        # pre-exam baseline, if long enough
        if (a - rec0) / 60 >= MIN_BASELINE_MIN:
            for k, v in window_features(sess, rec0, a).items():
                r[f"b_{k}"] = v
            r["baseline_min"] = (a - rec0) / 60
        else:
            for k in FEATURE_COLS:
                r[f"b_{k}"] = np.nan
            r["baseline_min"] = (a - rec0) / 60
        rows.append(r)

    df = pd.DataFrame(rows).merge(load_grades(), on=["sid", "exam"], how="left")
    # reactivity: exam minus own pre-exam baseline
    for c in FEATURE_COLS:
        df[f"d_{c}"] = df[f"x_{c}"] - df[f"b_{c}"]
    # within-subject centring of the outcome (controls for ability)
    df["grade_dev"] = df.grade_pct - df.groupby("sid").grade_pct.transform("mean")
    return df


def _cov(sess, a: float, b: float) -> float:
    """Fraction of the window with usable EDA (device worn)."""
    e = sess.signals["EDA"].slice_time(a, b)
    exp = (b - a) * sess.signals["EDA"].fs
    return float((e > 0.05).sum() / exp) if exp > 0 else 0.0


if __name__ == "__main__":
    df = build()
    out = ROOT / "data" / "processed" / "exam_features.csv"
    df.to_csv(out, index=False)
    print(f"{len(df)} sessions x {df.shape[1]} cols -> {out}")
    print("\nexam-window EDA coverage:")
    print(df.groupby("exam").exam_cov.agg(['min', 'median', 'max']).round(3).to_string())
    print("\nbaseline minutes available:")
    print(df.groupby("exam").baseline_min.agg(['min', 'median', 'max']).round(1).to_string())
    print("\nmissing features (exam window):",
          df[[f"x_{c}" for c in FEATURE_COLS]].isna().sum().sum())
    print("missing features (baseline)   :",
          df[[f"b_{c}" for c in FEATURE_COLS]].isna().sum().sum())
