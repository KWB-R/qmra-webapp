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

**Status:** in-progress (built in pull request #29; CI green on `a8a1972`; the pull request stays open until the release, D5)

- [x] A step with failure frequency 365 and failure duration 1,440 gives the same best-case results as the same scenario without that step's positive maximum LRVs.
- [x] A step with failure frequency 365 and failure duration 60 gives the same best-case results as the scenario with the train's best-case LRV replaced by the Eq. 5 mixed LRV, computed by hand in the test.
- [x] Two steps always failing with 900 + 900 minutes equal the hand-computed result with 360 minutes of overlap.
- [x] Three steps always failing within a day in total equal the hand-computed result without overlap.
- [x] Three steps always failing with more than a day in total equal the scenario without their positive maximum LRVs.
- [x] A failing step without removal for one pathogen group does not count for that group.
- [x] Raising a failure duration never lowers a best-case mean, and raising a failure frequency never lowers any mean.
- [x] Worst-case mean ≥ best-case mean for every reference pathogen and risk measure, with failures.
- [x] With every failure frequency at 0, all results equal today's exactly. The same scenario gives identical results every time. The existing test suite passes unchanged.
- [x] Manual check on the dev environment, announced to the team first:
  - Enter a scenario with failures and run it as a guest and as a registered user.
  - Confirm that the result page, the saved-assessments page, the assessment comparison and the export's result table show the changed results, with unchanged layout.
- [ ] The calculation time for a drinking-water scenario (365 events per year) with failures is measured on the dev environment and recorded in the pull request.

Review on 2026-09-28 (against the Spec, ADR-0001 and the code of the three C2 commits):

- [x] The calculation matches the Spec: failure days per exposure event from a fixed-seed generator shared by both cases and all pathogens; worst-case loses only positive minimum LRVs; best-case follows the mixed-water rules including the three-or-more exception; LRVs of 0 or below are untouched. The hand-computed examples of decision 6 (mixed LRV about 6.9 and about 2.6) agree with the code's formula.
- [x] The concentration samples are picked by position with the same generator calls as before, so results without failures stay bit-identical. The PR records a 28-scenario check of this.
- [ ] Wording left over from before D4: `CONTEXT.md` (*Combined failure*: "loses all their LRVs"), `docs/vision.md` MVP item 3 and the C2 scope in `docs/failure_roadmap.md` still say worst-case loses the *full* LRV of a failing step. It should say every *positive* LRV.
- [ ] Decide whether it is acceptable that the failure draws of a step depend on its position in the train. Two scenarios that differ only by an extra non-failing step placed *before* a failing one give slightly different results, because the later step's random stream changes. The difference is sampling noise, but it can surprise a user comparing two saved assessments, and C5's independent script must use the same keying to match.
- [ ] The Spec still says "Status: draft" and "Spec issue: #___". Set it to implemented and create the Spec issue, or record that C2 has none.
