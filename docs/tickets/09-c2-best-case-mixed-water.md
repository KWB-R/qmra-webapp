# 09: Best-case applies the mixed-water assumption, including combined failures

**What to build:** The best-case result includes treatment failures under the mixed-water assumption. On a failure day, the consumed water is a mixture of water treated during the failure events and water treated in normal operation, in proportion to the failure durations. The event's LRV is −log₁₀ of the time-weighted average of 10^(−LRV) over the segments of the day, where a segment's LRV is the best-case LRV of the train minus the positive maximum LRVs of the steps down in that segment.

Combined failures of one day:
- if their durations fit into one day, they do not overlap;
- two failure events longer than a day in total overlap only by the minutes beyond the day;
- three or more failure events longer than a day in total count like worst-case: all these steps are down for the whole day (changed on 2026-09-25 from the lowest-concentration arrangement, which needed a numerical solver for a rare exception). Only steps that lose LRV for the pathogen group count.

For a single failing step, the result equals Eq. 5 of the failure approach. Work per failure day is reused for repeated combinations of failing steps.

This Ticket closes C2: it includes the manual check on the dev environment and the time measurement.

Source: Spec C2 Failure calculation (`docs/specs/c2-failure-calculation.md`), ADR-0001, `CONTEXT.md` (*Mixed-water assumption*, *Combined failure*), decision 6 in `docs/QMRA_Failure_Approach.md`. The Spec issue does not exist yet. GitHub issue #26.

**Blocked by:** 08 (#25)

**Status:** ready-for-agent

- [ ] A step with failure frequency 365 and failure duration 1,440 gives the same best-case results as the same scenario without that step's positive maximum LRVs.
- [ ] A step with failure frequency 365 and failure duration 60 gives the same best-case results as the scenario with the train's best-case LRV replaced by the Eq. 5 mixed LRV, computed by hand in the test.
- [ ] Two steps always failing with 900 + 900 minutes equal the hand-computed result with 360 minutes of overlap.
- [ ] Three steps always failing within a day in total equal the hand-computed result without overlap.
- [ ] Three steps always failing with more than a day in total equal the scenario without their positive maximum LRVs.
- [ ] A failing step without removal for one pathogen group does not count for that group.
- [ ] Raising a failure duration never lowers a best-case mean, and raising a failure frequency never lowers any mean.
- [ ] Worst-case mean ≥ best-case mean for every reference pathogen and risk measure, with failures.
- [ ] With every failure frequency at 0, all results equal today's exactly. The same scenario gives identical results every time. The existing test suite passes unchanged.
- [ ] Manual check on the dev environment, announced to the team first:
  - Enter a scenario with failures and run it as a guest and as a registered user.
  - Confirm that the result page, the saved-assessments page, the assessment comparison and the export's result table show the changed results, with unchanged layout.
- [ ] The calculation time for a drinking-water scenario (365 events per year) with failures is measured on the dev environment and recorded in the pull request.
