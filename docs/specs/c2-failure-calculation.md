# Spec C2: Failure calculation

Status: draft, 2026-09-24. Change C2 in `docs/failure_roadmap.md` (Large). Spec issue: #___
Sources: `docs/vision.md` (MVP item 3 and 4), `CONTEXT.md`, ADR-0001, the decisions in
`docs/QMRA_Failure_Approach.md`, roadmap decisions D4 and D5. Builds on C1
(`docs/specs/c1-failure-inputs.md`).

## Problem Statement

After C1, users can enter a failure frequency and a failure duration for each treatment
step, but the result ignores them: an assessment with a UV unit failing 10 days per year
gives the same annual probability of infection as one where it never fails. A utility
operator therefore still cannot see how failures of their treatment steps affect the
yearly risk, whether the reference level is still met, or how two failure scenarios
compare.

## Solution

The risk calculation takes treatment failures into account as decided in ADR-0001. In the
Monte Carlo simulation, every simulated exposure event falls on a failure day of each
treatment step with probability failure frequency / 365. On a failure day:

- **worst-case** calculates the event with the failing steps' positive LRVs removed for the
  whole day, whatever the failure duration;
- **best-case** applies the mixed-water assumption: the consumed water is a mixture of water
  treated during the failure events and water treated in normal operation, in proportion to
  the failure durations, with the failure events arranged within the day so that the mixed
  water has the lowest pathogen concentration.

LRVs of 0 or below are never affected (D4). The result page, the reference-level
exceedance, the saved results and the result table in the export package all show the
result including failures, with no change to their layout. An assessment in which every
failure frequency is 0 gives exactly the same results as before C2.

## User Stories

1. As a utility operator, I want the result to include the failures I entered, so that I
   see the yearly risk my plant actually runs.
2. As a utility operator, I want the reference-level exceedance to be judged on the result
   including failures, so that I learn whether failures push a pathogen over the reference
   level.
3. As a utility operator, I want both risk measures (annual probability of infection and
   DALYs per person per year) to include failures, so that I can judge the health burden as
   well as the infection risk.
4. As a user, I want worst-case to assume that all water consumed on a failure day was
   treated during the failure, so that worst-case stays the cautious estimate.
5. As a user, I want best-case to assume mixed water on a failure day, weighted by the
   failure duration, so that best-case reflects storage that dilutes failure water.
6. As a user, I want a longer failure duration to raise the best-case risk and leave the
   worst-case risk unchanged, so that the two cases behave as documented.
7. As a user, I want a higher failure frequency never to lower the risk, so that the results
   make sense when I try different values.
8. As a user, I want worst-case risk never to be below best-case risk, so that the two cases
   keep their meaning with failures.
9. As a user, I want the number of failure days to vary between simulated years, so that
   the risk distribution shows years with more or fewer failures, as real years do.
10. As a user with an exposure of few events per year, I want a low failure frequency to
    show up as an upper tail of the risk distribution, so that I see the rare bad years.
11. As a user with several failing steps, I want failures of different steps on the same
    day to be combined, so that combined failures are not missed.
12. As a user, I want a combined failure in best-case to assume that failure events do not
    overlap when they fit into one day, so that best-case stays the favourable assumption.
13. As a user, I want combined failure events longer than a day in total to overlap only as
    much as necessary, on the steps whose joint loss matters least, so that best-case stays
    favourable without a jump at 24 hours.
14. As a user, I want a failure to remove only the positive LRVs of a step, so that a step
    with regrowth (a negative LRV) in one pathogen group does not improve during a failure.
15. As a user, I want a pathogen group whose LRV at a step is 0 or empty to be unaffected by
    that step's failure, so that failures only matter where the step removes pathogens.
16. As a user, I want every failure frequency at 0 to give exactly the results I got before,
    so that existing assessments and comparisons keep their numbers.
17. As a registered user, I want saved assessments to store the result including failures,
    so that the saved-assessments page and the assessment comparison show it.
18. As a user comparing two saved assessments that differ only in their failure inputs, I
    want the comparison to show different infection risks, so that I see what the failures
    cost.
19. As a registered user, I want the export package's result table to contain the result
    including failures, so that my report matches the result page.
20. As a guest, I want the unsaved result to include failures in the same way, so that the
    result does not depend on having an account.
21. As a user, I want the same assessment to give the same result every time it is
    calculated, so that I can reproduce and discuss a result.
22. As a reviewer, I want the calculation to follow ADR-0001 and the documented decisions,
    so that the result can be checked against an independent calculation (C5).
23. As a user, I want the result page to look as before, so that I do not need to learn a
    new layout.
24. As a user, I want the calculation with failures to finish in about the same time as
    before, so that running an assessment stays quick.
25. As a developer of C5, I want the calculation to be deterministic for a given scenario,
    so that benchmark comparisons are stable.
26. As a developer of C4, I want the calculation's rules to be stated in the Spec in plain
    terms, so that the explanations for users can be written from it.

## Implementation Decisions

- **Only the calculation module changes.** Its public entry point keeps its interface: it
  receives an assessment, its inflow concentrations and its treatment steps, and returns one
  result per reference pathogen. It now reads each treatment step's failure frequency and
  failure duration (stored by C1). The result record, the result page, saving and the export
  are not changed; they show whatever the calculation returns.
- **What a failure removes (D4).** For each treatment step and pathogen group, worst-case
  can lose the step's minimum LRV and best-case its maximum LRV, each only if it is above 0.
  LRVs of 0, below 0 or empty stay in place during a failure.
- **Failure days per exposure event (ADR-0001).** For every simulated exposure event of every
  simulated year, and for every treatment step with failure frequency above 0, the step
  fails that day if a uniform random number is below failure frequency / 365. The same
  random numbers are used for both cases and all reference pathogens. As a consequence,
  raising a failure frequency only ever adds failure days, and worst-case and best-case see
  the same failure days.
- **Worst-case on a failure day.** The event's LRV is the worst-case LRV of the train minus
  the removable minimum LRVs of all steps failing that day. The failure duration is not
  used.
- **Best-case on a failure day (mixed-water assumption).** The day is split into time
  segments by which failing steps are down. The event's LRV is −log₁₀ of the time-weighted
  average of 10^(−LRV of each segment), where a segment's LRV is the best-case LRV of the
  train minus the removable maximum LRVs of the steps down in it. The failure events of the
  day are arranged within 1,440 minutes so that this average concentration is lowest. This
  gives no overlap when the durations fit into one day and otherwise the minimal overlap,
  placed on the steps whose joint loss matters least (`CONTEXT.md`, *Combined failure*). For
  a single failing step it equals Eq. 5 of the failure approach. With the few failing steps
  per day that occur in practice, the arrangement can be found exactly, for example by
  choosing the time share of each combination of failing steps.
- **Concentration sampling unchanged.** The sampled inflow concentrations and the choice of
  which sample each simulated event uses stay exactly as today, including the fixed seed.
  The failure draws come from their own fixed-seed random generator. When all failure
  frequencies are 0, no failure draws are made and the results are identical to today's.
- **Dose and yearly risk.** Each event's dose follows from its sampled concentration, its
  LRV (normal, or reduced as above) and the volume per event, and the yearly risk combines
  the events of a simulated year as today. The summary statistics and the reference-level
  exceedance (on the mean) are computed as today, now from the result including failures.
- **Saved results.** Saving an assessment recalculates and stores its results as today.
  Results stored before C2 stay valid: every assessment in production has failure frequency
  0 at the release, so its stored results equal what C2 calculates.
- **Speed.** When failures are present, the dose-response is evaluated per simulated event
  instead of per concentration sample. The work per failure day depends only on which steps
  fail, so repeated combinations can be reused. The calculation time for a drinking-water
  scenario (365 events per year) with failures is measured on the dev environment and
  recorded in the pull request; the vision sets no response-time target yet.
- **Unchanged warnings.** The warning for a maximum LRV above 6 is not changed.
- **Delivery.** C2 is built on C1's pull request, stays open and is tested on the dev
  environment; it is not merged into `main` before the release (D5).

## Testing Decisions

- **What a good test is.** A test gives the calculation a complete scenario (inflow
  concentrations, treatment steps with failure inputs, exposure) and checks the returned
  results: mean, median, quartiles, minimum and maximum per reference pathogen, for both
  cases and both risk measures, and the reference-level exceedance. It does not inspect
  intermediate arrays or random draws.
- **One seam: the calculation's public entry point**, called the way the existing
  calculation tests call it. The result page, saving and export only pass results through,
  and C1's HTTP tests already show that failure inputs arrive at the calculation. C2 adds no
  HTTP tests.
- **Behaviour covered at that seam** (internal checks; the independent benchmark is C5):
  - **No failures:** with every failure frequency at 0, all results equal today's exactly,
    including the existing regression test's numbers.
  - **Always failing, worst-case:** a step with failure frequency 365 gives the same
    worst-case results as the scenario without that step's positive minimum LRVs.
  - **Always failing, full day, best-case:** failure frequency 365 and duration 1,440 give
    the same best-case results as the scenario without that step's positive maximum LRVs.
  - **Always failing, part of the day, best-case:** failure frequency 365 and duration 60
    give the same best-case results as the scenario with the train's best-case LRV replaced
    by the constant mixed LRV from Eq. 5, computed by hand in the test.
  - **Combined failures:** two steps always failing with 900 + 900 minutes equal the
    hand-computed constant LRV with 360 minutes of overlap; three steps always failing with
    durations above a day in total equal the hand-computed lowest-concentration arrangement.
  - **Monotonicity:** raising a failure frequency never lowers any mean; raising a failure
    duration never lowers a best-case mean and leaves worst-case unchanged.
  - **Case order:** worst-case mean ≥ best-case mean for every pathogen and risk measure,
    with and without failures.
  - **D4:** a step with a negative LRV for one pathogen group and a positive LRV for another
    leaves the first group's results unchanged when it fails; a group with LRV 0 is
    unaffected.
  - **Reproducibility:** calculating the same scenario twice gives identical results.
- **Prior art.** The existing calculation tests: a scenario built from bundled data and
  passed to the calculation, and the regression test comparing fixed numbers.
- **Manual check on the dev environment.** Enter a scenario with failures in the
  configurator, run it as a guest and as a registered user, and confirm the result page,
  the saved-assessments page and the export's result table show the changed results. Record
  the calculation time.
- The existing test suite passes unchanged.

## Acceptance criteria

1. The calculation follows the rules above: failure days per exposure event, worst-case
   full loss, best-case mixed-water assumption with the lowest-concentration arrangement,
   and only positive LRVs lost.
2. With every failure frequency at 0, all results equal today's exactly.
3. All tests listed above pass, and the existing suite passes unchanged.
4. The result page, the reference-level exceedance, saved results, the assessment comparison
   and the export's result table show the result including failures, with unchanged
   layout (manual check on the dev environment).
5. The same scenario gives identical results on every calculation.
6. The calculation time with failures is measured and recorded in the pull request.

Quality goals from `docs/vision.md`, one criterion each:

| Quality goal | Criterion in C2 |
|---|---|
| Scientific correctness | The internal checks pass, including the closed-form cases (always failing steps compared with hand-computed LRVs) and the frequency-0 regression (criteria 2–3). Agreement with an independent calculation is C5. |
| Reproducibility | A scenario gives identical results on every calculation because the failure draws use their own fixed seed, and assessments without failures keep their exact results (criteria 2, 5). |
| Export stability | The export package keeps its files and columns; only the result values of assessments with failures change (criterion 4). |

Not relevant to C2: *Input validity* (C1), *Traceability* (C3), *Privacy of registered-user
data* (no change to access).

## Out of Scope

- Failure inputs, their validation and storage (C1).
- Failure inputs in the export package and the HTML report (C3).
- Explanations for users in the FAQ, guided tour and documentation (C4).
- Comparison with an independent calculation and the benchmark scenarios (C5); the
  tolerance (D1) is not needed here.
- Showing normal operation next to the result with failures (decided against).
- DALYs or inputs in the assessment comparison (later).
- Partial loss of removal (not planned).
- Recording the model version and simulation settings with results (reproducible assessment
  snapshots, later).
- A response-time target (open question in the vision).

## Further Notes

- The rule for arranging three or more failure events of one day in best-case was decided
  on 2026-09-24 while writing this Spec and added to `CONTEXT.md` (*Combined failure*) and
  to decision 6 in `docs/QMRA_Failure_Approach.md`. Overlapping two failure events never
  lowers the mixed concentration, so the lowest-concentration arrangement always has
  minimal overlap and agrees with the rule for two steps.
- No contradiction with ADR-0001 was found. ADR-0001 notes that two exposure events on the
  same calendar day need not share a failure state; this Spec keeps that.
- Results with failures will differ from a hand calculation with Eq. 6 of the failure
  approach, as ADR-0001 explains; they agree on average.
