# Follow-up study protocol: powering the physiology–performance question

Status: draft for group review, 2026-09-19.
Motivated by `docs/RESULTS.md`. This is the "next" half of the plan — the
"now" half (state detection) is already delivered at AUROC 0.93.

## Why a new study is needed

The one suggestive finding across both corpora is that **EDA reactivity
correlates negatively with within-subject performance** (SCR rate
ρ = −0.441, p = .015 duration-matched). It does not survive Holm
correction across five pre-specified features (p_adj = .074), and the
multivariate model does not generalise out-of-subject.

The reason is power, not absence of effect:

| Corpus | Observed effect | Min detectable (80% power) |
|---|---|---|
| Exam (n=30) | ρ ≈ 0.44 | r = 0.49 |
| Nurse (n=129, 10 clusters) | AUROC 0.544 | AUROC 0.662 |

Both studies are underpowered for the effects they observed. The question
is open, not answered.

## Design

**One-sentence hypothesis (pre-specified, directional).** Within a
student, exam sessions with greater electrodermal reactivity relative to a
duration-matched pre-exam baseline are associated with lower performance
relative to that student's own mean.

This is a *confirmatory* test of a direction already estimated from
independent data — a far stronger design than the exploratory analysis
that produced it.

| Item | Value |
|---|---|
| Participants | **25 students** (target), minimum 20 |
| Sessions | 3 graded exams each (midterm, midterm, final) |
| Observations | 75 (target), 60 (minimum) |
| Device | Empatica E4 or equivalent (EDA 4 Hz, BVP 64 Hz, ACC 32 Hz, TEMP 4 Hz) |
| Primary outcome | Exam score, converted to % |
| Primary predictor | SCR-rate reactivity, exam35 − baseline35 |
| Primary test | Spearman ρ, within-subject centred, one-sided (direction pre-specified) |
| Secondary | Tonic EDA reactivity; LOSO ridge on the 5 pre-specified features |

### Power

Detecting r = 0.40 at 80% power, α = .05 two-sided requires **47
observations**; one-sided, fewer. 75 observations gives comfortable margin
for clustering and dropout, and would also power the weaker r = 0.30 case
(needs 85) at reduced but non-trivial power.

**25 students x 3 exams is a semester-sized study, not a 212-participant
programme.** This is the key practical point: the question is reachable.

## Protocol details that these data showed matter

Each of these is a lesson from `docs/RESULTS.md`, not boilerplate:

1. **Duration-match the windows.** Use a fixed 35 min before and after task
   onset. Unmatched windows produced a spurious EDA effect (dz +0.47 -> +0.15
   under matching) via electrode hydration drift.

2. **Record the task start time directly.** Do not rely on a timetable. The
   Final in the public corpus does not start when its documentation says,
   and no event tag records when it did. Press the device event tag at
   start and end of every session.

3. **Standardise the baseline context.** The baseline in the public data
   included travelling to the exam, so the exam contrast was dominated by
   posture and activity (activity dz = −0.59). Seat participants for the
   full baseline window.

4. **Do not use temperature as a wear gate.** Kleckner's >30 °C criterion
   rejected every Midterm 1 session purely because those rooms were colder.
   Gate on EDA > 0.05 µS and log ambient temperature separately.

5. **Collect a performance measure with within-subject variance.** Grades
   worked: within-subject SD was 7.8 points (median). Two students in the
   public corpus were nearly flat (SD 1.3, 2.3) and contributed almost
   nothing — over-recruit to absorb this.

6. **Pre-register the feature set and the direction.** Five features
   maximum. The multiplicity correction is what the current finding fails.

## Analysis plan (fixed in advance)

- Primary: one-sided Spearman on SCR-rate reactivity vs grade deviation.
- Multiplicity: Holm across the 5 pre-specified features for secondary tests.
- Validation: leave-one-subject-out; report R², permutation p
  (within-subject shuffle), subject-level bootstrap CI.
- Report the null plainly if it is null. The current work is publishable as
  a negative result; so is this.

## Reuse

The entire pipeline already exists and is validated:
`src/data/e4.py`, `src/features/physio.py`, `src/data/exam_state.py`,
`src/eval/state_clf.py`, `src/eval/h1.py`. New data in E4 format drops
straight in.

## Open questions for the group

1. Can we access a course willing to host this? That is the binding
   constraint, not analysis.
2. Ethics/IRB lead time at Kumoh?
3. Device availability — 25 students x 3 sessions needs either 25 units or
   a rotation across exam sittings.
4. Is the state-detection result (AUROC 0.93) written up as its own short
   paper now, or held as part of a combined submission?
