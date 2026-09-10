# DT_AI — Digital Twin for Human Stress & Error Risk in High-Risk Work

See [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md) for scope, hypotheses, datasets,
roles, and milestones.

## Layout

    data/raw/         downloaded datasets, never edited, never committed
    data/interim/     per-subject resampled/aligned signals
    data/processed/   model-ready feature tables
    src/data/         loaders, one module per dataset
    src/features/     HRV, EDA decomposition, ACC activity counts
    src/models/       baselines (H1 comparators)
    src/twin/         latent state-space model — the forward-simulable core
    src/eval/         H1 / H2 evaluation protocols, subject-level splits
    notebooks/        exploration only; nothing load-bearing lives here
    reports/figures/  paper figures, one per author (see plan §5)

## Ground rules

- Splits are **by subject**, never by window. Window-level splits leak and
  inflate every stress-detection result in this literature.
- Week 3-4 gate: reproduce a published WESAD baseline before building
  anything new.
- `src/twin/` must stay forward-simulable. If a change makes the model
  unable to roll out without observations, it breaks hypothesis H2.

## Setup

    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
