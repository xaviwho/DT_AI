"""Loader for PhysioNet DriveDB (Healey & Picard, stress in automobile drivers).

Record quirks found by inspecting the headers (see docs/DATASETS.md):

- `marker` is the protocol annotation channel. drive01 and drive03 lack it,
  so they cannot be used for anything supervised.
- drive07 spells the channel "hand GSr" (lowercase r). Exact-string matching
  silently drops it, which is easy to miss because the record still loads.
- drive15 has a trailing empty signal name in its header.
- drive17a and drive17b are two segments of the SAME subject. They must land
  on the same side of any train/test split (see `subject_id`).
- Channels are sampled at different rates; wfdb resamples to the highest
  when reading multi-channel, so ask for what you need explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import wfdb

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
DRIVEDB = RAW / "stress-recognition-in-automobile-drivers-1.0.0"

# Records lacking the marker channel: no protocol labels, unusable for H1.
NO_MARKER = {"drive01", "drive03"}

# Canonical name -> spellings seen across headers.
ALIASES = {
    "ECG": ("ECG",),
    "EMG": ("EMG",),
    "foot_gsr": ("foot GSR",),
    "hand_gsr": ("hand GSR", "hand GSr"),  # drive07 typo
    "HR": ("HR",),
    "marker": ("marker",),
    "RESP": ("RESP",),
}


@dataclass
class Record:
    name: str
    subject_id: str
    fs: float
    signals: dict[str, np.ndarray]

    @property
    def has_marker(self) -> bool:
        return "marker" in self.signals


def subject_id(record_name: str) -> str:
    """drive17a and drive17b are one subject; everything else is 1:1.

    Splitting by record instead of subject would leak that subject across
    train and test.
    """
    stem = record_name.replace("drive", "")
    return "drive" + stem.rstrip("ab") if stem[-1:] in ("a", "b") else record_name


def list_records(include_unlabeled: bool = False) -> list[str]:
    names = sorted(p.stem for p in DRIVEDB.glob("drive*.hea"))
    if include_unlabeled:
        return names
    return [n for n in names if n not in NO_MARKER]


def load_record(name: str, channels: tuple[str, ...] | None = None) -> Record:
    """Read one record, normalising channel names to the canonical set."""
    rec = wfdb.rdrecord(str(DRIVEDB / name))

    # Map header spellings onto canonical names.
    found: dict[str, np.ndarray] = {}
    for idx, raw_name in enumerate(rec.sig_name):
        if not raw_name or not raw_name.strip():
            continue  # drive15 trailing blank
        for canon, spellings in ALIASES.items():
            if raw_name.strip() in spellings:
                found[canon] = rec.p_signal[:, idx]
                break

    if channels is not None:
        missing = set(channels) - set(found)
        if missing:
            raise KeyError(f"{name} is missing channels: {sorted(missing)}")
        found = {c: found[c] for c in channels}

    return Record(
        name=name,
        subject_id=subject_id(name),
        fs=float(rec.fs),
        signals=found,
    )


if __name__ == "__main__":
    usable = list_records()
    subjects = {subject_id(n) for n in usable}
    print(f"{len(usable)} labelled records, {len(subjects)} distinct subjects")
    for n in usable:
        r = load_record(n)
        dur = len(next(iter(r.signals.values()))) / r.fs / 60
        print(f"  {n:10s} subj={r.subject_id:8s} {dur:5.1f} min  "
              f"{len(r.signals)} ch  marker={r.has_marker}")
