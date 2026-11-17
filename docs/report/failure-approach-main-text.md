---
title: "Treatment failure in the QMRA tool: approach and decisions"
subtitle: "Text for the main part of the report (draft, 2026-10-17)"
---

# Purpose

A quantitative microbial risk assessment (QMRA) usually assumes that every treatment step
always reaches its log removal value (LRV). In practice, treatment steps sometimes fail: a
UV lamp breaks, a filter is bypassed, a dosing pump stops. Short failures can contribute a
large part of the annual infection risk, because a few days with poorly treated water can
outweigh many days of normal operation.

The QMRA tool was therefore extended so that each treatment step can be given failure
events. This chapter explains the idea of the approach and the reasons behind its main
decisions. The equations and the full algorithm are given in the annex. The approach builds
on the failure approach of Hambsch et al. (2019) and departs from it in the points
explained below.

# Starting point: the QMRA tool without failures

The tool estimates the annual probability of infection and the disease burden (DALYs) for
three reference pathogens (Rotavirus, *Campylobacter jejuni* and *Cryptosporidium parvum*).
It runs a Monte Carlo simulation: for each simulated year, it draws the pathogen
concentration in the source water for every exposure event of the year, reduces it by the
LRV of the treatment train, and turns the ingested dose into a probability of infection.

The uncertainty about the treatment performance is expressed by two cases. Best-case uses
the maximum LRV of every treatment step, worst-case uses the minimum LRV. The range between
the two cases shows how much the result depends on the treatment performance.

# Failure inputs

Each treatment step has three failure inputs. They apply to all pathogen groups of the
step.

- **Failure frequency:** the expected number of failure days per year (0 to 365). With the
  default of 0, the step never fails.
- **Failure duration:** the average length of one failure event in minutes (1 to 1,440,
  default 30).
- **Number of parallel units:** how many equal units share the water of the step (a whole
  number of 1 or more, default 1).

The inputs were chosen because operators know them or can estimate them from their
operating records: on how many days a year something goes wrong, for how long, and how the
step is built.

# Main ideas and the reasons for them

## Failure days are drawn at random for each exposure event

The tool builds the annual risk from exposure events, not from calendar days. For drinking
water there is one exposure event per day, but for other uses there are far fewer, for
example 20 irrigation events per year. For each exposure event, the tool therefore draws at
random whether it falls on a failure day of a treatment step, with a probability that
follows from the failure frequency. Each treatment step is drawn independently.

*Why:* the source method counts 365 days per year. That only fits exposures with one event
per day. Drawing per exposure event works for every exposure, uses one calculation for one
or several failing steps, and fits the existing simulation. As a consequence, the number of
failure events varies between simulated years, as it does in reality. This widens the range
of annual risks.

## A failure event stops one of the parallel units

Many treatment steps consist of several parallel units, for example several UV reactors or
filters. A failure event is assumed to stop one of these units while the others keep
working. The water of the stopped unit passes untreated, the rest is treated as usual. A
step with one unit therefore loses its whole LRV during a failure. A step with two units
keeps a small LRV, because only half of the water is untreated.

*Why:* in most cases a treatment step does not lose all its removal during a failure. A
first idea, one reduction percentage for all pathogen groups, was dropped, because the same
percentage for viruses, bacteria and protozoa has no physical meaning. The number of
parallel units describes how the step is built, and the remaining LRV follows from it for
each pathogen group.

An important property follows from this: the untreated share limits what the step can
achieve during a failure. A step with two units keeps at most about 0.3 log, however high
its normal LRV is, and a step with ten units at most 1 log. Parallel units therefore help,
but they do not replace a working barrier.

## The failure duration counts in both cases

The water used on a failure day is assumed to be a mixture of water treated during the
failure and water treated in normal operation, in proportion to the failure duration (the
mixed-water assumption). A failure of 4 hours, for example, affects one sixth of the water
of that day. For each failing step, this gives a daily LRV that lies between its LRV during
the failure and its normal LRV.

Best-case and worst-case use the same rule. They differ only in the LRV a step starts from,
its maximum or minimum LRV, as in normal operation.

*Why:* an earlier version assumed in worst-case that all water used on a failure day had
been treated during the failure, so the duration had no effect in worst-case. Consistently,
best-case would then have to assume that the water was never treated during the failure,
and neither case would depend on the duration. That is not plausible. The duration is
better read as the probability that water used on a failure day was treated during the
failure: the longer the failure, the more likely this is. Using the same rule in both cases
keeps the range between best-case and worst-case a measure of the treatment performance
only.

## Water is mixed by concentration, not by LRV

The daily LRV is calculated from the mixed pathogen concentrations, not as an average of
the LRVs over the day.

*Why:* LRVs are logarithms. A small share of untreated water dominates the mixture, so an
average of the LRVs is far too optimistic. In the example below, it would give a failing UV
disinfection a daily LRV of 2.5 instead of 0.78.

## Combined failures add up without further rules

If several treatment steps fail on the same day, each failing step gets its own daily LRV,
and the daily LRVs of all steps are added up. This is the same as if each failure happened
at a random time of the day, independently of the other steps.

*Why:* the alternative, arranging failures within the day so that they overlap as little or
as much as possible, would need extra rules, for example for failures that add up to more
than one day. Treating the failures as independent avoids these rules and gives results
between the two extremes.

## Only positive LRVs are affected

A failure removes only the positive LRVs of a step. An LRV of 0 or below, which can be used
to describe recontamination, stays unchanged.

# Assumptions and limitations

- **Independent failures.** Failure days of different treatment steps are independent.
  Common causes, such as a power failure that stops several steps, are not modelled.
- **Units failing together.** Parallel units that fail together, for example through a
  shared power supply, are not modelled. Such a step should be entered with one unit.
- **Average concentration over the day.** The daily LRV uses the average concentration of
  the water used on a failure day. This is slightly more conservative than drawing for
  each exposure event whether it falls inside the failure.
- **Default duration.** With the default failure duration of 30 minutes, worst-case results
  are much less conservative than with a full loss for the whole day. The failure duration
  should therefore be set from operating experience.
- **Draft.** The approach and this text are to be reviewed by a domain expert before the
  release of the tool.

# Example

The example shows the effect of a failing UV disinfection on the infection risk from
*Cryptosporidium parvum* in drinking water (365 exposure events per year, 1 L per event).
The source water contains 0.1 to 10 oocysts per litre. The treatment train has two steps:
a filtration with a protozoa LRV of 2 to 3 and a UV disinfection with a protozoa LRV of 2.5
to 3. The values are illustrative and are not the default values of the tool. Only the UV
disinfection fails, on 10 days per year. The results were calculated with the tool.

| UV failure (10 days per year) | Best-case | Worst-case |
|---|---|---|
| No failures | 4.0 × 10^-5^ | 1.3 × 10^-3^ |
| 60 minutes, 1 unit | 8.1 × 10^-5^ | 1.7 × 10^-3^ |
| 60 minutes, 2 units | 6.1 × 10^-5^ | 1.5 × 10^-3^ |
| 4 hours, 1 unit | 2.0 × 10^-4^ | 2.9 × 10^-3^ |
| 4 hours, 2 units | 1.2 × 10^-4^ | 2.1 × 10^-3^ |
| 24 hours, 1 unit | 1.0 × 10^-3^ | 1.1 × 10^-2^ |

: Median annual probability of infection with *Cryptosporidium parvum*. The tolerable risk
level is 10^-4^ infections per person per year.

Without failures, best-case lies below the tolerable risk level of 10^-4^ per year. Ten
failure days of one hour double the best-case risk. With failures of four hours, best-case
exceeds the tolerable risk level by a factor of two; a second UV unit reduces this to just
above the level. A failure of a whole day on ten days per year raises the best-case risk
about 25-fold. Worst-case already exceeds the tolerable risk level without failures, and
failures raise it further.

The example also shows why the water is mixed by concentration. On a failure day with a
4-hour failure, the UV disinfection (LRV 3, one unit) reaches a daily LRV of 0.78. An
average of the LRVs over the day would give 2.5, which would hide most of the effect of the
failure.

# Differences from the source method

The approach follows Hambsch et al. (2019) in its main idea: failure days with a reduced
LRV, and the mixed-water assumption with the failure duration. It departs from it in three
points:

1. Failure days are drawn per exposure event instead of counting 365 days per year.
2. Worst-case uses the failure duration in the same way as best-case. In the source,
   worst-case removes the LRV of the failing step for the whole day.
3. The number of parallel units is new: in the source, a failing step always loses its
   whole LRV.

# Reference

Hambsch, B., Lipp, P., Ho, J. (2019): Modelhafte Prüfung und Konzeptentwicklung zur
quantitativen Risikobewertung der mikrobiellen Rohwasserbelastung für die
Trinkwasseraufbereitung (Abschlussbericht). DVGW-Förderkennzeichen W 201808.
Technologiezentrum Wasser, Karlsruhe.
