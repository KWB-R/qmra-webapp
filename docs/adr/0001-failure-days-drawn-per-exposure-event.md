# ADR-0001: Failure days are drawn per exposure event inside the Monte Carlo simulation

- **Status:** Accepted
- **Date:** 2026-09-23
- **Deciders:** QMRA project team (domain-modeling session on the failure approach)
- **Related:** `docs/QMRA_Failure_Approach.md` (Decisions section), `CONTEXT.md` (Treatment failure, Failure day, Failure frequency)
- **TL;DR:** When treatment failures are added, each exposure event is randomly assigned to a failure day or a normal day inside the existing simulation, instead of counting 365 days per year as the source method does.
- **Quality goals:** scientific correctness — one calculation path for single and combined failures, consistent with how the existing model builds yearly risk; understandable assumptions — failure frequency stays in the unit operators know (days per year).

## Context

The failure approach (`docs/QMRA_Failure_Approach.md`, after Hambsch et al., 2019) builds
yearly infection risk from 365 daily risks. With one failing treatment step it uses a
closed formula over exactly *n* failure days (Eq. 6); for several failing steps it draws a
random 365-day sequence of failure days per step.

The application does not work in days. It builds yearly risk from exposure events: it
samples the dose of each event and combines as many events as the exposure has per year.
For drinking water (365 events per year) days and events coincide; for an exposure such as
irrigation with 20 events per year they do not, and "5 failure days per year" has no
direct meaning for the calculation.

## Decision

Failure frequency is entered in failure days per year per treatment step. Inside the
Monte Carlo simulation, each exposure event falls on a failure day of each step
independently, with probability failure frequency / 365. Events on a failure day use the
LRV with the failing steps removed (worst-case) or the mixed-water LRV (best-case). There
is no separate deterministic calculation path based on Eq. 6, including for the case of a
single failing step.

## Options considered

| Option | Pros | Cons |
|--------|------|------|
| A (chosen): per-event draw with probability n/365 | Works for every exposure; one path for single and combined failures; fits the existing event-based simulation | Departs from the cited method; the number of failure events varies between simulated years |
| B: one exposure event per day, 365-day sequence as in the source | Matches the source method literally | Forces exposures to at most 365 events per year and changes how exposures are defined |
| C: deterministic share, events × n/365 failure events per year | Simple, no extra randomness | Fractional events for small exposures; a second path next to the combined-failure draw |
| D: Eq. 6 for one failing step, random draw only for combined failures | Closest to the source for the simple case | Two calculation paths that give different results for comparable inputs |

## Consequences

- Results with failures will not equal a hand calculation with Eq. 6. They agree on
  average, but the number of failure events varies from simulated year to year, which
  widens the risk distribution. This is intended: it reflects that failures are random.
- For exposures with few events per year and low failure frequencies, many simulated years
  contain no failure event at all. The yearly risk distribution will show this as a long
  upper tail rather than a shifted median.
- Two exposure events on the same calendar day are not forced to share the same failure
  state. This is accepted, since the model has no notion of calendar days.
- Anyone comparing the application against Hambsch et al. (2019) needs this ADR to explain
  the difference.
