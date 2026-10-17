# 17: The failure LRV follows from the number of parallel units, and C2 is checked on dev

**What to build:** A failing treatment step with N parallel units keeps the share of water treated by the other units during the failure event (D7, ADR-0002). For each positive LRV, its failure LRV is the LRV of the mixture of untreated water (1/N) and water treated with the step's LRV ((N − 1)/N), mixed by concentration. It is 0 for one unit, as in Ticket 16, and at most log₁₀ N. The daily LRV of Ticket 16 uses this failure LRV in both cases. Failure frequency stays per step, and LRVs of 0 or below are not affected (D4).

This Ticket closes the D6/D7 rework of C2: it includes the manual check on the dev environment and the time measurement.

Delivered on branch `c2-failure-calculation` as part of the C2 pull request (#29). The pull request is tested on the dev environment again and not merged before the release (D5).

Source: Spec C2 Failure calculation, revision for D6 and D7 (`docs/specs/c2-failure-calculation.md`), roadmap decision D7, ADR-0002. The Spec issue does not exist yet. GitHub issue #39.

**Blocked by:** 16 (#38)

**Status:** ready-for-agent

- [x] The calculation reads each treatment step's number of parallel units and uses the failure LRV in the daily LRV of both cases.
- [x] A step with one parallel unit gives the same results as in Ticket 16.
- [x] A step with LRV 4 always failing for the whole day with 2, 4 or 10 parallel units gives the same results as a train in which that step has LRV 0.30, 0.60 or 1.00 (the D7 table, allowing for its two-decimal rounding).
- [x] Raising the number of parallel units never raises any mean.
- [x] All tests pass, and the export package keeps its files and columns with failures.
- [ ] The calculation time of a drinking-water scenario (365 events per year) with failures is measured and recorded in the C2 pull request.
- [ ] Manual check on the dev environment, announced to the team first:
  - Enter the worked example's two steps with failures and run them as a guest and as a registered user.
  - Change the failure duration and the number of parallel units, and see both cases react.
  - Confirm that the result page, the saved-assessments page and the export's result table show the changed results.

Quality goals (`docs/vision.md`): Scientific correctness (expected values from the D7 table, not from the code), Export stability (files and columns unchanged).
