# AI-Driven Digital Twin for Stress, Decision-Making, and Error Risk in High-Risk Work

Working title (tightened from the group proposal):
**"A physiological digital twin for predicting acute cognitive-performance decrement in high-risk occupational work"**

Team: Evans (neuro), Maame Yaa (safety/human factors), Victor (AI/digital twin),
Barry + Calista (comp bio / biomarkers).

---

## 1. The problem with the proposal as written

"Digital twin of a worker under stress" is a framing, not a hypothesis. Five
contributors each adding a discipline to one narrative tends to produce a
review paper. To publish an empirical result we need **one falsifiable
prediction target measurable in one dataset**, with the other disciplines
supplying features, priors, and interpretation.

## 2. Proposed testable core

**H1.** A latent state model (arousal, fatigue, cognitive load) inferred from
wearable physiology predicts near-term decrement in task performance
(reaction time / error rate) better than (a) raw physiological features and
(b) time-on-task alone.

**H2 (twin claim).** The same fitted latent model, run forward as a
simulator, reproduces held-out subjects' performance trajectories under
unseen stressor schedules — i.e. it is a *twin*, not just a classifier.

H2 is what earns the "digital twin" word. Without it, reviewers will call
this stress classification, which is a saturated literature.

## 3. Architecture (three layers, mapped to people)

    Layer 3  Risk / decision      RL or POMDP policy: when to rotate, rest,   -> Evans
             (action selection)   or reassign a worker given twin state
                  ^
    Layer 2  Latent state twin    State-space model (fatigue, arousal, load)  -> Victor
                  ^               fitted per-subject, forward-simulable
    Layer 1  Observation model    HRV, EDA, ACC, temp, skin conductance       -> Barry/Calista
                                  + salivary cortisol/alpha-amylase where
                                  available

    Context / labels             Task demand, shift, incident taxonomy        -> Maame Yaa

Concretely for Layer 2: start with a **switching linear dynamical system** or
a **latent ODE / neural state-space model**. Both are forward-simulable
(needed for H2) and interpretable enough for a health audience. Do not start
with a black-box LSTM classifier — it cannot support H2.

## 4. Datasets that actually exist and are downloadable

Ranked by fit. All are public; none require IRB for secondary analysis, but
check each license.

| Dataset | What it gives | Fit |
|---|---|---|
| **Nurse Stress (Hosseini et al. 2022, Dryad)** | Empatica E4 (EDA, HRV, temp, ACC) on nurses during real hospital shifts, with self-reported stress events | **Best.** Real occupational stress, real shift structure. Closest to the target population. |
| **WESAD (UCI)** | 15 subjects, chest+wrist, baseline/stress/amusement, TSST protocol | Best for validating the observation model; lab-controlled, well-benchmarked |
| **MMASH (PhysioNet)** | 24h actigraphy, HRV, sleep, **salivary cortisol + melatonin**, psych questionnaires | The biomarker bridge for Barry/Calista. Links physiology to endocrine markers |
| **DriveDB / Stress Recognition in Automobile Drivers (PhysioNet)** | ECG, EMG, EDA during real driving with graded stress | Good second cohort for generalization tests |
| **EEGMAT (PhysioNet)** | EEG during mental arithmetic under time pressure | Only if Evans wants a neural (not just autonomic) channel |
| **OSHA Severe Injury Reports + NIOSH FACE reports** | Incident narratives, construction/disaster context | Maame Yaa's layer: taxonomy of error modes, and the *justification* for which outcomes matter. Not a modeling dataset — narrative text |
| **SWELL-KW** | Knowledge work under stressors, physiology + performance | Has explicit task-performance labels, useful for H1 |

**The honest gap:** no public dataset has (physiology + performance + real
disaster/construction incidents) in one place. Options:

1. Model on nurse/driver data, frame construction/disaster as the
   *translation target* — argue transfer, don't claim it.
2. Add a small in-house VR or simulated-task study (PVT + stressor) to close
   the loop. This is the highest-value original contribution if any of you
   can run 20-30 participants.
3. Use OSHA narratives only for an error taxonomy that defines the outcome
   variable. Legitimate, but it's a framing contribution.

Option 1 is the fastest publishable path. Option 2 is what turns this into a
grant.

## 5. Role assignment (concrete, not thematic)

| Person | Owns | Deliverable |
|---|---|---|
| Victor | Layers 1-2, pipeline, all code | Fitted twin, held-out simulation results, repo |
| Evans | Layer 3 + neuro framing | RL/POMDP policy, priors on the latent structure, Intro + Discussion |
| Maame Yaa | Outcome definition, human-factors framing | Error taxonomy from OSHA/FACE, translation section |
| Barry / Calista | Biomarker channel | Cortisol/amylase analysis on MMASH; feasibility note on saliva sampling in field |
| Rotating | Lit review, writing | Shared |

Rule: every author owns a figure or a table. If someone doesn't, they are an
acknowledgement, not an author.

## 6. Milestones

- **W1-2** Dataset access + licenses; agree the outcome variable
- **W3-4** Layer 1 reproduction: match published WESAD stress-detection baselines. If we can't reproduce known results, stop and fix the pipeline
- **W5-8** Layer 2 fit on nurse data; H1 test vs. two baselines
- **W9-10** H2 test: forward simulation on held-out subjects
- **W11-12** Layer 3 policy; ablations
- **W13-16** Writing

## 7. Target venues

Ordered by realistic fit for the H1+H2 result:

1. *IEEE Journal of Biomedical and Health Informatics* — best match for wearable + state-space
2. *IEEE Trans. Human-Machine Systems* — if Layer 3 is strong
3. *Safety Science* / *Automation in Construction* — if the construction translation is real, not aspirational
4. *npj Digital Medicine* — needs the biomarker layer to be substantive
5. *Scientific Reports* / *PLOS One* — fallback, sound-science venues
6. *Frontiers in AI* — viable but weakest signal

## 8. Funding hooks (as framed in the group note)

Occupational health (NIOSH), military human performance (ARL/DEVCOM), UN
disaster agencies. All of these want the H2 forward-simulation claim, not a
classifier. Design for it from day one.

## 9. Open decisions for the group

1. Outcome variable: reaction time, error rate, or self-reported stress?
   (Self-report is weakest; reviewers will push back.)
2. Are we collecting new data, or purely secondary analysis?
3. Is the biomarker layer in scope for paper 1, or paper 2?
4. Who is corresponding author?
