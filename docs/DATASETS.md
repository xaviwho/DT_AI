# Dataset acquisition status

Last attempted: 2026-09-10. Archives land in `data/raw/_archives/`.

## Acquired and integrity-verified

| Dataset | File | Bytes | Check |
|---|---|---|---|
| DriveDB (Stress Recognition in Automobile Drivers) | `drivedb.zip` | 113,937,531 | `unzip -t` clean, matches server content-length |
| MMASH | `mmash.zip` | 23,780,300 | `unzip -t` clean, matches server content-length |
| EEGMAT | `eegmat.zip` | 183,634,285 | `unzip -t` clean, matches server content-length |

Source (all open, no credentialing):
- DriveDB — https://physionet.org/content/drivedb/1.0.0/
- MMASH — https://physionet.org/content/mmash/1.0.0/
- EEGMAT — https://physionet.org/content/eegmat/1.0.0/

MMASH ships a `SHA256SUMS.txt`; verify against it before use.

## BLOCKED — requires manual action

### WESAD — host unreachable from this machine
The official distribution is a sciebo (uni-siegen.de) link. `uni-siegen.sciebo.de`
does not respond from here: connection reset at the host root, not just the file
path. This is a network/firewall block, not a bad URL.

The UCI entry (dataset 465) is **not** a mirror — it is a 261-byte zip containing
a single `WESAD.txt` pointing back at sciebo. Note it names a *different* token
than the commonly circulated one:

    https://uni-siegen.sciebo.de/s/pYjSgfOVs6Ntahr/download   <- from UCI stub
    https://uni-siegen.sciebo.de/s/HGdUkoNlW1Ub0Gx/download   <- commonly cited

**Action:** download (~2.1 GB) from a network that can reach sciebo, drop the
zip in `data/raw/_archives/`. Try the UCI-stub token first.

### Nurse Stress (Dryad) — API now requires authentication
`doi:10.5061/dryad.5hqbzkh6f`. Metadata is public and confirms the dataset:
*"A multi-modal sensor dataset for continuous stress detection of nurses in a
hospital"*, 1,156,988,590 bytes total, two files:

| File | Bytes | SHA-256 |
|---|---|---|
| `Stress_dataset.zip` | 1,156,939,542 | `86e7146cbb124f9b5e37bc5bd8fa63f8786379dfdb10dfc9fdc5fd6c41e63407` |
| `SurveyResults.xlsx` | 49,048 | `4ee7733f8e8da362af33a765c495f4a5ed8302b5af39327c2cdb...` (truncated) |

Every download route returns an error: the v2 API download endpoints give
`401 {"error":"Unauthorized, must have current bearer token"}`, and the web
`file_stream` route gives a bot-blocked `403`.

**Action:** download via a browser from https://datadryad.org/dataset/doi:10.5061/dryad.5hqbzkh6f
Verify with the SHA-256 above — Dryad publishes it, so we can confirm integrity
even though we fetched it by hand.

Get `SurveyResults.xlsx` first, it is 49 KB. It carries the stress
self-reports, and its annotation density decides whether H1 is testable on this
dataset at all. That is the single assumption the whole plan rests on.

### SWELL-KW — access request required
Distributed via DANS EASY under a request form; no direct download exists.
Only needed if the Nurse labels prove too sparse and we need the H1 fallback.
Start the request now if we want it, since approval takes time.

### OSHA Severe Injury Reports — bot-blocked
`https://www.osha.gov/sites/default/files/severeinjury.csv` returns `403`.
Fetch manually from https://www.osha.gov/severeinjury or the DOL data catalog.
Narrative text for Maame Yaa's error taxonomy; not on the modeling critical path.

## Licensing — do before use, not after

Each carries its own terms. PhysioNet sets are ODC-BY 1.0 or similar; the Dryad
nurse set is CC0. Record the license per dataset here before anything goes in
a manuscript.

---

## Characterization (2026-09-18)

Extracted and inspected the three acquired datasets. All checksums verify
(MMASH 2/2, DriveDB 37/37, EEGMAT 75/75). Findings below are from the data,
not the documentation, and several contradict the documentation.

### DriveDB — 18 records, but only 14 usable subjects

| Issue | Detail | Consequence |
|---|---|---|
| **drive13 == drive14** | Bit-identical across all 5 shared channels (74,836 samples each). Same recording published twice, differing only in which extra channel is included (HR vs hand GSR). | Treating them as two subjects duplicates one subject across a split. **Direct leakage.** True N = 14. |
| **No usable labels** | The `marker` channel is not a protocol-segment label. It is a drifting analog trace: 894 unique digital values in drive05, baseline ~1200 with excursions to 9061, ~24k transitions. | Protocol boundaries (rest/city/highway) must come from the timings in Healey & Picard's paper. **Not available in the files.** |
| **drive01, drive03** | No `marker` channel at all. | Excluded. |
| **drive07 typo** | Channel is spelled `hand GSr`. | Exact-string matching silently drops it; the record still loads, so it fails quietly. Handled in the loader. |
| **drive15** | Trailing empty signal name in the header. | Handled in the loader. |
| **drive17a / drive17b** | Two segments of one subject. | Must share a split side. Handled via `subject_id()`. |

Records are long (~80 min), which is the one thing DriveDB has going for it.

### MMASH — biomarker layer is far thinner than the plan assumed

22 subjects. Per subject: `Actigraph.csv`, `Activity.csv`, `RR.csv`
(inter-beat intervals with day/time), `questionnaire.csv`, `saliva.csv`,
`sleep.csv`, `user_info.csv`.

**`saliva.csv` has exactly 2 samples per subject** — "before sleep" and
"wake up" — giving cortisol and melatonin. That is 44 cortisol values in
total across the study.

This does not support a biomarker *modeling* layer. It supports a
correlational side-analysis at best. The plan's §3 Layer-1 biomarker channel
and the Barry/Calista assignment need rescoping, or the saliva angle moves
to a future data collection.

The genuine strength here is continuous 24h RR plus actigraphy, with
questionnaires (STAI, PANAS, Daily_stress) at 4 timepoints (10/14/18/22h).
That is the only *trajectory* data currently in hand.

### EEGMAT — the only real performance outcome, but cross-sectional

36 subjects, 75 EDF files. `subject-info.csv` gives **"Number of
subtractions"** (range 1.0–34.59, mean 17.6) and a binary "Count quality".
This is a genuine cognitive-performance measure, which nothing else we have
provides.

Two limits:
- Recordings are **60-second artifact-free segments**. One rest (`_1`) and
  one task (`_2`) per subject. No trajectory, so this cannot test H2.
- Documentation inconsistency: README says 24 good / 12 bad counters; the
  CSV gives 26 / 10. Use the CSV, and note the discrepancy in any writeup.

### Consequence for the hypotheses

| | H1 (predicts performance decrement) | H2 (forward simulation) |
|---|---|---|
| DriveDB | No — no performance measure, and no usable labels without the paper's timings | No |
| MMASH | Weak — self-report only, 4 timepoints | Partial — 24h RR is the only trajectory data in hand |
| EEGMAT | Cross-sectional only — one scalar per subject | No |

**None of the three acquired datasets can test H2, and none has a
time-resolved performance outcome.** The Nurse Stress dataset is therefore
not the preferred option — it is load-bearing. Until it is obtained, the
project as scoped in PROJECT_PLAN.md cannot be executed.
