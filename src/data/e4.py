"""Reader for Empatica E4 session exports.

Both corpora in this project (Wearable Exam Stress, Nurse Stress) ship the
identical E4 format, so this module serves both.

E4 CSV layout (all signal files):
    line 1: start time, unix epoch seconds (UTC)
    line 2: sample rate, Hz
    line 3+: samples, one per row (ACC has three columns)

IBI.csv is the exception: line 1 is the start epoch, then rows of
`offset_seconds, ibi_seconds`. It is produced by Empatica's own beat
detector and can be empty when the signal was too poor to extract beats.
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np

SIGNALS = ("ACC", "BVP", "EDA", "HR", "TEMP")


@dataclass
class Signal:
    name: str
    t0: float
    fs: float
    x: np.ndarray  # (n,) or (n, 3) for ACC

    @property
    def t1(self) -> float:
        return self.t0 + len(self.x) / self.fs

    def times(self) -> np.ndarray:
        return self.t0 + np.arange(len(self.x)) / self.fs

    def slice_time(self, a: float, b: float) -> np.ndarray:
        """Samples falling in [a, b) epoch seconds."""
        i0 = max(0, int(np.ceil((a - self.t0) * self.fs)))
        i1 = min(len(self.x), int(np.floor((b - self.t0) * self.fs)))
        return self.x[i0:i1] if i1 > i0 else self.x[:0]


@dataclass
class Session:
    sid: str
    label: str            # exam name, or session zip stem
    signals: dict[str, Signal]
    ibi: np.ndarray       # (m, 2): offset seconds, ibi seconds
    ibi_t0: float

    def ibi_in(self, a: float, b: float) -> np.ndarray:
        """IBI values (seconds) whose beat time falls in [a, b)."""
        if self.ibi.size == 0:
            return np.array([])
        t = self.ibi_t0 + self.ibi[:, 0]
        return self.ibi[(t >= a) & (t < b), 1]

    @property
    def t0(self) -> float:
        return min(s.t0 for s in self.signals.values())

    @property
    def t1(self) -> float:
        return max(s.t1 for s in self.signals.values())


def _parse_signal(text: str, name: str) -> Signal | None:
    lines = text.strip().splitlines()
    if len(lines) < 3:
        return None
    if name == "ACC":
        t0 = float(lines[0].split(",")[0])
        fs = float(lines[1].split(",")[0])
        x = np.array([[float(v) for v in ln.split(",")] for ln in lines[2:]])
    else:
        t0 = float(lines[0].split(",")[0])
        fs = float(lines[1].split(",")[0])
        x = np.array([float(ln.split(",")[0]) for ln in lines[2:]])
    if fs <= 0 or len(x) == 0:
        return None
    return Signal(name, t0, fs, x)


def _parse_ibi(text: str) -> tuple[np.ndarray, float]:
    lines = text.strip().splitlines()
    if len(lines) < 2:
        return np.zeros((0, 2)), 0.0
    t0 = float(lines[0].split(",")[0])
    rows = []
    for ln in lines[1:]:
        p = ln.split(",")
        if len(p) >= 2:
            try:
                rows.append((float(p[0]), float(p[1])))
            except ValueError:
                continue
    return (np.array(rows) if rows else np.zeros((0, 2))), t0


def read_dir(path: Path, sid: str, label: str) -> Session:
    sigs = {}
    for n in SIGNALS:
        f = path / f"{n}.csv"
        if f.exists():
            s = _parse_signal(f.read_text(), n)
            if s is not None:
                sigs[n] = s
    ibi, ibi_t0 = (_parse_ibi((path / "IBI.csv").read_text())
                   if (path / "IBI.csv").exists() else (np.zeros((0, 2)), 0.0))
    return Session(sid, label, sigs, ibi, ibi_t0)


def read_zip(path: Path, sid: str, label: str) -> Session:
    sigs = {}
    ibi, ibi_t0 = np.zeros((0, 2)), 0.0
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        for n in SIGNALS:
            fn = f"{n}.csv"
            if fn in names:
                s = _parse_signal(z.read(fn).decode(errors="replace"), n)
                if s is not None:
                    sigs[n] = s
        if "IBI.csv" in names:
            ibi, ibi_t0 = _parse_ibi(z.read("IBI.csv").decode(errors="replace"))
    return Session(sid, label, sigs, ibi, ibi_t0)
