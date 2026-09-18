"""Window-level physiological features from Empatica E4 signals.

Deliberately dependency-light: numpy + scipy only. Every feature is a
documented formula rather than a library call, so the pipeline is auditable
by a reviewer and stable across library versions.

HRV comes from the E4's own IBI stream where available. Where IBI is empty
(common in the nurse corpus, where sessions are short and motion-heavy) the
HRV block is returned as NaN rather than silently imputed - missingness here
is informative and must survive into the model.
"""

from __future__ import annotations

import numpy as np
from scipy import signal as sps

from ..data.e4 import Session

# EDA decomposition cutoffs (Hz). Standard split: slow tonic drift vs
# phasic skin-conductance responses.
TONIC_HZ = 0.05
PHASIC_LO, PHASIC_HI = 0.05, 1.0


def _slope(x: np.ndarray, fs: float) -> float:
    """Least-squares slope per minute."""
    if len(x) < 3:
        return np.nan
    t = np.arange(len(x)) / fs / 60.0
    return float(np.polyfit(t, x, 1)[0])


def _hrv(ibi: np.ndarray) -> dict[str, float]:
    """Time-domain HRV. ibi in seconds.

    Physiologically implausible intervals are dropped before computing:
    the E4's beat detector emits artefacts under motion.
    """
    v = ibi[(ibi > 0.3) & (ibi < 2.0)] * 1000.0  # ms
    if len(v) < 10:
        return dict(hrv_n=len(v), hrv_mean=np.nan, hrv_sdnn=np.nan,
                    hrv_rmssd=np.nan, hrv_pnn50=np.nan)
    d = np.diff(v)
    return dict(
        hrv_n=len(v),
        hrv_mean=float(v.mean()),
        hrv_sdnn=float(v.std(ddof=1)),
        hrv_rmssd=float(np.sqrt((d ** 2).mean())),
        hrv_pnn50=float((np.abs(d) > 50).mean()),
    )


def _eda(x: np.ndarray, fs: float) -> dict[str, float]:
    if len(x) < int(fs * 10):  # need >=10 s
        return dict(eda_mean=np.nan, eda_sd=np.nan, eda_slope=np.nan,
                    eda_tonic=np.nan, eda_scr_rate=np.nan, eda_scr_amp=np.nan)
    out = dict(eda_mean=float(np.mean(x)), eda_sd=float(np.std(x)),
               eda_slope=_slope(x, fs))
    nyq = fs / 2
    try:
        b, a = sps.butter(2, TONIC_HZ / nyq, btype="low")
        tonic = sps.filtfilt(b, a, x)
        b, a = sps.butter(2, [PHASIC_LO / nyq, min(PHASIC_HI / nyq, 0.99)],
                          btype="band")
        phasic = sps.filtfilt(b, a, x)
    except ValueError:
        out.update(eda_tonic=np.nan, eda_scr_rate=np.nan, eda_scr_amp=np.nan)
        return out
    # SCR peaks: at least 0.01 uS prominence, >=1 s apart (standard).
    pk, props = sps.find_peaks(phasic, prominence=0.01, distance=int(fs))
    minutes = len(x) / fs / 60.0
    out.update(
        eda_tonic=float(np.mean(tonic)),
        eda_scr_rate=float(len(pk) / minutes) if minutes > 0 else np.nan,
        eda_scr_amp=float(np.mean(props["prominences"])) if len(pk) else 0.0,
    )
    return out


def _acc(a: np.ndarray, fs: float) -> dict[str, float]:
    if a.ndim != 2 or len(a) < int(fs * 5):
        return dict(acc_mag_mean=np.nan, acc_mag_sd=np.nan, acc_counts=np.nan)
    mag = np.linalg.norm(a, axis=1)
    # Activity counts: mean absolute deviation of the high-passed magnitude,
    # a standard actigraphy proxy that ignores the gravity component.
    hp = np.abs(np.diff(mag))
    return dict(acc_mag_mean=float(mag.mean()), acc_mag_sd=float(mag.std()),
                acc_counts=float(hp.mean() * fs))


def window_features(sess: Session, a: float, b: float) -> dict[str, float]:
    """Features over the epoch-second window [a, b)."""
    f: dict[str, float] = {"win_s": b - a}
    f.update(_hrv(sess.ibi_in(a, b)))

    hr = sess.signals.get("HR")
    if hr is not None:
        x = hr.slice_time(a, b)
        f.update(hr_mean=float(np.mean(x)) if len(x) else np.nan,
                 hr_sd=float(np.std(x)) if len(x) > 1 else np.nan,
                 hr_slope=_slope(x, hr.fs) if len(x) > 2 else np.nan)
    else:
        f.update(hr_mean=np.nan, hr_sd=np.nan, hr_slope=np.nan)

    eda = sess.signals.get("EDA")
    f.update(_eda(eda.slice_time(a, b), eda.fs) if eda is not None
             else _eda(np.array([]), 4.0))

    tmp = sess.signals.get("TEMP")
    if tmp is not None:
        x = tmp.slice_time(a, b)
        f.update(temp_mean=float(np.mean(x)) if len(x) else np.nan,
                 temp_sd=float(np.std(x)) if len(x) > 1 else np.nan,
                 temp_slope=_slope(x, tmp.fs) if len(x) > 2 else np.nan)
    else:
        f.update(temp_mean=np.nan, temp_sd=np.nan, temp_slope=np.nan)

    acc = sess.signals.get("ACC")
    f.update(_acc(acc.slice_time(a, b), acc.fs) if acc is not None
             else _acc(np.zeros((0, 3)), 32.0))
    return f


FEATURE_COLS = [
    "hrv_mean", "hrv_sdnn", "hrv_rmssd", "hrv_pnn50",
    "hr_mean", "hr_sd", "hr_slope",
    "eda_mean", "eda_sd", "eda_slope", "eda_tonic", "eda_scr_rate", "eda_scr_amp",
    "temp_mean", "temp_sd", "temp_slope",
    "acc_mag_mean", "acc_mag_sd", "acc_counts",
]
