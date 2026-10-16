# Review of the failure work on dev, October 2026

Status: draft, 2026-10-16. Findings from comparing scenarios on dev.qmra.org with the
failure work C1–C3 (see `docs/failure_roadmap.md`). Sources of truth: `docs/vision.md`,
`CONTEXT.md`, `docs/adr/`, the specs in `docs/specs/`.

## How findings are sorted

Each finding gets one type:

- **Bug** – the application does not do what the spec or an ADR says. Fixed in the open
  pull request of its Change (C1–C3), with a test first.
- **Decision** – the model or a decision should change. Updates `CONTEXT.md`, an ADR or a
  roadmap decision (D6, …) first; the spec and the pull request follow.
- **UI** – labels, messages, layout or explanations. Goes into C1 or C4.
- **New scope** – not covered by C1–C5. Added to the roadmap as a new Change.

## Scenarios compared

| Scenario | Source water | Treatment steps (failure frequency, duration) | Exposure | Notes |
|----------|--------------|-----------------------------------------------|----------|-------|
| S1       |              |                                               |          |       |

## Findings

### F1 One failure rule for best-case and worst-case

- Type: Decision
- Change: C2 (calculation), C4 (explanations), C5 (benchmark)
- Scenario: –
- Observed: worst-case assumes that all water consumed on a failure day was treated during
  the failure event, so a failing step loses its positive LRVs for the whole exposure event,
  whatever the failure duration (ADR-0001, Consequences; D4). Only best-case uses the
  failure duration, through the mixed-water assumption.
- Expected: best-case and worst-case use the same failure rule, the mixed-water assumption,
  which includes the failure duration. The only difference between the two cases is the LRV
  the failing step starts from: its maximum LRV in best-case and its minimum LRV in
  worst-case, as for normal operation.
- Why it matters: if worst-case assumes the water is always used during the failure, then
  best-case should consistently assume it is never used during the failure. Both cases
  would then be independent of the failure duration, which is not plausible. Instead, the
  failure duration can be read as the probability that the water used on a failure day was
  treated during the failure: the longer the failure, the more likely this is. For an
  average infection risk it therefore makes sense to weight the loss of LRV by the failure
  duration in both cases.
- Next step: settle the open questions below, then record the decision as ADR-0002
  (replacing the worst-case part of ADR-0001) and as roadmap decision D6, and update
  `CONTEXT.md` and the C2 spec.

Answers (2026-10-16):

1. Combined failures: no arrangement within the day. Each treatment step first gets a
   daily average LRV for the failure day, averaged by concentration, with
   d = failure duration / 1440 min:

   $LRV_{day} = -\log_{10}\left(d \cdot 10^{-LRV_{fail}} + (1 - d) \cdot 10^{-LRV}\right)$

   The train LRV of the day is the sum of the steps' daily LRVs. $LRV_{fail}$ is 0 for one
   unit and the F2 formula for more units. This equals placing each failure at a random
   time of day, independently of the other steps. On days with one failing step the
   result equals the current mixed-water rule; with several failing steps it is lower
   than the current best-case. Worked example: `docs/failure-daily-lrv-example.md`.
2. Terms: keep best-case and worst-case; their definitions in `CONTEXT.md` now differ
   only by the maximum or minimum LRV.
3. ADR-0001's reason for the full-day loss in worst-case: dropped for every exposure.

### F2 Number of parallel units as a new failure input

- Type: Decision
- Change: C1 (input), C2 (calculation), C3 (export), C4 (explanations), C5 (benchmark)
- Scenario: –
- Observed: a failing step loses all its positive LRVs (LRV = 0 during the failure).
  `CONTEXT.md` (Treatment failure) says partial loss of removal is "not modelled and not
  planned".
- Expected: a third failure input per treatment step, the **number of parallel units**, a
  whole number of 1 or more, default 1. The water is shared equally between the units. A
  failure event affects only one unit; the other units keep working normally. With *N*
  units, 1/*N* of the water is not treated during the failure and (*N* − 1)/*N* is treated
  with the step's normal LRV. The step's LRV during the failure is therefore

  $LRV_{fail} = -\log_{10}\left(\frac{N-1}{N} \cdot 10^{-LRV_{treatment}} + \frac{1}{N}\right)$

  where $LRV_{treatment}$ is the step's minimum LRV in worst-case and its maximum LRV in
  best-case, for each pathogen group. With the default of 1 unit, $LRV_{fail} = 0$, which
  equals today's rule. Because the formula uses each group's own LRV, the effect differs
  between pathogen groups. This replaces the first version of F2 (one failure reduction
  percentage for all pathogen groups), which was dropped for that reason.
- Why it matters: in most cases the LRV does not drop to 0 during a failure. Often a step
  has several parallel treatment units that do not fail at the same time.
- Next step: settle the open questions below, then record the decision as roadmap decision
  D7 and update `CONTEXT.md` (Treatment failure, Failure event), the C1 and C2 specs and the
  C3 scope.

What the formula gives: the untreated share sets an upper limit of $\log_{10} N$ on the
LRV during a failure, whatever the normal LRV of the step:

| Units *N* | Normal LRV 1 | Normal LRV 2 | Normal LRV 4 | Normal LRV 6 |
|-----------|--------------|--------------|--------------|--------------|
| 1         | 0            | 0            | 0            | 0            |
| 2         | 0.26         | 0.30         | 0.30         | 0.30         |
| 3         | 0.40         | 0.47         | 0.48         | 0.48         |
| 4         | 0.49         | 0.59         | 0.60         | 0.60         |
| 10        | 0.72         | 0.96         | 1.00         | 1.00         |

Answers (2026-10-16):

1. Formula: confirmed. The untreated and the treated shares are mixed by concentration.
2. Upper limit of $\log_{10} N$: intended. A step with 2 units keeps 0.3 log during a
   failure.
3. Range: whole number of 1 or more, no upper limit.
4. Failure frequency: stays the failure days per year of the whole step, any one of its
   units failing.
5. LRVs of 0 or below: stay unchanged during a failure (D4).
6. Non-technical measures: agreed to the proposal below. `CONTEXT.md` names them as a kind of treatment step
   (for example a hygiene practice), but the application does not tell them apart: a
   treatment step has a name, a group and LRVs, and all 22 bundled treatment steps are
   treatment technologies. A non-technical measure can only appear as a personal treatment
   step. Proposed: show the number of parallel units on every treatment step that accepts
   failure inputs (D4), with the default of 1.
7. Personal treatment steps: store the number of parallel units like failure frequency and
   failure duration (C1 ticket 06).

## Decisions taken in this review

- **D6** One daily LRV rule for both cases (F1), recorded in `docs/failure_roadmap.md` and
  ADR-0002.
- **D7** Number of parallel units (F2), recorded in `docs/failure_roadmap.md` and ADR-0002.
- `CONTEXT.md` updated: best-case, worst-case, treatment failure, failure event, failure
  day, failure frequency, failure duration, mixed-water assumption, combined failure; new
  terms parallel units, failure LRV, daily LRV.
- `docs/QMRA_Failure_Approach.md` decisions 1, 3, 4 and 6 marked as changed or replaced;
  ADR-0001 marked as partly superseded.

## Follow-up tickets

| Ticket | Finding | Change | Branch |
|--------|---------|--------|--------|
|        |         |        |        |
