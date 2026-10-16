# Daily average LRV for treatment failures: worked example

Status: 2026-10-16. Example for finding F1 of `docs/review-2026-10-dev-scenarios.md`,
decided as D6 in `docs/failure_roadmap.md` and recorded in ADR-0002.

## Purpose

The new rule gives the same result as the earlier mixed-water rule when one step fails, and
a lower LRV when several steps fail on the same day. Best-case and worst-case use one
failure rule; only the starting LRV differs (maximum LRV in best-case, minimum LRV in
worst-case).

## The approach

Each treatment step first gets a daily average LRV for the failure day; the train LRV of
the day is the sum of these daily LRVs. No arrangement of failures within the day is
needed.

1. Daily LRV of one step, averaged by concentration, where d = failure duration / 1440 min
   is the share of the day the step is down:

   $LRV_{day} = -\log_{10}\left(d \cdot 10^{-LRV_{fail}} + (1 - d) \cdot 10^{-LRV}\right)$

2. Train LRV of the day = the sum of the daily LRVs of all steps. A step without a failure
   that day keeps its normal LRV.

LRV is the step's maximum LRV in best-case and its minimum LRV in worst-case. LRV_fail is
the step's LRV during the failure: 0 for one unit, and the parallel-units formula of D7
(ADR-0002) for more units.

## Example setup

A treatment train of two steps with a normal train LRV of 7.

| Step | Normal LRV | Parallel units | LRV during failure |
|------|------------|----------------|--------------------|
| A    | 4          | 1              | 0                  |
| B    | 3          | 1              | 0                  |

In the combined cases both steps fail on the same day for the same duration.

## Results

**One step fails (A for 60 min, B normal):** the train LRV of the day is 4.38 with both the
earlier mixed-water rule and the new approach.

**Both steps fail on the same day, each for the same duration** (train LRV of the day):

| Failure duration of each step | Earlier best-case (failures do not overlap) | New approach | Failures overlap as much as possible | Earlier worst-case |
|-------------------------------|---------------------------------------------|--------------|--------------------------------------|--------------------|
| 60 min                        | 4.34                                        | 2.75         | 1.38                                 | 0                  |
| 4 h                           | 3.74                                        | 1.55         | 0.78                                 | 0                  |
| 12 h                          | 3.26                                        | 0.60         | 0.30                                 | 0                  |
| 16 h                          | 0.48                                        | 0.35         | 0.18                                 | 0                  |

## What this means

- **Between the extremes.** Multiplying the steps' daily averages equals placing each
  failure at a random time of day, independently of the others. No overlap rules are
  needed, also not for failures that add up to more than a day.
- **Rare days.** Two steps fail on the same day only with probability
  f_A/365 × f_B/365 per exposure event: about 0.08 % of events with 10 failure days per
  year each. The yearly risk changes noticeably only with high failure frequencies or long
  durations.
- **Parallel units fit in.** LRV_fail in step 1 is the parallel-units formula of D7, so
  both decisions combine without extra rules.
- **Average by concentration, not by LRV.** A plain average of the LRVs over the day gives
  6.71 instead of 2.75 for the 60 min case, which is far too optimistic.
