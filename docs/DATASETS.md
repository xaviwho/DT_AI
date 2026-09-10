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
