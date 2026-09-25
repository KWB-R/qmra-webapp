# 08: Failure days drawn per exposure event; worst-case loses the positive LRVs of failing steps

**What to build:** The worst-case result includes treatment failures. For every simulated exposure event, and for every treatment step with a failure frequency above 0, the step fails that day with probability failure frequency / 365 (ADR-0001). On a failure day, worst-case calculates the event with the positive minimum LRVs of every failing step removed, whatever the failure duration. LRVs of 0, below 0 or empty stay in place (D4).

The failure draws come from their own fixed-seed random generator and are shared by both cases and all reference pathogens. Raising a failure frequency therefore only adds failure days. If every failure frequency is 0, no failure draws are made and the results are exactly today's. Best-case does not change in this Ticket; the mixed-water assumption follows in the next one.

The result page, the reference-level exceedance, saved results and the export's result table show whatever the calculation returns. Their layout does not change.

Source: Spec C2 Failure calculation (`docs/specs/c2-failure-calculation.md`), ADR-0001, roadmap decision D4. The Spec issue does not exist yet. GitHub issue #25.

**Blocked by:** 07 (#24), 04 (#21, C1 stored failure inputs)

**Status:** ready-for-agent

- [x] With every failure frequency at 0, all results equal today's exactly, including the existing regression test's numbers.
- [x] A step with failure frequency 365 gives the same worst-case results as the same scenario without that step's positive minimum LRVs.
- [x] Raising a failure frequency never lowers any mean. Changing a failure duration leaves worst-case unchanged.
- [x] Worst-case mean ≥ best-case mean for every reference pathogen and risk measure, with and without failures.
- [x] D4: a failing step with a negative LRV in one pathogen group and a positive LRV in another leaves the first group's results unchanged. A group with LRV 0 is unaffected.
- [x] Calculating the same scenario with failures twice gives identical results.
- [x] All tests go through the calculation's public entry point and check only the returned results. The existing test suite passes unchanged.
