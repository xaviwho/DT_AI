# Physiological state detection in high-demand work — revised plan

**Revised 2026-09-19** after data acquisition and analysis. The original
plan (commit `1d87367`) is superseded; what changed and why is recorded in
§1 so the group can see which assumptions died.

Team: Evans (neuro), Maame Yaa (safety/human factors), Victor (AI/pipeline),
Barry + Calista (comp bio) — **roles revised, see §5**.

---

## 1. What changed from the original plan

| Original assumption | Reality | Source |
|---|---|---|
| Nurse Stress carries the study | Usable n=149 → 129 after filters, 10 nurses; self-report only | `DATASETS.md` |
| Biomarker layer via MMASH cortisol | **2 saliva samples per subject**, 44 values total | `DATASETS.md` |
| H2 forward simulation is the headline | No open corpus has performance trajectories | `DATASETS.md` |
| TILES as primary corpus | DUA ruled out by the group (prior request unanswered) | group decision |
| H1 predicts performance decrement | Not supported out-of-subject in either corpus | `RESULTS.md` |
| DriveDB gives 18 subjects | 14; drive13/14 bit-identical; `marker` unusable | `DATASETS.md` |

**What survived and got stronger:** state detection. AUROC 0.933
[0.885, 0.973], permutation p = .002.

## 2. Current claim set

| Claim | Status | Evidence |
|---|---|---|
| Wrist physiology detects high-demand task episodes | **Supported** | AUROC 0.93, LOSO, p=.002 |
| EDA reactivity tracks within-subject performance | **Suggestive** | ρ=−0.44, p=.015, Holm p=.074 |
| Detector is arousal-based not posture-based | **Not supported** | EDA alone at chance (0.398) |
| Physiology predicts performance out-of-subject | **Not supported** | LOSO R² < 0 |
| Physiology discriminates self-reported stress | **Not supported** | AUROC 0.544, nurses |

## 3. Revised hypotheses

- **H1a (delivered).** Wrist-worn physiology discriminates high-demand task
  episodes from matched pre-task baseline, across held-out subjects.
- **H1b (open, powered by the follow-up).** Within-subject electrodermal
  reactivity is negatively associated with relative performance.
  Directional, pre-specified — see `STUDY_PROTOCOL.md`.
- **H2 (reframed).** No longer an empirical claim. The forward-simulable
  state-space architecture is presented as a **design contribution** with
  H1a as its validated first stage. It is not evidenced and must not be
  written as capability.

## 4. Deliverables

1. **Paper 1 (ready to write).** State detection + the methodological
   findings: duration-matching artifact, activity confounding, EDA-vs-
   temperature wear gating, the two-corpus null. Figures 1–4 exist.
2. **Study protocol** for the confirmatory H1b test (`STUDY_PROTOCOL.md`).
3. **Paper 2 (conditional)** on the follow-up data.

## 5. Revised roles

The biomarker channel is cut — there is no cortisol data to analyse. This
is a data reality, not a judgement on the people.

| Person | Revised ownership |
|---|---|
| Victor | Pipeline, all analysis, Figs 1–4, Methods |
| Evans | Interpretation of the cardiac/motor vs arousal distinction; why EDA fails here; Discussion |
| Maame Yaa | Translation section: what episode-level detection is and is not good for in safety-critical work; Introduction |
| Barry / Calista | **Reassigned** — own the follow-up study: protocol, IRB, recruitment, device logistics (`STUDY_PROTOCOL.md` §"Open questions") |
| All | Review, pre-registration sign-off |

Rule retained from the original plan: every author owns a figure, a table,
or a named deliverable.

## 6. Venues (revised)

Paper 1 is a methods-and-negative-results contribution, not a performance
monitor. Ordered by fit:

1. *Sensors* — good home for wearable methodology plus honest nulls
2. *IEEE JBHI* — as a short methods note
3. *PLOS One* — sound-science venue, no novelty bar
4. *Behavior Research Methods* — if the artifact findings lead

Dropped: *npj Digital Medicine* (required the biomarker layer);
*IEEE THMS* (required the H2 policy layer).

## 7. Open decisions for the group

1. Publish the state-detection result now as a standalone short paper, or
   hold it for a combined submission with the follow-up? (Recommendation:
   publish now — it stands alone and is not contingent.)
2. Is a course available to host the follow-up? **This is the binding
   constraint on H1b, not analysis.**
3. IRB lead time at Kumoh, and device availability for 25 participants.
4. Confirm the role reassignment in §5.

## 8. What is already reproducible

    python -m src.data.exam_stress        # exam feature table
    python -m src.data.exam_state         # duration-matched windows
    python -m src.data.nurse              # nurse feature table
    python -m src.eval.make_figures       # Figs 1-2
    python -m src.eval.make_figures_nurse # Fig 3
    python -m src.eval.make_figures_state # Fig 4
