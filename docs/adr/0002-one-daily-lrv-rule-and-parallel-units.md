# ADR-0002: One daily LRV rule for both cases, with parallel units

- **Status:** Accepted
- **Date:** 2026-10-16
- **Deciders:** QMRA project team (review of the failure work on dev, October 2026)
- **Related:** ADR-0001 (this ADR replaces its rule for the LRV on a failure day),
  `docs/review-2026-10-dev-scenarios.md` (findings F1, F2), roadmap decisions D6 and D7,
  worked example: [Daily average LRV for treatment failures](https://claude.ai/code/artifact/2ea53cad-0d3f-4e40-90f8-e57a8867cc87)
- **TL;DR:** On a failure day, best-case and worst-case both weight each failing step's
  loss by the failure duration, and a step with several parallel units loses only the share
  of the failing unit.
- **Quality goals:** Scientific correctness — one rule for both cases, so the spread
  between best-case and worst-case comes only from the minimum and maximum LRVs and every
  failure input has an effect in both cases; one formula for single and combined failures,
  so the C5 benchmark checks one method.

## Context

ADR-0001 gave the two cases different rules on a failure day. Worst-case assumed all water
consumed on a failure day was treated during the failure event, so a failing step lost its
positive LRVs whatever the failure duration. Best-case applied the mixed-water assumption,
and combined failures in best-case were arranged with as little overlap as possible, with
extra rules for durations longer than a day.

Comparing scenarios on dev.qmra.org showed two problems. First, if worst-case assumes the
water is always used during the failure, best-case would consistently assume it is never
used during the failure, so neither case would depend on the duration. That is not
plausible. The duration is better read as the probability that water used on a failure day
was treated during the failure. Second, a failing step rarely drops to LRV 0: steps often
have several parallel units that do not fail at the same time.

## Decision

**Daily LRV.** On a failure day each failing treatment step gets a daily LRV, averaged by
concentration over the day, with d = failure duration / 1440 min:

```latex
LRV_{day} = -\log_{10}\left(d \cdot 10^{-LRV_{fail}} + (1 - d) \cdot 10^{-LRV}\right)
```

The train LRV of the day is the sum of the daily LRVs of failing steps and the normal LRVs
of the other steps. Best-case and worst-case use the same rule; LRV is the step's maximum
LRV in best-case and its minimum LRV in worst-case.

**Parallel units.** Each treatment step that accepts failure inputs has a number of
parallel units N, a whole number of 1 or more (default 1, no upper limit). The units share
the water equally, and a failure event stops one unit while the others keep working:

```latex
LRV_{fail} = -\log_{10}\left(\frac{N-1}{N} \cdot 10^{-LRV} + \frac{1}{N}\right)
```

With N = 1, LRV_fail = 0. LRV_fail is at most log10 N whatever the normal LRV (0.3 for two
units). Failure frequency stays the failure days per year of the whole step. LRVs of 0 or
below are not affected (D4).

The per-event draw of failure days in ADR-0001 stays unchanged.

## Options considered

| Option | Pros | Cons |
|--------|------|------|
| A (chosen): daily LRV per step, summed over the train, same rule in both cases | One formula for single and combined failures; no overlap rules; failure duration counts in both cases | Lower LRV than today's best-case on days with combined failures |
| B: keep ADR-0001 (worst-case full loss, best-case mixed water) | Already built (C2) | Worst-case ignores the duration; inconsistent assumptions between the two cases |
| C: mixed water in both cases, combined failures arranged with least overlap | Closest to the current best-case | Needs overlap rules and exceptions for durations longer than a day |
| D: plain average of the LRVs over the day | Simple to explain | Far too optimistic: 6.71 instead of 2.75 in the worked example |
| E: one failure reduction percentage per step instead of parallel units | Free choice of the remaining LRV | The same percentage for all pathogen groups is not physically meaningful |

## Consequences

- Worst-case results with failures become lower than today, because worst-case now uses the
  failure duration. Best-case results change only on days with combined failures, where
  they become higher in risk than today.
- Summing the steps' daily LRVs equals placing each failure event at a random time of day,
  independently of the other steps. The overlap rules for combined failures, including
  "three or more steps longer than a day count like worst-case", are dropped.
- The failure inputs per treatment step become failure frequency, failure duration and
  number of parallel units. This changes C1 (input and storage, also for personal treatment
  steps), C2 (calculation), C3 (export), C4 (explanations) and C5 (benchmark scenarios).
- With every number of parallel units at 1, the result on days with one failing step equals
  the current best-case rule, which keeps part of the C2 work.
- A comparison with Hambsch et al. (2019) now differs from the source also in worst-case,
  which the source calculates without the duration.
