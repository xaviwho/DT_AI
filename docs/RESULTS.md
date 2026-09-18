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
