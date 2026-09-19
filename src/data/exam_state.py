"""Duration-matched windows for the state-detection task.

The naive contrast (whole baseline vs whole exam) has a confound: baseline
segments run ~40-65 min while exam windows run 90-180 min. Any feature with
a duration dependence would let a classifier separate the classes by window
length rather than physiology.

This module takes a fixed MATCH_MIN minutes from each: the segment
immediately BEFORE exam onset, and the segment immediately AFTER it. Both
classes then have identical support, and the contrast is anchored on the
same moment in time, which also removes slow drift (circadian, ambient
temperature) that would otherwise differ between a 07:55 baseline and a
late-morning exam.
"""

from __future__ import annotations

import glob
from pathlib import Path

import pandas as pd

from .e4 import read_dir
from .exam_stress import DATA, exam_window, load_grades
from ..features.physio import window_features

MATCH_MIN = 35.0   # fits inside the shortest baseline (40.8 min)


def build(match_min: float = MATCH_MIN) -> pd.DataFrame:
    rows = []
    for d in sorted(glob.glob(str(DATA / "S*") + "/*/")):
        p = Path(d)
        sid, exam = p.parent.name, p.name
        sess = read_dir(p, sid, exam)
        a, _ = exam_window(sess, exam)
        rec0 = sess.signals["EDA"].t0
        w = match_min * 60
        if a - w < rec0:
            continue  # not enough pre-exam signal for a matched window
        for state, (s, e) in (("baseline", (a - w, a)), ("exam", (a, a + w))):
            r = {"sid": sid, "exam": exam, "state": state,
                 "y": int(state == "exam")}
            r.update(window_features(sess, s, e))
            rows.append(r)
    df = pd.DataFrame(rows).merge(load_grades(), on=["sid", "exam"], how="left")
    return df


if __name__ == "__main__":
    df = build()
    out = Path(__file__).resolve().parents[2] / "data" / "processed" / "exam_state.csv"
    df.to_csv(out, index=False)
    print(f"{len(df)} windows ({df.y.sum()} exam / {(1-df.y).sum()} baseline) "
          f"from {df.sid.nunique()} subjects -> {out}")
    print("window minutes:", df.win_s.div(60).round(1).unique())
    print("missing feature cells:", df.isna().sum().sum())
