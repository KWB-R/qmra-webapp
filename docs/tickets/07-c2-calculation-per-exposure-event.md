# 07: Tidy-up: the calculation works per exposure event, with results unchanged

**What to build:** Tidy-up before failures enter the calculation. No result changes.

The Monte Carlo simulation is reorganised to work per simulated exposure event. Each event picks its concentration sample by position instead of by value, which uses exactly the same random numbers as today, and each event gets its own LRV. For now every event still gets the same LRV. Best-case and worst-case use the same building blocks, and the summary statistics (mean, minimum, quartiles, median, maximum) and the reference-level exceedance are computed in one place for both cases and both risk measures. The calculation's public entry point keeps its interface.

Delivered on branch `c2-failure-calculation`, based on `c1-failure-inputs`, as part of the single C2 pull request. The pull request stays open until the release (D5).

Source: Spec C2 Failure calculation (`docs/specs/c2-failure-calculation.md`), Change C2 in `docs/failure_roadmap.md`. The Spec issue does not exist yet. GitHub issue #24.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [x] Every simulated exposure event has its own concentration sample, picked by position, and its own LRV. The random numbers are the same as today's.
- [x] Best-case and worst-case share the same calculation steps. Summary statistics and the reference-level exceedance are computed in one place.
- [x] The existing regression test passes with exactly the same numbers, and the existing test suite passes unchanged.
- [x] A new test at the calculation's public entry point shows that calculating the same scenario twice gives identical results.
