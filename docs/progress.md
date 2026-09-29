# Progress: treatment failure (C1–C5)

Status: 2026-09-29. Work of 2026-09-24 to 2026-09-28 on the Changes in `docs/failure_roadmap.md`.
Nothing is merged into `main` (roadmap decision D5): each Change is a draft pull request that
targets `main` only so that the pipeline deploys it to dev. The production jobs run only for
`main` itself.

## Overview

| Change | Branch (based on) | Pull request | Tickets | State |
|---|---|---|---|---|
| C1 Failure inputs | `c1-failure-inputs` (`main`) | #28 | #21, #22, #23 (`docs/tickets/04`–`06`) | Built, tested manually on dev |
| C2 Failure calculation | `c2-failure-calculation` (C1) | #29 | #24, #25, #26 (`07`–`09`) | Built, tested manually on dev |
| C3 Failure inputs in the export | `c3-failure-inputs-in-export` (C2) | #34 | #30, #31 (`10`, `11`) | Built, deployed to dev, manual check open |
| C4 Explain treatment failure | not created yet (will be based on C2) | — | #32, #33 (`12`, `13`) | Tickets ready |
| C5 Failure benchmark | — | — | — | Waits for decisions D1–D3 |

**Dev** (https://dev.qmra.org) runs C1 + C2 + C3 (PR #34, commit `27b5268`) since 2026-09-25.

**Review of 2026-09-28** (by a teammate):
- **Statuses:** tickets 04–11 are set to "review".
- **Review notes:** ticket 09 records a review of the C2 commits against the Spec, ADR-0001 and the code; tickets 10 and 11 record a review of the C3 commits.
- **D4 wording:** `CONTEXT.md`, the roadmap and the vision now say that worst-case loses every *positive* LRV of a failing step, as the code does.

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
- **For the release notes:** `treatments.csv` has two new columns at the end.

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
- **C3 and C4 are based on C2,** so dev keeps C1 + C2 while they are tested.

## Open items

**Checks still to do**
- **C1 (#28):** real-data check; "I can explain this Change".
- **C2 (#29):** calculation time measured on dev and recorded in the PR (ticket 09, #26); real-data check; "I can explain this Change".
- **C3 (#34):** manual check on dev, from the list in the PR; real-data check; "I can explain this Change".

**Work not started**
- **C4:** #32 (FAQ and guided tour) and #33 (Sphinx page) can start now.
- **C5:** needs decisions D1 (tolerance), D2 (who writes the independent script) and D3 (who signs off). The script must implement the combined-failure rule of 2026-09-25.

**Known issues and risks**
- **Bug #27** (older than C1): an empty "Events per year" or "Volume per event" gives a server error for guests and registered users.
- **Lost click** (existing behaviour): typing into a field and clicking "Show assessment results" straight away loses the first click.
- **Precision:** tiny best-case probabilities lose precision in `1 − exp(−k·dose)`. Making the calculation more precise (`expm1`/`log1p`) would be a separate change to the calculation.
- **Step order:** failure draws are keyed by a step's position in the train. Saved assessments pass their steps without an explicit order (stable in practice).
- **Unpinned dependencies:** numpy and pandas aren't pinned; reproducibility across releases is an open question for Architecture.
- **Housekeeping:**
  - the C1 and C2 Spec issues were never created (`#___` in the roadmap);
  - the local branch `c2-failure-calculation` on the Controlled server is behind GitHub (the review commits of 2026-09-28) and holds one ticket commit (`5ca99b1`) that is on GitHub only through `c3-failure-inputs-in-export`. Update it from GitHub before working on it again.
  - The GitHub command-line login on the Controlled server has expired (`HTTP 401`); issues and pull requests can't be updated from there until someone logs in again.
