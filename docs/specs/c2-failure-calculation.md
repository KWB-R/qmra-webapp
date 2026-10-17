# Spec C2: Failure calculation

Status: draft, 2026-09-24, revised 2026-10-17 for D6 (one daily LRV rule for both cases)
and D7 (number of parallel units). Change C2 in `docs/failure_roadmap.md` (Large). Spec
issue: #___
Sources: `docs/vision.md` (MVP item 3 and 4), `CONTEXT.md`, ADR-0001, ADR-0002, the
decisions in `docs/QMRA_Failure_Approach.md`, roadmap decisions D4–D7. Builds on C1
(`docs/specs/c1-failure-inputs.md`, revised for D7). Worked example:
`docs/failure-daily-lrv-example.md`.

The first version is built and was tested on the dev environment (tickets 07–09). It drew
failure days per exposure event, lost a failing step's positive minimum LRVs for the whole
day in worst-case, and applied the mixed-water assumption with overlap rules in best-case.
This revision keeps the failure-day draws and replaces the rule for the LRV on a failure
day: both cases now use the daily LRV of each failing step, and a step with several
parallel units loses only the share of the failing unit (ADR-0002). Requirements that are
new or changed in this revision are marked *(D6)* or *(D7)*.

## Problem Statement

After C1, users enter a failure frequency, a failure duration and a number of parallel
units for each treatment step. A utility operator wants the result to show how these
failures affect the yearly risk, whether the reference level is still met, and how two
failure scenarios compare.

The first version of C2 answers this with two different rules. Worst-case ignores the
failure duration, so a one-minute and a full-day failure give the same worst-case risk.
Best-case needs special overlap rules for failures of several steps on one day. Neither
case knows parallel units, so every failure is counted as a complete loss of the step's
positive LRVs, although a step often has several units that do not fail at the same time.
The review on dev in October 2026 found these results implausible (findings F1 and F2 in
`docs/review-2026-10-dev-scenarios.md`).

## Solution

The risk calculation takes treatment failures into account as decided in ADR-0001 and
ADR-0002. In the Monte Carlo simulation, every simulated exposure event falls on a failure
day of each treatment step with probability failure frequency / 365 (ADR-0001, unchanged).
On a failure day, best-case and worst-case use the same rule *(D6)*:

- each failing step gets a **daily LRV**: the water consumed that day is a mixture of water
  treated during the failure event and water treated in normal operation, in proportion to
  the failure duration (the mixed-water assumption), averaged by concentration;
- during the failure event the step has its **failure LRV**: with N parallel units, one
  unit stops and the others keep working, so 1/N of the water is not treated *(D7)*. With
  one unit the failure LRV is 0;
- the treatment train's LRV that day is the sum of the failing steps' daily LRVs and the
  other steps' normal LRVs, so combined failures need no overlap rules *(D6)*;
- the only difference between the two cases is the LRV each step starts from: its maximum
  LRV in best-case and its minimum LRV in worst-case.

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
4. As a user, I want best-case and worst-case to use the same failure rule, so that the
   difference between the two cases comes only from the minimum and maximum LRVs. *(D6)*
5. As a user, I want the failure duration to count in both cases, so that a one-minute
   failure and a full-day failure give different results in worst-case too. *(D6)*
6. As a user, I want a longer failure duration never to lower the risk, in either case, so
   that the results make sense when I try different values. *(D6)*
7. As a user, I want a failure lasting the whole day (1,440 minutes) of a step with one
   unit to remove that step's positive LRVs for the day, so that the extreme case matches
   the obvious expectation. *(D6)*
8. As a user, I want a step with several parallel units to lose only the share of the
   failing unit, so that a failure of one of four filters is not counted as a failure of
   all four. *(D7)*
9. As a user, I want the LRV of a step during a failure to follow from the share of
   untreated water, so that two units keep about 0.3 log and ten units about 1 log during a
   failure, whatever the step's normal LRV. *(D7)*
10. As a user, I want more parallel units never to raise the risk, so that describing my
    plant more precisely never makes it look worse. *(D7)*
11. As a user, I want a step with one parallel unit to lose all its positive LRVs during the
    failure, so that the default behaves as before. *(D7)*
12. As a user, I want a higher failure frequency never to lower the risk, so that the
    results make sense when I try different values.
13. As a user, I want worst-case risk never to be below best-case risk, so that the two
    cases keep their meaning with failures.
14. As a user, I want the number of failure days to vary between simulated years, so that
    the risk distribution shows years with more or fewer failures, as real years do.
15. As a user with an exposure of few events per year, I want a low failure frequency to
    show up as an upper tail of the risk distribution, so that I see the rare bad years.
16. As a user with several failing steps, I want failures of different steps on the same
    day to be combined, so that combined failures are not missed.
17. As a user, I want combined failures to be calculated as if each failure event happened
    at a random time of day, independently of the others, so that the result is neither
    the most favourable nor the least favourable arrangement. *(D6)*
18. As a user, I want two steps failing on the same day for a long time each to be
    calculated without a special rule for durations that add up to more than a day, so
    that there is no jump in the result at 24 hours. *(D6)*
19. As a user, I want a failure to remove only the positive LRVs of a step, so that a step
    with regrowth (a negative LRV) in one pathogen group does not improve during a failure.
20. As a user, I want a pathogen group whose LRV at a step is 0 or empty to be unaffected by
    that step's failure, so that failures only matter where the step removes pathogens.
21. As a user, I want a step with a minimum LRV of 0 and a positive maximum LRV to affect
    only best-case when it fails, so that each case loses only what it counted.
22. As a user, I want every failure frequency at 0 to give exactly the results I got before,
    so that existing assessments and comparisons keep their numbers.
23. As a registered user, I want saved assessments to store the result including failures,
    so that the saved-assessments page and the assessment comparison show it.
24. As a user comparing two saved assessments that differ only in their failure inputs, for
    example only in the number of parallel units, I want the comparison to show different
    infection risks, so that I see what the failures cost.
25. As a registered user, I want the export package's result table to contain the result
    including failures, so that my report matches the result page.
26. As a guest, I want the unsaved result to include failures in the same way, so that the
    result does not depend on having an account.
27. As a user, I want the same assessment to give the same result every time it is
    calculated, so that I can reproduce and discuss a result.
28. As a reviewer, I want the calculation to follow ADR-0001, ADR-0002 and the worked
    example, so that the result can be checked against an independent calculation (C5).
29. As a user, I want the result page to look as before, so that I do not need to learn a
    new layout.
30. As a user, I want the calculation with failures to finish in about the same time as
    before, so that running an assessment stays quick.
31. As a developer of C5, I want the calculation to be deterministic for a given scenario,
    so that benchmark comparisons are stable.
32. As a developer of C4, I want the calculation's rules to be stated in the Spec in plain
    terms, so that the explanations for users can be written from it.

## Implementation Decisions

- **Only the calculation module changes.** Its public entry point keeps its interface: it
  receives an assessment, its inflow concentrations and its treatment steps, and returns one
  result per reference pathogen. It reads each treatment step's failure frequency, failure
  duration and number of parallel units (stored by C1). The result record, the result page,
  saving and the export are not changed; they show whatever the calculation returns.
- **What a failure can affect (D4).** For each treatment step and pathogen group, worst-case
  starts from the step's minimum LRV and best-case from its maximum LRV. Only an LRV above
  0 is affected by a failure; LRVs of 0, below 0 or empty stay in place.
- **Failure days per exposure event (ADR-0001, unchanged).** For every simulated exposure
  event of every simulated year, and for every treatment step with failure frequency above
  0, the step fails that day if a uniform random number is below failure frequency / 365.
  The same random numbers are used for both cases and all reference pathogens. Each step
  draws from its own stream, keyed by its position in the train, from a fixed seed. As a
  consequence, raising a failure frequency only ever adds failure days, and worst-case and
  best-case see the same failure days.
- **Failure LRV of a step (D7, ADR-0002).** For a positive LRV of a step with N parallel
  units, the failure LRV is −log₁₀((N − 1)/N · 10^(−LRV) + 1/N): the untreated and the
  treated water are mixed by concentration. It is 0 for one unit and at most log₁₀ N.
- **Daily LRV of a failing step (D6, ADR-0002).** With d = failure duration / 1,440, the
  daily LRV is −log₁₀(d · 10^(−failure LRV) + (1 − d) · 10^(−LRV)), averaged by
  concentration, never by LRV. LRV is the step's maximum LRV in best-case and its minimum
  LRV in worst-case.
- **LRV of an exposure event on a failure day (D6).** The event's LRV is the case's LRV of
  the train minus, for every step failing that day, the difference between that step's LRV
  and its daily LRV. The two cases use the same rule. Combined failures need no further
  rule: summing the steps' daily LRVs equals placing each failure event at a random time of
  day, independently of the other steps.
- **Rules that are removed (D6).** The worst-case loss of the failing steps' positive
  minimum LRVs for the whole day regardless of the duration, the best-case arrangement of
  combined failures without overlap, the overlap by the minutes beyond a day, and the rule
  that three or more steps longer than a day in total count like worst-case.
- **Concentration sampling unchanged.** The sampled inflow concentrations and the choice of
  which sample each simulated event uses stay exactly as today, including the fixed seed.
  When all failure frequencies are 0, no failure draws are made and the results are
  identical to today's.
- **Dose and yearly risk.** Each event's dose follows from its sampled concentration, its
  LRV (normal, or reduced as above) and the volume per event, and the yearly risk combines
  the events of a simulated year as today. The summary statistics and the reference-level
  exceedance (on the mean) are computed as today, now from the result including failures.
- **Saved results.** Saving an assessment recalculates and stores its results as today.
  Results stored before C2 stay valid: every assessment in production has failure frequency
  0 at the release, so its stored results equal what C2 calculates.
- **Speed.** The dose-response is evaluated once per distinct event LRV and concentration
  sample, as in the first version. Each failing step contributes one fixed LRV difference
  per case and pathogen group, so the number of distinct event LRVs is bounded by the
  combinations of failing steps. The calculation time for a drinking-water scenario (365
  events per year) with failures is measured and recorded in the pull request; the first
  version took 0.13–0.19 s locally against 0.07 s without failures. The vision sets no
  response-time target yet.
- **Unchanged warnings.** The warning for a maximum LRV above 6 is not changed.
- **Delivery.** The rework is done in new tickets on the existing C2 pull request (#29),
  which builds on C1's pull request (roadmap decision "Rework of C1–C3"). Tickets 08 and 09
  get a note naming the tickets that partly replace them. C2 stays open and is tested on the
  dev environment again; it is not merged into `main` before the release (D5).

## Testing Decisions

- **What a good test is.** A test gives the calculation a complete scenario (inflow
  concentrations, treatment steps with failure inputs, exposure) and checks the returned
  results: mean, median, quartiles, minimum and maximum per reference pathogen, for both
  cases and both risk measures, and the reference-level exceedance. It does not inspect
  intermediate arrays or random draws. Expected values come from an independent source:
  the results of a scenario without failures that has the expected constant LRV, the
  worked example, or the failure LRV table of D7; never from the formula the code uses.
  The worked example and the D7 table give LRVs rounded to two decimals, so comparisons
  with them allow for that rounding.
- **One seam: the calculation's public entry point**, called the way the existing
  calculation tests call it. The result page, saving and export only pass results through,
  and C1's HTTP tests show that the three failure inputs arrive at the calculation. C2 adds
  no HTTP tests.
- **Behaviour covered at that seam** (internal checks; the independent benchmark is C5):
  - **No failures:** with every failure frequency at 0, all results equal today's exactly,
    including the existing regression test's numbers.
  - **Always failing, full day, one unit** *(D6)*: a step with failure frequency 365,
    duration 1,440 and one unit gives the same results in both cases as the scenario
    without that step's positive LRVs (daily LRV 0).
  - **Always failing, part of the day** *(D6)*: failure frequency 365 and duration 60 give,
    in both cases, the same results as a scenario whose train has the hand-computed constant
    daily LRV; for the worked example's step with LRV 4 next to a step with LRV 3, the train
    LRV of the day is 4.38.
  - **Combined failures, worked example** *(D6)*: two steps with LRV 4 and 3, both always
    failing for 60 minutes with one unit, give the same results as a train with constant
    LRV 2.75; for 4 h, 12 h and 16 h each, 1.55, 0.60 and 0.35. These values come from
    `docs/failure-daily-lrv-example.md`.
  - **Average by concentration** *(D6)*: in the 60-minute combined case the result differs
    clearly from a train with the plain LRV average of 6.71.
  - **Parallel units** *(D7)*: a step with LRV 4 always failing for the whole day with 2,
    4 or 10 units gives the same results as a train in which that step has LRV 0.30, 0.60
    or 1.00 (the D7 table); with one unit, LRV 0.
  - **Monotonicity:** raising a failure frequency never lowers any mean; raising a failure
    duration never lowers any mean, in either case *(D6)*; raising the number of parallel
    units never raises any mean *(D7)*.
  - **Case order:** worst-case mean ≥ best-case mean for every pathogen and risk measure,
    with and without failures.
  - **D4:** a step with a negative LRV for one pathogen group and a positive LRV for another
    leaves the first group's results unchanged when it fails; a group with LRV 0 is
    unaffected; a step with minimum LRV 0 and a positive maximum LRV changes only
    best-case when it fails.
  - **Reproducibility:** calculating the same scenario twice gives identical results.
- **Tests of the first version that change.** The worst-case tests for a full-day loss
  regardless of the duration, and for the duration not changing worst-case, are replaced
  by the full-day and monotonicity checks above. The best-case tests for overlap beyond a
  day, three steps within a day, three steps over a day counting like worst-case and three
  steps crossing a day are removed with their rules.
- **Prior art.** The existing calculation tests: a scenario built from bundled data and
  passed to the calculation, the regression test comparing fixed numbers, and the C2 tests
  that compare an always-failing scenario with a scenario of constant LRV.
- **Export.** C1's HTTP test that the export package keeps its files and columns with
  failures, and the reference export test of C3, keep passing; only result values of
  assessments with failures change.
- **Manual check on the dev environment.** Enter the worked example's two steps with
  failures in the configurator, run it as a guest and as a registered user, change the
  failure duration and the number of parallel units, and confirm that both cases react and
  that the result page, the saved-assessments page and the export's result table show the
  changed results. Record the calculation time.
- The existing test suite passes, apart from the first-version tests named above.

## Acceptance criteria

1. The calculation follows the rules above: failure days per exposure event, the failure
   LRV from the number of parallel units, the daily LRV of each failing step in both cases,
   summed over the train, and only positive LRVs affected.
2. With every failure frequency at 0, all results equal today's exactly.
3. The results match the worked example and the D7 failure LRV table in the tests listed
   above, and all other listed tests pass.
4. The result page, the reference-level exceedance, saved results, the assessment comparison
   and the export's result table show the result including failures, with unchanged
   layout (manual check on the dev environment).
5. The same scenario gives identical results on every calculation.
6. The calculation time with failures is measured and recorded in the pull request.

Quality goals from `docs/vision.md`, one criterion each:

| Quality goal | Criterion in C2 |
|---|---|
| Scientific correctness | The internal checks pass, with expected values from the worked example and the D7 table rather than from the code, and the frequency-0 regression holds (criteria 2–3). Agreement with an independent calculation is C5. |
| Reproducibility | A scenario gives identical results on every calculation because the failure draws use their own fixed seed, and assessments without failures keep their exact results (criteria 2, 5). |
| Export stability | The export package keeps its files and columns; only the result values of assessments with failures change (criterion 4). |

Not relevant to C2: *Input validity* (C1), *Traceability* (C3), *Privacy of registered-user
data* (no change to access).

## Out of Scope

- Failure inputs, their validation and storage, including the number of parallel units
  (C1).
- Failure inputs in the export package, including a column for the number of parallel
  units (C3).
- Explanations for users in the FAQ, guided tour and documentation (C4).
- Comparison with an independent calculation and the benchmark scenarios (C5); the
  tolerance (D1) is not needed here.
- A draw per exposure event of whether it falls inside the failure event, instead of the
  average concentration (ADR-0002, Consequences).
- Units of one step that fail together, and a failure frequency per unit (D7).
- Showing normal operation next to the result with failures (decided against).
- DALYs or inputs in the assessment comparison (later).
- Recording the model version and simulation settings with results (reproducible assessment
  snapshots, later).
- A response-time target (open question in the vision).

## Further Notes

- No contradiction with an accepted ADR was found. ADR-0002 replaces ADR-0001's rule for the
  LRV on a failure day; the per-event draw of failure days and the note that two exposure
  events on the same calendar day need not share a failure state stay.
- With the default failure duration of 30 minutes, worst-case results with failures are
  much less conservative than in the first version (ADR-0002, Consequences). This is
  intended; C4 explains that the duration affects both cases.
- Results with failures still differ from a hand calculation with Eq. 6 of the failure
  approach, as ADR-0001 explains, and now also in worst-case, which the source calculates
  without the duration (ADR-0002).
- Assessments saved on the dev environment with the first version keep their stored
  results until they are saved again. Production has no assessments with failures.
