# Results — H1 on the Wearable Exam Stress corpus

Generated 2026-09-18. Reproduce with:

    python -m src.data.exam_stress     # builds data/processed/exam_features.csv
    python -m src.eval.make_figures    # writes reports/figures/*.png

## Design

n = 30 sessions (10 students x 3 exams). Outcome is **grade deviation**:
each session's grade minus that student's own mean across their three
exams, which removes ability — the dominant between-subject confound.
Predictors are within-subject centred for the same reason; without it the
model learns *who* the student is rather than their state.

Validation is **leave-one-subject-out**. The feature set was
**pre-specified** at five features (RMSSD, mean HR, SCR rate, tonic EDA,
activity counts) chosen from stress physiology before looking at outcomes:
with 57 available features and n=30, anything else guarantees overfitting.

## Result 1 — the features are valid (Fig 1)

Paired exam-window vs own pre-exam baseline, all 30 sessions:

| Feature | Baseline | Exam | Δ | t | p | dz |
|---|---|---|---|---|---|---|
| HRV RMSSD (ms) | 93.16 | 129.75 | +36.60 | 3.19 | .0034 | 0.58 |
| Heart rate (bpm) | 113.09 | 90.46 | −22.63 | −8.63 | <.0001 | −1.58 |
| SCR rate (/min) | 4.32 | 6.32 | +2.00 | 2.56 | .0158 | 0.47 |
| EDA tonic (µS) | 0.259 | 0.403 | +0.144 | 2.21 | .0354 | 0.40 |
| Activity counts | 84.19 | 62.79 | −21.40 | −3.28 | .0027 | −0.60 |

All five separate the two states. This matters because it rules out the
"features are broken" explanation for Result 3.

**Important caveat on direction.** HR *falls* and RMSSD *rises* during the
exam — the opposite of a naive stress prediction. Activity counts fall by a
similar effect size (dz = −0.60), which explains it: the pre-exam baseline
includes travelling to the exam, so the contrast is dominated by
**posture and physical activity**, not arousal.

The two EDA measures are the exception. Electrodermal activity is largely
independent of posture, and both rise. **EDA carries the genuine
sympathetic-arousal signal here; the cardiac features largely track
movement.** Any writeup must say this — a reviewer will otherwise read the
HR drop as evidence the pipeline is broken.

## Result 2 — EDA arousal tracks lower relative performance (Fig 2, right)

Within-subject centred predictors vs grade deviation, all 30 sessions:

| Feature | Spearman ρ | p | Holm-adjusted p |
|---|---|---|---|
| **SCR rate** | **−0.397** | **.030** | .149 |
| **EDA tonic** | **−0.375** | **.041** | .165 |
| Heart rate | +0.295 | .114 | .341 |
| Activity counts | −0.168 | .376 | .752 |
| HRV RMSSD | +0.015 | .937 | .937 |

Both EDA measures are negative and nominally significant: on exams where a
student showed more sympathetic arousal, they scored **below their own
average**. The direction is physiologically coherent and consistent across
both EDA measures, which are partly independent.

**Neither survives Holm correction across the five pre-specified
features.** This is suggestive, not established.

## Result 3 — the multivariate model does not generalise (Fig 2, left)

Leave-one-subject-out, Ridge on all five features:

| Block | Spearman ρ | R² | RMSE (pp) |
|---|---|---|---|
| Reactivity (exam − baseline) | +0.059 | −0.089 | 9.64 |
| Exam window (absolute) | −0.167 | −0.088 | 9.64 |

Negative R² means the model performs worse than predicting each student's
own mean. Permutation test (outcome shuffled **within subject**, 500
draws): **p = 0.307**. Subject-level bootstrap 95% CI for ρ:
**[−0.325, 0.485]**.

### Sensitivity

The Final's onset is an assumption (see `docs/DATASETS.md`). Varying it
does not rescue the model:

| Final lead-in | ρ | R² |
|---|---|---|
| 23 min | −0.178 | −0.097 |
| 38 min | −0.015 | −0.188 |
| 53 min (primary) | +0.059 | −0.089 |
| 68 min | +0.026 | −0.081 |
| 83 min | +0.018 | −0.119 |

Midterms only (timing confirmed by event tags, n=20): ρ = −0.060, p = .80.

## Power

Minimum detectable |r| at 80% power, α = .05:

| n | min detectable \|r\| |
|---|---|
| 30 sessions | 0.49 |
| 20 (midterms only) | 0.59 |
| 10 (subjects; clustered worst case) | 0.79 |

The observed EDA effects (|ρ| ≈ 0.38–0.40) sit **below** the detection
floor. The study is underpowered for effects of exactly the size it
observed — which is why they are nominally significant but do not survive
correction or cross-validate.

## Honest summary

1. The E4 feature pipeline is validated: it separates exam from baseline
   with large effects.
2. The exam-vs-baseline contrast is **confounded by physical activity**.
   EDA is the interpretable channel; cardiac features are not, here.
3. EDA arousal shows a moderate, physiologically coherent negative
   association with within-subject performance, **nominally significant but
   not robust to multiplicity correction**.
4. No model predicts held-out subjects better than their own mean.
5. The study cannot distinguish "no effect" from "a moderate effect it is
   too small to detect". Both remain live.

Claim 3 with its caveats is a legitimate finding. Claiming prediction of
performance from physiology is not supported by these data.

---

# Results — H1 on the Nurse Stress corpus

Reproduce with:

    python -m src.data.nurse              # builds data/processed/nurse_features.csv
    python -m src.eval.make_figures_nurse # writes reports/figures/fig3_nurse_null.png

## Design

Binary **low (0) vs high (2)** self-reported stress; the middle class is
dropped (14 usable instances, absent for most nurses). Same five
pre-specified features as the exam analysis, same leave-one-subject-out
protocol, same within-subject centring.

Predictions are **pooled across folds before scoring**: many held-out
nurses contribute only one class, so per-fold AUROC is undefined.

Scoring is AUROC and AUPRC, never accuracy — prevalence is 82%, so a
constant "high stress" prediction would score 0.82 and mean nothing.

## Attrition (Fig 3, left)

| Stage | n | nurses |
|---|---|---|
| All survey reports | 358 | 15 |
| Labelled (not `'na'`) | 245 | 15 |
| + ≥90% E4 coverage | 163 | 12 |
| + binary (0 vs 2) | 149 | 12 |
| + nurse contributes both classes | **129** | **10** |

The last filter matters: a nurse with only one class cannot inform a
within-subject discrimination and would only inflate the apparent n.

A further constraint: a 30-minute pre-report baseline exists for only
**101 of 163** usable reports, so reactivity features are secondary here.
HRV is available for 150 of 163 — reports are short (median 6–10 min), so
the E4's IBI stream is often sparse.

## Result — no discrimination (Fig 3, centre and right)

| Specification | n | nurses | AUROC | AUPRC | chance AUPRC |
|---|---|---|---|---|---|
| **Absolute, within-nurse centred (primary)** | 129 | 10 | **0.544** | 0.833 | 0.822 |
| Absolute, raw | 129 | 10 | 0.496 | 0.811 | 0.822 |
| Reactivity vs 30-min baseline | 60 | 8 | 0.416 | 0.695 | 0.750 |

Permutation test (labels shuffled **within nurse**, 300 draws):
**p = 0.299** (null AUROC mean 0.493, SD 0.088).
Subject-level bootstrap 95% CI: **[0.416, 0.683]** — spans 0.5.

No single feature approaches significance (best: activity counts,
ρ = +0.125, p = .160).

## The EDA finding does not replicate

This is the most informative comparison in the project.

| Feature | Exam corpus (vs grade) | Nurse corpus (vs stress) |
|---|---|---|
| SCR rate | ρ = **−0.397**, p = .030 | ρ = +0.075, p = .401 |
| EDA tonic | ρ = **−0.375**, p = .041 | ρ = −0.042, p = .637 |

The exam corpus's nominally significant EDA effects are absent here.

Two readings, and the data cannot separate them:

1. The exam effects were false positives — consistent with their failing
   Holm correction.
2. The outcomes differ. The exam corpus predicts an **objective**
   performance score; the nurse corpus predicts a **self-report**.
   Physiology and self-reported stress are known to decouple, so a genuine
   physiology-performance link need not appear as a
   physiology-self-report link.

Reading 2 is the more interesting hypothesis and cannot be tested without
a corpus carrying both outcome types — which is exactly what TILES would
have provided and no open dataset does.

## Power

| Comparison | Minimum detectable AUROC (80% power) |
|---|---|
| Pooled n=129 (106 high / 23 low) | 0.662 |
| Clustered, treating each nurse as one unit | 0.792 |

Observed AUROC is 0.544. As with the exam corpus, the study is
**underpowered for moderate effects**: an AUROC of 0.60–0.65, which would
be scientifically meaningful, is below this design's detection floor.

## Combined conclusion across both corpora

1. The E4 pipeline is validated (exam manipulation check, large effects).
2. Neither corpus supports predicting the outcome from physiology using a
   pre-specified feature set and honest subject-level validation.
3. The one suggestive signal (EDA arousal vs objective performance) does
   not survive multiplicity correction and does not replicate against a
   self-report outcome.
4. Both studies are underpowered for the effect sizes actually observed,
   so **"no effect" and "a real moderate effect" remain indistinguishable**.

This is a credible negative-results and methods contribution. It is not
evidence for a deployable stress-or-performance monitor, and must not be
written up as one.
