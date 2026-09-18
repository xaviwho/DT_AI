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

---

## Nurse Stress — SurveyResults.xlsx acquired and analysed (2026-09-18)

Downloaded manually. **Integrity verified**: 49,048 bytes, SHA-256
`4ee7733f8e8da362af33a765c495f4a5ed8302b5af39327c2cdb420a27def2b3`,
an exact match to Dryad's published digest. Stored in
`data/raw/nurse_stress/` (gitignored).

One sheet, 358 rows x 20 cols. Each row is a self-reported stress event with
`Start time`, `End time`, `duration`, `date`, `Stress level`, plus 14 binary
stressor-category flags (COVID related, Patient in Crisis, Increased
Workload, ...) and a free-text `Description`. Dates span 2020-04-14 to
2020-12-13 — the COVID period, which is a confound to state explicitly.

### Density: adequate

15 nurses, median 23 reports each (range 4–46), median 9 distinct shift
dates per nurse. Event durations are short, mostly 3–15 min.

### Three problems that constrain the design

**1. `Stress level` is 32% missing.** 113 of 358 are the string `'na'`
(note: string, not a NaN — it silently makes the column dtype `object`, and
any naive `astype(int)` will crash or coerce wrongly).

**2. Missingness is far from random.** Per-nurse `'na'` fraction ranges from
0.00 to 0.65:

    CE 0.65   DF 0.62   EG 0.55   94 0.53   6B 0.43   15 0.40
    83 0.30   BG 0.28   7A 0.24   5C 0.20   E4 0.12   8B 0.06
    6D 0.00   7E 0.00   F5 0.00

Complete-case analysis therefore silently reweights the cohort toward four
nurses. This needs stating in any writeup, and argues for a
missingness-aware model rather than dropping rows.

**3. The middle class is too rare to model.** Labelled distribution is
level 2 = 179, level 0 = 46, level 1 = **20**. Level 1 is absent entirely in
9 of 15 nurses.

| Design | Viable? |
|---|---|
| 3-class (0/1/2) | **No.** n=20 in class 1, absent for 9/15 nurses |
| Binary (0 vs 2) | **Yes.** 46 vs 179, and 13 of 15 nurses have both classes |

Per-nurse labelled totals are small (median 16, min 4), so subject-level
cross-validation will have high variance. Report confidence intervals, not
point accuracies.

### The finding that matters most for the plan

**This dataset has labelled stress, not performance.** There is no reaction
time, no error rate, no task outcome — only self-reported stress level.

H1 is currently worded as predicting *performance decrement*. No dataset we
now hold can test that, including this one. H1 must either be reworded to
predict self-reported stress (weaker, and the exact framing PROJECT_PLAN.md
§9 warns reviewers will push back on), or the project needs new data
collection with a performance task.

This is a scoping decision for the group, not a technical one.

---

## Nurse Stress — full dataset acquired and aligned (2026-09-18)

`Stress_dataset.zip` downloaded manually. **Integrity verified**:
1,156,939,542 bytes, SHA-256
`86e7146cbb124f9b5e37bc5bd8fa63f8786379dfdb10dfc9fdc5fd6c41e63407`,
exact match to Dryad's published digest.

Structure: 15 folders (matching the survey IDs exactly), containing **609
nested per-session zips** named `<ID>_<unix_start>.zip`. Each is a standard
Empatica E4 export: `ACC/BVP/EDA/HR/IBI/TEMP.csv`, `tags.csv`, `info.txt`.
E4 CSVs carry the start epoch on line 1 and the sample rate on line 2
(EDA 4 Hz, HR 1 Hz, BVP 64 Hz, ACC 32 Hz).

All 609 sessions are readable. **1,252 hours** of recording, median session
70 min. Per-nurse totals range 24–150 h. A session index is cached at
`data/interim/e4_sessions.csv`.

### Timezone: UTC-5, solved empirically

Survey times are local; E4 timestamps are UTC. Sweeping candidate offsets
and maximising survey/signal overlap gives an unambiguous peak at **UTC-5**
(US Central Daylight Time, consistent with the hospital and the Apr–Dec 2020
window):

    UTC-5: 227 reports overlap (63%)   <- peak
    UTC-6: 189 (53%)
    UTC-4: 164 (46%)

This offset is an inference, not documented. It should be stated as an
assumption in any writeup.

### Attrition: 358 reports -> 149 usable examples

| Stage | n | nurses |
|---|---|---|
| All survey reports | 358 | 15 |
| Labelled (not `'na'`) | 245 | 15 |
| Labelled **and** signal-covered | 166 | **12** |
| Binary (0 vs 2), >90% covered | **149** | **12** |

Class balance of the usable binary set: **class 0 = 23, class 2 = 126**
(85% majority). Only **10 of 12** nurses have both classes.

Three nurses (`15`, `83`, `94`) have labels but **no overlapping signal at
all** and drop out entirely — note that `83` and `94` are among the
best-recorded nurses by hours, so this is a scheduling mismatch, not a
device-failure story.

Coverage is close to all-or-nothing: relaxing the threshold from >90% to
>0% recovers only 3 more reports (163 -> 166). Sessions either span a
report window or miss it entirely, so the threshold choice is not a
sensitive parameter.

### What this means

The modelling target is a **binary, heavily imbalanced, small-n** problem:
149 examples, 23 in the minority class, spread over 10 usable nurses —
roughly 2 minority examples per nurse.

Consequences, all of which should be settled before modelling starts:

- Subject-level cross-validation is mandatory, and with 23 positives it
  will have very high variance. Report confidence intervals; a single
  accuracy number will be meaningless.
- Accuracy is the wrong metric at 85% majority. Use AUROC/AUPRC with
  subject-level bootstrap.
- The earlier non-random missingness finding compounds this: nurses drop
  out both from `'na'` labels and from coverage gaps, and these are
  different subsets.

H2 remains untestable: there is still no performance outcome anywhere in
the corpus.
