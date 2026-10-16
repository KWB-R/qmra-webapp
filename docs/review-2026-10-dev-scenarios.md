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

Open questions:

1. Combined failures: under the mixed-water assumption the failure events are arranged so
   that the mixed water has the *lowest* pathogen concentration. Should worst-case use the
   same arrangement, or the arrangement with the *highest* concentration (as much overlap as
   possible)?
2. Terms: "worst-case" in `CONTEXT.md` is defined partly by the failure rule, and the
   mixed-water assumption is called a best-case assumption. Both definitions need rewording.
   Do the names best-case and worst-case stay?
3. ADR-0001's reason for ignoring the duration in worst-case (the water of one exposure
   event was treated during the downtime) is dropped. Is there any exposure for which it
   should still apply?

### F2 Failure reduction as a new failure input

- Type: Decision
- Change: C1 (input), C2 (calculation), C3 (export), C4 (explanations), C5 (benchmark)
- Scenario: –
- Observed: a failing step loses all its positive LRVs (LRV = 0 during the failure).
  `CONTEXT.md` (Treatment failure) says partial loss of removal is "not modelled and not
  planned".
- Expected: a third failure input per treatment step, the **failure reduction**: an integer
  percentage from 0 (no loss of LRV) to 100 (LRV drops to 0), default 100. During a failure
  the step's LRV is

  $LRV_{fail} = LRV_{treatment} \times (1 - reduction)$

  where $LRV_{treatment}$ is the step's minimum LRV in worst-case and its maximum LRV in
  best-case, and $reduction$ is the failure reduction as a fraction (for example 60 % →
  0.6). With the default of 100 % the result equals today's rule.
- Why it matters: in most cases the LRV does not drop to 0 during a failure. Often a step
  has several parallel treatment lines that do not fail at the same time.
- Next step: settle the open questions below, then record the decision as roadmap decision
  D7 and update `CONTEXT.md` (Treatment failure), the C1 and C2 specs and the C3 scope.

Open questions:

1. Formula: the notes give $LRV_{treatment} - LRV_{} \times reduction$. Is the reading
   above, $LRV_{treatment} \times (1 - reduction)$, correct?
2. Scope of the reduction: one value per treatment step for all pathogen groups, or one per
   pathogen group?
3. LRVs of 0 or below: they stay unchanged during a failure, as today (D4)?
4. Should a step with failure reduction 0 % still accept a failure frequency, or should the
   configurator treat it as "no failure"?
5. Personal treatment steps store the failure reduction too, like failure frequency and
   failure duration (C1 ticket 06)?

## Decisions taken in this review

None yet.

## Follow-up tickets

| Ticket | Finding | Change | Branch |
|--------|---------|--------|--------|
|        |         |        |        |
