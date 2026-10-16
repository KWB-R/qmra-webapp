# Failure roadmap

Status: draft, 2026-09-24, revised 2026-10-16 (D6, D7). Overview of the Changes that deliver the MVP in `docs/vision.md`:
treatment failure, including combined failures. Sources of truth: `docs/vision.md`,
`CONTEXT.md`, `docs/adr/`. Each Large change gets a Spec (`/to-spec`); Small changes are
built directly. Changes are refined into tickets later. All Changes start from `main`.

## Changes

### C1 Failure inputs — Large

Spec issue: #___ (draft: `docs/specs/c1-failure-inputs.md`)

Purpose: users can enter a failure frequency, a failure duration and a number of parallel
units for each treatment step, and they are stored with the scenario.

Scope: failure frequency (failure days per year, 0–365, default 0) and failure duration
(minutes, 1–1440, default 30) and number of parallel units (whole number of 1 or more,
default 1, D7) on each treatment step of an assessment and on personal
treatment steps; configurator fields with units and validation, the number of parallel
units always shown next to the other two; only treatment steps with
at least one positive LRV accept failure inputs (D4); values of a personal treatment step are
carried into the assessment; saving, reopening and editing keep them. Existing saved
assessments get failure frequency 0 and 1 parallel unit, so their results are unchanged.

Reopened by D7 (2026-10-16): the number of parallel units is added in new tickets on the
existing C1 pull request.

Not included: any effect on the calculation (C2), the export (C3), explanations
beyond field labels and units (C4).

### C2 Failure calculation — Large

Spec issue: #___ (draft: `docs/specs/c2-failure-calculation.md`)

Purpose: results include treatment failures as decided in ADR-0001 and ADR-0002.

Scope: failure days drawn per exposure event and per treatment step inside the Monte Carlo
simulation; best-case and worst-case both use the daily LRV of each failing step, starting
from its maximum or minimum LRV (D6); the failure LRV follows from the number of parallel
units (D7); a failure removes only positive LRVs, LRVs of 0 or below stay (D4); combined
failures sum the steps' daily LRVs, without overlap rules (D6); the result page
and the reference-level exceedance show the result including failures. With every failure
frequency at 0, results equal today's. Tested with checks that need no external expected
values: failure frequency 0 reproduces today's results exactly, worst-case risk is never
below best-case, a higher failure frequency never lowers the risk, LRVs of 0 or below are
unaffected, one parallel unit gives a failure LRV of 0, more parallel units never
lower the result's LRV, a longer failure duration never lowers the risk, one unit with a
failure duration of 1440 minutes gives a daily LRV of 0, the daily LRV matches the worked
example in `docs/failure-daily-lrv-example.md` (4.38 for one failing step, 2.75 for two),
and the daily LRV is averaged by concentration, never by LRV.

Reopened by D6 and D7 (2026-10-16): the daily LRV and the failure LRV replace the
worst-case full-day loss and the overlap rules, in new tickets on the existing C2 pull
request.

Not included: the comparison with an independent calculation (C5), showing normal
operation next to the result with failures (decided against), DALYs in the assessment
comparison (later).

### C3 Failure inputs in the export — Small

The export package's treatment table shows each treatment step's failure frequency,
failure duration and number of parallel units, so a reader can see which failures a result
is based on. Left out: the HTML report, which shows no inputs at all and so doesn't show
failure inputs either (decided 2026-09-25); renaming export files (`inflows.csv` →
`inflow_concentration.csv` waits until later); origin and reference columns for inputs;
changes to the assessment comparison.

Reopened by D7 (2026-10-16): the number of parallel units column is added in a new ticket
on the existing C3 pull request.

### C4 Explain treatment failure — Small

The FAQ, the configurator guided tour and the Sphinx documentation (`docs/source/`) explain
failure frequency, failure duration and parallel units, failure days, the failure LRV, the
daily LRV under the mixed-water assumption and combined failures. They also say that the
failure duration affects both best-case and worst-case, and that a step whose units can
fail together (for example through a shared power supply) is entered with one unit. Left
out: field labels and
units (C1), rewording the deferred UI terms such as "tolerable risk level", and
explanations of unrelated parts of the model.

### C5 Failure benchmark — Small

A small set of benchmark scenarios with failures is stored in the repository: a single
failing step, a combined failure, a failure duration of 1440 minutes, a combined failure
with a step that has several parallel units, an exposure with few events per year, and a step with a negative LRV in one pathogen group.
A domain expert calculates their expected results with an independent Monte Carlo script
(for example in R) that implements the documented method (`CONTEXT.md`, the decisions in
`docs/QMRA_Failure_Approach.md`, ADR-0001, ADR-0002) without using the application's code, and
regression tests compare the application's results with them within the agreed tolerance
(D1, D2). The tests then run on every later change. Left out: benchmarks for parts of the
model unrelated to failures, and the reproducibility records named in the vision's quality
goals.

## Dependencies

- C2 depends on C1 (it reads the stored failure inputs).
- C3 depends on C1.
- C4 depends on C2 (it explains the calculation's behaviour) and on C1.
- C5 depends on C2 (it checks the implemented calculation).
- Release depends on C1–C5: users must never see failure inputs without effect, results
  they cannot trace, or results not checked against an independent calculation. Because
  every merge into `main` deploys to production without approval (`docs/environments.md`),
  merging any of C1–C5 into `main` before the release is not allowed (D5). Each Change stays an open pull
  request, built on the pull request it depends on, and is tested on the dev environment.

## Parallel work

- The Specs of C1 and C2 can be written in parallel; both rest on `CONTEXT.md`, ADR-0001
  and ADR-0002.
- Once C1 is done, C2 and C3 can be built in parallel, both on top of C1's pull request.
- C4 can be drafted while C2 is being built and finished once C2 is done.
- The benchmark scenarios of C5 and their expected values (D2) can be prepared while C2 is
  being built; only the comparison tests need C2 done.
- C4 and C5 can be built in parallel.

## Sequence

1. `/to-spec` C1 and C2 (in parallel).
2. `/implement` C1.
3. `/implement` C2; build C3 in parallel.
4. Rework for D6 and D7 (added 2026-10-16), after the review of C1–C3 on dev:
    1. Update the C1 and C2 specs.
    2. Write tickets 14 and up; tickets 04–11 stay as built, and tickets 08 and 09 get a
       note naming the tickets that partly replace them.
    3. Rework C1 (number of parallel units: input, storage, personal treatment steps).
    4. Rework C2 (daily LRV, failure LRV) and C3 (number of parallel units column) in
       parallel.
    5. Test C1–C3 on the dev environment again.
5. Build C4 and C5 once C2 is done.
5. Release: once C1–C5 are done and tested together on the dev environment and D3 is
   settled, merge all five pull requests into `main` together. That deploys them to
   production.

"Done" means the pull request is reviewed and tested on the dev environment, but not merged.
The dev environment shows only the pull request pushed last, so testing there is announced
to the team first. Each open pull request is kept up to date with `main` to limit
conflicts at the release.

## Unresolved decisions

| # | Decision | Owner | Depends on | Blocks |
|---|---|---|---|---|
| D1 | Tolerance for matching benchmark scenarios. With an independent Monte Carlo script (D2), differences are only sampling noise or real errors | Wolfgang, Malte | — | C5 |
| D2 | Who calculates the expected values; ideally not the author of C2 | Wolfgang, Malte | — | C5 |
| D3 | Which one or two domain experts sign off the C5 benchmark comparison | Wolfgang, Malte | — | Release |

## Resolved decisions

- **D4 (2026-09-24).** A treatment step accepts failure inputs if at least one of its LRVs
  is positive. A failure removes only the positive LRVs; LRVs of 0 or below, such as
  regrowth in one pathogen group, are not affected.
- **Implement before benchmarking (2026-09-24).** C2 is built and tested with internal
  checks; the comparison with an independent calculation moved to C5. The release still
  waits for C5.
- **Benchmark method (2026-09-24).** Expected values come from an independent Monte Carlo
  script that implements the documented method, not from a spreadsheet of the original
  Hambsch equations, so that differences are noise or errors rather than method
  differences.
- **Acceptance before release (2026-09-24).** Domain experts accept the results by
  reviewing the C5 benchmark comparison and confirming it in writing, for example in the
  C5 pull request. The explanations in C4 are not part of this sign-off. Who signs off is
  still open (D3).
- **D5: no merge into `main` before the release (2026-09-24).** Merging any of C1–C5 into
  `main` before the release is not allowed. They stay open pull requests, each
  built on the one it depends on and tested on the dev environment, and are merged into
  `main` together at the release. Rejected: a setting that hides failures in production
  (extra code in C1), and a required approval for production deploys (would block urgent
  fixes on `main`). Accepted cost: long-lived branches and conflicts to resolve with
  `main`.
- **D6: one daily LRV rule for both cases (2026-10-16).** On a failure day, best-case and
  worst-case both use each failing step's daily LRV under the mixed-water assumption; the
  only difference is the step's starting LRV (maximum or minimum). Combined failures sum
  the steps' daily LRVs, which replaces the overlap rules. Replaces the worst-case full-day
  loss of ADR-0001. See ADR-0002 and finding F1 in `docs/review-2026-10-dev-scenarios.md`.
- **D7: number of parallel units (2026-10-16).** Each treatment step that accepts failure
  inputs has a number of parallel units (whole number of 1 or more, default 1, no upper
  limit). A failure event stops one unit and the other units keep working, which gives the
  failure LRV; failure frequency stays per step. Shown for every step that accepts failure
  inputs, including non-technical measures, and stored on personal treatment steps. Units
  failing together are not modelled; such a step is entered with one unit.
  Rejected: one failure reduction percentage for all pathogen groups. See ADR-0002 and
  finding F2.
- **Rework of C1–C3 (2026-10-16).** D6 and D7 are built in new tickets (14 and up) on the
  existing C1, C2 and C3 pull requests, not as a new Change, so that no pull request
  delivers a rule that has already been replaced. C1–C3 are in progress again until those
  tickets are done. The default failure duration stays 30 minutes (ADR-0002,
  Consequences).
