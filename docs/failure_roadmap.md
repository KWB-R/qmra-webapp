# Failure roadmap

Status: draft, 2026-09-24. Overview of the Changes that deliver the MVP in `docs/vision.md`:
treatment failure, including combined failures. Sources of truth: `docs/vision.md`,
`CONTEXT.md`, `docs/adr/`. Each Large change gets a Spec (`/to-spec`); Small changes are
built directly. Changes are refined into tickets later. All Changes start from `main`.

## Changes

### C1 Failure inputs — Large

Spec issue: #___

Purpose: users can enter a failure frequency and a failure duration for each treatment
step, and they are stored with the scenario.

Scope: failure frequency (failure days per year, 0–365, default 0) and failure duration
(minutes, 1–1440, default 30) on each treatment step of an assessment and on personal
treatment steps; configurator fields with units and validation; only treatment steps with
a positive LRV accept failure inputs (see D4); values of a personal treatment step are
carried into the assessment; saving, reopening and editing keep them. Existing saved
assessments get failure frequency 0, so their results are unchanged.

Not included: any effect on the calculation (C2), export and report (C3), explanations
beyond field labels and units (C4).

### C2 Failure calculation — Large

Spec issue: #___

Purpose: results include treatment failures as decided in ADR-0001.

Scope: failure days drawn per exposure event and per treatment step inside the Monte Carlo
simulation; worst-case loses the full LRV of every failing step; best-case applies the
mixed-water assumption; combined failures overlap as little as possible; the result page
and the reference-level exceedance show the result including failures. With every failure
frequency at 0, results equal today's. The Spec defines benchmark scenarios with failures;
a domain expert provides their expected values, and the Change is done when results match
within the agreed tolerance.

Not included: showing normal operation next to the result with failures (decided
against), DALYs in the assessment comparison (later).

### C3 Failure inputs in export and report — Small

The export package's treatment table and the HTML report show each treatment step's failure
frequency and failure duration, so a reader can see which failures a result is based on.
Left out: renaming export files (`inflows.csv` → `inflow_concentration.csv` waits until
later), origin and reference columns for inputs, changes to the assessment comparison.

### C4 Explain treatment failure — Small

The FAQ, the configurator guided tour and the Sphinx documentation (`docs/source/`) explain
failure frequency and failure duration, failure days, why worst-case ignores the failure
duration, the mixed-water assumption and combined failures. Left out: field labels and
units (C1), rewording the deferred UI terms such as "tolerable risk level", and
explanations of unrelated parts of the model.

## Dependencies

- C2 depends on C1 (it reads the stored failure inputs).
- C3 depends on C1.
- C4 depends on C2 (it explains the calculation's behaviour) and on C1.
- Release depends on C1–C4: nothing is deployed until all four are merged, so users never
  see failure inputs without effect or results they cannot trace.

## Parallel work

- The Specs of C1 and C2 can be written in parallel; both rest on `CONTEXT.md` and ADR-0001.
- After C1 is merged, C2 and C3 can be built in parallel.
- C4 can be drafted while C2 is being built and finished once C2 is merged.

## Sequence

1. `/to-spec` C1 and C2 (in parallel).
2. `/implement` C1.
3. `/implement` C2; build C3 in parallel.
4. Build C4 once C2 is merged.
5. Release once C1–C4 are merged.

## Unresolved decisions

| # | Decision | Owner | Depends on | Blocks |
|---|---|---|---|---|
| D1 | Tolerance for matching benchmark scenarios | Wolfgang, Malte | — | Completion of C2 (not its Spec) |
| D2 | Expected values for the failure benchmark scenarios, from a domain expert | Wolfgang, Malte | C2 Spec (which scenarios) | Completion of C2 |
| D3 | Which domain experts accept the results | Wolfgang, Malte | D1, D2 | Release |
| D4 | Which treatment steps accept failure inputs when their LRV is positive for one pathogen group but zero or negative for another | Wolfgang, Malte | — | C1 Spec |
