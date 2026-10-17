# 16: Both cases use the daily LRV of each failing step

**What to build:** On a failure day, best-case and worst-case use the same rule (D6, ADR-0002). Each failing treatment step gets a **daily LRV** under the mixed-water assumption: the water consumed that day is a mixture of water treated during the failure event and water treated in normal operation, in proportion to the failure duration, averaged by concentration and never by LRV. The step starts from its maximum LRV in best-case and from its minimum LRV in worst-case. The LRV of an exposure event on a failure day is the case's LRV of the train minus, for every step failing that day, the difference between its LRV and its daily LRV. Combined failures need no further rule.

In this Ticket a failing step has LRV 0 during the failure event, which is the failure LRV of one parallel unit. The number of parallel units follows in Ticket 17.

The rules of the first version are removed: the worst-case loss of the failing steps' positive minimum LRVs for the whole day regardless of the failure duration, the best-case arrangement of combined failures without overlap, the overlap by the minutes beyond a day, and the rule that three or more steps longer than a day in total count like worst-case. The failure-day draws per exposure event (ADR-0001), the concentration sampling and the fixed seeds stay as they are. LRVs of 0, below 0 or empty are not affected by a failure (D4).

The result page, the reference-level exceedance, saved results and the export's result table show whatever the calculation returns. Their layout does not change.

Delivered on branch `c2-failure-calculation` as part of the C2 pull request (#29). The pull request is not merged before the release (D5).

Source: Spec C2 Failure calculation, revision for D6 and D7 (`docs/specs/c2-failure-calculation.md`), roadmap decision D6, ADR-0002, worked example `docs/failure-daily-lrv-example.md`. The Spec issue does not exist yet. GitHub issue: not created yet.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Both cases calculate a failing step's daily LRV from its failure duration, starting from the step's maximum LRV in best-case and its minimum LRV in worst-case, and sum the daily LRVs of all steps failing that day over the train.
- [ ] The worst-case full-day loss and the best-case overlap rules are removed from the calculation.
- [ ] With every failure frequency at 0, all results equal today's exactly, including the existing regression test's numbers.
- [ ] A step always failing for 1,440 minutes gives the same results in both cases as the scenario without that step's positive LRVs.
- [ ] The results match the worked example (`docs/failure-daily-lrv-example.md`), allowing for its two-decimal rounding: one step with LRV 4 failing 60 minutes next to a step with LRV 3 gives the results of a train with constant LRV 4.38; both steps failing 60 minutes, 4 h, 12 h and 16 h each give those of 2.75, 1.55, 0.60 and 0.35.
- [ ] In the 60-minute combined case, the result differs clearly from a train with the plain LRV average of 6.71.
- [ ] Raising a failure duration never lowers any mean, in either case; raising a failure frequency never lowers any mean; worst-case mean is never below best-case mean.
- [ ] D4: a negative LRV of one pathogen group stays unchanged when the step fails, a group with LRV 0 is unaffected, and a step with minimum LRV 0 and a positive maximum LRV changes only best-case when it fails.
- [ ] The same scenario gives identical results on every calculation.
- [ ] The first-version tests for the worst-case full-day loss, the duration not changing worst-case, and the best-case overlap rules are replaced or removed as the Spec names them. All other tests pass.

Quality goals (`docs/vision.md`): Scientific correctness (expected values from the worked example, not from the code), Reproducibility (fixed seeds, frequency 0 unchanged).
