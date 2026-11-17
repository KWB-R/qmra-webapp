# Progress: treatment failure (C1–C5)

Status: 2026-11-17. Work of 2026-09-24 to 2026-09-28 on the Changes in `docs/failure_roadmap.md`,
the rework after the dev review of October 2026 (D6, D7), and C4 (2026-10-17, pull request
opened 2026-11-17).
Nothing is merged into `main` (roadmap decision D5): each Change is a draft pull request that
targets `main` only so that the pipeline deploys it to dev. The production jobs run only for
`main` itself.

## Overview

| Change | Branch (based on) | Pull request | Tickets | State |
|---|---|---|---|---|
| C1 Failure inputs | `c1-failure-inputs` (`main`) | #28 | #21, #22, #23 (`docs/tickets/04`–`06`); #36, #37 (`14`, `15`) | D7 rework built (tickets 14–15), tested manually on dev |
| C2 Failure calculation | `c2-failure-calculation` (C1) | #29 | #24, #25, #26 (`07`–`09`) | D6/D7 rework built (tickets 16–17, #38, #39), tested manually on dev |
| C3 Failure inputs in the export | `c3-failure-inputs-in-export` (C2) | #34 | #30, #31 (`10`, `11`); #40 (`18`) | D7 rework built (ticket 18), tested manually on dev |
| C4 Explain treatment failure | `c4-failure-explanations` (C3) | #41 | #32, #33 (`12`, `13`) | Built; texts are drafts for domain expert review; manual check on dev open |
| C5 Failure benchmark | — | — | — | Waits for decisions D1–D3 |

**Dev** (https://dev.qmra.org) ran C1 + C2 + C3 (PR #34, commit `dfa309f`) from 2026-10-17. Opening PR #41 on 2026-11-17 deploys C1–C4 (commit `36e18ef`).

**Review of 2026-09-28** (by a teammate):
- **Statuses:** tickets 04–11 are set to "review".
- **Review notes:** ticket 09 records a review of the C2 commits against the Spec, ADR-0001 and the code; tickets 10 and 11 record a review of the C3 commits.
- **D4 wording:** `CONTEXT.md`, the roadmap and the vision now say that worst-case loses every *positive* LRV of a failing step, as the code does.

**Dev review of October 2026** (`docs/review-2026-10-dev-scenarios.md`, merged into `main` as #35):
- **D6:** best-case and worst-case use one rule on a failure day, the daily LRV of each failing step (ADR-0002). It replaces the worst-case full-day loss and the overlap rules built in #25 and #26.
- **D7:** a third failure input, the number of parallel units; a failure stops one unit (ADR-0002).
- **Rework:** in new tickets on the existing pull requests (roadmap, "Rework of C1–C3"). `main` was merged into C1–C3 on 2026-10-16 (docs only).
- **C1:** spec revised for D7 (`e9d5ce7`), tickets 14 (#36) and 15 (#37) written and built:
  - **Configurator (#36, `e547ca1`):** each treatment step has a number of parallel units (a whole number of 1 or more, no upper limit, default 1) next to failure frequency and failure duration, for guests and registered users; the shared rule rejects values below 1 and fractions with one message; existing assessments get 1.
  - **Personal treatment steps (#37, `f19a791`):** they store the number of parallel units under the same rule, and the configurator copies it into a newly added step; existing personal treatment steps get 1.
  - **Manual check on dev** passed on 2026-10-17. C1 was merged forward into C2 and C3; their tests pass.
- **C2:** spec revised for D6 and D7 (`3196dc4`), tickets 16 (#38) and 17 (#39) written and built; tickets 08 and 09 are marked as partly replaced:
  - **Daily LRV (#38, `99ad33d`):** on a failure day both cases use each failing step's daily LRV under the mixed-water assumption, averaged by concentration and starting from the maximum or minimum LRV; the losses of the failing steps are summed. The worst-case full-day loss and the overlap rules are removed. Tests compare with the worked example (`docs/failure-daily-lrv-example.md`).
  - **Parallel units (#39, `ff9891d`):** the failure LRV follows from the number of parallel units; one unit gives LRV 0. Tests compare with the D7 table.
  - **Calculation time** (local, drinking water, 365 events, 5 steps): 0.069 s without failures, 0.117 s with failures in all five steps. Still to be recorded in PR #29.
  - **Manual check on dev** passed on 2026-10-17. C2 was merged forward into C3 (`464b31c`); the reference export was updated on purpose, see below.
- **C3:** ticket 18 (#40) written and built:
  - **Parallel units column (#40, `dfa309f`):** `treatments.csv` has the column "Number of parallel units" after the two failure columns, repeated on each step's three rows; assessments saved before C1 export 1. The reference export was updated on purpose by that column only.
  - **Manual check on dev** passed on 2026-10-17, which also completes Ticket 11's check of the two failure columns and the unchanged report.
- **Still open:** the release note in PR #34 and the calculation time in PR #29 (to be posted on GitHub); then C5. C4 followed on 2026-10-17, see below.

**C4 (2026-10-17, PR #41 opened 2026-11-17):** based on C3 (`ed28879`) so that the C4 tickets and the export are there. Tickets 12 (#32, `520dc8b`) and 13 (#33, `0cfa9c8`) built, plus report texts (`36e18ef`). All texts are drafts written by Claude, for domain expert review before the release. The full suite passes (83 tests, 12 of them new for C4).

## What each Change delivers

### C1 Failure inputs (#28)

- **Configurator (#21, `57bdd21`):**
  - each treatment step has a failure frequency (days per year, 0–365, default 0) and a failure duration (whole minutes, 1–1440, default 30), with units;
  - values are checked on run and save, and stay with their step through save, reopen and edit;
  - the migration gives existing assessments 0 and 30;
  - one shared validation rule replaces the duplicated min ≤ max LRV check.
- **Positive LRV and guests (#22, `52e6087`):**
  - a frequency above 0 needs at least one positive LRV (D4);
  - guests now see validation messages on the affected field and step (before, an invalid guest result failed silently);
  - the treatments section grows with its content instead of hiding the new fields under the footer.
- **Personal treatment steps (#23, `7f05bcd`):** they store both values under the same rules, the configurator copies them into a newly added step, and the copy can be changed without touching the personal step.

### C2 Failure calculation (#29)

- **Tidy-up (#24, `93c8f76`):** the simulation works per exposure event. Results are bit-identical to before (checked on 28 scenarios, 1932 values).
- **Failure days and worst-case (#25, `2f6efec`):**
  - each exposure event falls on a failure day of each step with probability frequency / 365 (ADR-0001);
  - the draws come from their own fixed seed, one stream per step position, shared by both cases and all pathogens;
  - worst-case loses the failing steps' positive minimum LRVs for the whole day.
- **Best-case (#26, `a8a1972`):** the mixed-water assumption. For combined failures of one day, only steps that lose LRV for the pathogen group count:
  - failures that fit into a day don't overlap (one step: Eq. 5);
  - two steps longer than a day overlap by the extra minutes;
  - three or more steps longer than a day in total count like worst-case.
- **Without failures:** results are exactly those from before C2.
- **Local timing** (drinking water, 3 pathogens, 5 bundled steps): 0.07 s without failures, 0.13–0.19 s with failures.

### C3 Failure inputs in the export (#34)

- **Reference export test (#30, `7085d78`, fixes `305ec0f`, `27b5268`):** implements the "Export stability" Quality goal.
  - A fixed benchmark assessment is exported and compared with `qmra/risk_assessment/tests/reference_export/`: the same files, identical text, and each number within 0.1 % relative. Plots are only checked for presence.
  - `UPDATE_REFERENCE_EXPORT=1` rewrites the reference on purpose (see the README there).
- **Failure columns (#31, `a04e2f9`):** `treatments.csv` has "Failure frequency (days per year)" and "Failure duration (minutes)", repeated on each step's three rows. The HTML report stays without inputs.
- **For the release notes:** `treatments.csv` has three new columns at the end: "Failure frequency (days per year)", "Failure duration (minutes)" and, since ticket 18 (#40), "Number of parallel units".
- **Reference export updated on 2026-10-17 (`464b31c`):** after D6, the worst-case ("Minimum LRV") results of the benchmark assessment are lower, because worst-case now uses the failure duration; the reference-level exceedance in the report drops from "min" to "none" twice. Best-case values, files and columns are unchanged.
- **For the release notes:** worst-case results of assessments with failures are lower than with the first version (D6, ADR-0002); the reference-level exceedance can drop from "min" to "none".

### C4 Explain treatment failure (#41)

- **FAQ and guided tour (#32, `520dc8b`):**
  - new FAQ question 13 on treatment failure: the three failure inputs, failure days per exposure event, the failure LRV from the number of parallel units, the daily LRV under the mixed-water assumption for both cases, combined failures and D4;
  - the limitations question (now 14) says that units of a step failing together are not modelled; such a step is entered with one unit;
  - step 4 of the guided tour names the three failure fields with their units;
  - tests (`test_failure_explanations`) check that the inputs are named and that none of the replaced rules appear.
- **Sphinx page "Treatment failure" (#33, `0cfa9c8`):** linked from `index.rst`. Formulas, ranges, the D7 table, the worked example, and how the method differs from the source (ADR-0001, ADR-0002). Tests (`test_failure_docs`) compare the page's numbers with the implemented calculation. The documentation builds locally with Sphinx 9.1.0.
- **Report texts (`36e18ef`):** `docs/report/failure-approach-main-text` (idea, decisions, an example calculated with the tool) and `failure-approach-annex` (algorithm, all equations, a hand calculation, an R script), as Markdown with `.docx` built by pandoc.

## Decisions made during implementation

All on 2026-09-25 unless noted. The documents named are updated.

- **C1: failure fields are required in the form.** Existing form tests got the two fields in their input data.
- **C1: guests see validation errors.** The guest result returns the messages, and the configurator shows them on the affected step (option a).
- **C1: dev only moves forward.** The migrations can't be reversed on dev, and only C1 and branches built on it go there until the release. The columns get no database default.
- **C2: statistics instead of the mean.** Tests check the returned statistics and the exceedance, because the mean isn't returned. Per-year coupling makes that equivalent.
- **C2: one C1 test split.** With frequency 0, results and export stay identical. With failures, only values change.
- **C2: three or more steps over a day count like worst-case in best-case.** This replaces the lowest-concentration arrangement decided on 2026-09-24, which needed a linear program whose solver failed for large combined losses; the per-pathogen arrangement rule is dropped with it. See the C2 Spec, `CONTEXT.md` (*Combined failure*), decision 6 in `docs/QMRA_Failure_Approach.md`, the roadmap and the vision.
- **C2: only steps that lose LRV for the pathogen group count** towards "three or more" (Reading 1).
- **C2: tested on dev with a PR into `main`,** because the pipeline deploys only pull requests into `main`.
- **C3 and C4 have no Spec** (Small Changes). The Tickets follow the roadmap entries.
- **C3: the HTML report shows no inputs** and doesn't get failure inputs. Roadmap entry corrected.
- **C3: failure columns are repeated on each step's three rows** of `treatments.csv`.
- **C3: a reference export test is added**, comparing numbers within 0.1 %. CI's processor and math library differ from this server's by up to 10⁻⁵ relative in tiny best-case probabilities.
- **C4: texts are drafted by Claude** and reviewed by a domain expert before the release. Step 4 of the guided tour is extended, and a new Sphinx page is added.
- **C3 is based on C2,** so dev keeps C1 + C2 while it is tested.
- **C4 is based on C3** (changed 2026-10-17, `ed28879`), so that the C4 tickets and the export are there. Dev runs C1–C4 from PR #41 on.

## Open items

**Checks still to do**
- **C1 (#28):** real-data check; "I can explain this Change".
- **C2 (#29):** calculation time recorded in the PR (measured locally, see above; ticket 09, #26); real-data check; "I can explain this Change".
- **C3 (#34):** release note in the PR updated for the third column; real-data check; "I can explain this Change".
- **C4 (#41):** manual check on dev, from the list in the PR; domain expert review of the FAQ, the tour, the Sphinx page and the report texts; `code-review`; "I can explain this Change".

**Work not started**
- **C5:** needs decisions D1 (tolerance), D2 (who writes the independent script) and D3 (who signs off). The script must implement the combined-failure rule of 2026-09-25.

**Known issues and risks**
- **Bug #27** (older than C1): an empty "Events per year" or "Volume per event" gives a server error for guests and registered users.
- **Lost click** (existing behaviour): typing into a field and clicking "Show assessment results" straight away loses the first click.
- **Precision:** tiny best-case probabilities lose precision in `1 − exp(−k·dose)`. Making the calculation more precise (`expm1`/`log1p`) would be a separate change to the calculation.
- **Step order:** failure draws are keyed by a step's position in the train. Saved assessments pass their steps without an explicit order (stable in practice).
- **Unpinned dependencies:** numpy and pandas aren't pinned; reproducibility across releases is an open question for Architecture.
- **Housekeeping:**
  - the C1 and C2 Spec issues were never created (`#___` in the roadmap);
  - the local branch `c2-failure-calculation` matches GitHub again (checked 2026-11-17).
  - The GitHub command line works again on the Controlled server (2026-11-17): PR #41 was opened from there.
