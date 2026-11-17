Treatment failure
=================

.. note::

    Draft written by Claude for review by a domain expert before the release.

A treatment step does not always reach its LRV. The tool can include **failure events**:
periods in which a treatment step works only partly or not at all. This page describes how
the result uses them. The method follows the failure approach of Hambsch et al. (2019),
with the differences listed at the end.

Failure inputs
##############

Each treatment step has three failure inputs. They apply to all pathogen groups of the step.

#. **Failure frequency** (days per year): the expected number of failure days per year of
   the step, from 0 to 365, default 0. With 0 the step never fails. Only a step with at least
   one positive LRV can have a failure frequency above 0.
#. **Failure duration** (minutes): the average length of one failure event, from 1 to 1,440
   minutes (one day), default 30.
#. **Number of parallel units**: how many equal units share the water of the step, a whole
   number of 1 or more, default 1, without an upper limit.

The failure frequency counts the failure days of the whole step, whichever of its units
fails.

Failure days per exposure event
###############################

The tool builds the annual risk from exposure events, not from days: it samples the dose of
each exposure event and combines as many events as the exposure has per year. For each
exposure event, it draws whether the event falls on a failure day of a treatment step, with
probability

.. math::

    p = \frac{failure\:frequency}{365}

independently for each step. Both cases (best-case and worst-case) and all reference
pathogens use the same failure days. The number of failure events therefore varies between
simulated years, which widens the risk distribution: failures are random.

The source method instead counts 365 days per year and draws a 365-day sequence of failure
days. That would only fit an exposure with one event per day, such as drinking water. For an
exposure such as irrigation with 20 events per year, "5 failure days per year" has no direct
meaning for the calculation, so the tool draws per exposure event (ADR-0001).

Failure LRV
###########

A failure event stops one of the step's *N* parallel units while the others keep working.
The water is shared equally between the units, so 1/*N* of the water is not treated and
(*N* − 1)/*N* is treated with the step's LRV. The two are mixed by pathogen concentration,
which gives the step's LRV during the failure, the **failure LRV**:

.. math::

    LRV_{fail} = -\log_{10}\left(\frac{N-1}{N} \cdot 10^{-LRV} + \frac{1}{N}\right)

With one unit, the failure LRV is 0. Because of the untreated share, it is at most
log\ :sub:`10` *N*, however high the step's LRV is (ADR-0002):

+---------------+--------------+--------------+--------------+--------------+
| Units *N*     | LRV 1        | LRV 2        | LRV 4        | LRV 6        |
+===============+==============+==============+==============+==============+
| 1             | 0.00         | 0.00         | 0.00         | 0.00         |
+---------------+--------------+--------------+--------------+--------------+
| 2             | 0.26         | 0.30         | 0.30         | 0.30         |
+---------------+--------------+--------------+--------------+--------------+
| 3             | 0.40         | 0.47         | 0.48         | 0.48         |
+---------------+--------------+--------------+--------------+--------------+
| 4             | 0.49         | 0.59         | 0.60         | 0.60         |
+---------------+--------------+--------------+--------------+--------------+
| 10            | 0.72         | 0.96         | 1.00         | 1.00         |
+---------------+--------------+--------------+--------------+--------------+

Because the formula uses each pathogen group's own LRV, the effect differs between pathogen
groups. Units of a step that fail together, for example through a shared power supply, are
not modeled; enter such a step with one unit.

Daily LRV
#########

The tool follows the **mixed-water assumption**: the water used on a failure day is a
mixture of water treated during the failure event and water treated in normal operation, in
proportion to the failure duration. With *d* = failure duration / 1,440 min, the share of
the day the step is down, each failing step gets a **daily LRV**:

.. math::

    LRV_{day} = -\log_{10}\left(d \cdot 10^{-LRV_{fail}} + (1 - d) \cdot 10^{-LRV}\right)

The mixture is averaged by concentration, never by LRV: an average of the LRVs would be far
too optimistic (see the example below).

Best-case and worst-case use the same rule (ADR-0002). They differ only in the LRV a step starts
from, as in normal operation: *LRV* is the step's maximum LRV in best-case and its minimum
LRV in worst-case, and the failure LRV follows from it. The failure duration therefore
affects both cases. For example, with the default duration of 30 minutes, a step with an LRV
of 4 and one unit has a daily LRV of 1.68 on a failure day.

The treatment train's LRV on a failure day is the sum of the daily LRVs of its failing steps
and the LRVs of the other steps.

Only positive LRVs are affected by a failure. An LRV of 0 or below, for example to
simulate recontamination, stays unchanged on a failure day.

Combined failures
#################

If several steps fail on the same day, each failing step gets its own daily LRV, and the
daily LRVs are added up. This equals placing each failure event at a random time of day,
independently of the other steps, so no further rules are needed, also when the failure
durations add up to more than a day.

Worked example (``docs/failure-daily-lrv-example.md``): a treatment train of two steps, A with
an LRV of 4 and B with an LRV of 3, one unit each, so the train LRV is 7 in normal
operation.

- Only A fails, for 60 minutes: the train LRV of that day is 4.38.
- A and B both fail on the same day, each for the same duration:

  ========================= ====================
  Failure duration per step Train LRV of the day
  ========================= ====================
  60 min                    2.75
  4 h                       1.55
  12 h                      0.60
  16 h                      0.35
  ========================= ====================

An average of the LRVs over the day would give 6.71 instead of 2.75 for the 60-minute case.

Two steps fail on the same day only rarely: with 10 failure days per year each, about 0.08 %
of the exposure events. Combined failures change the annual risk noticeably only with high
failure frequencies or long failure durations.

Differences from the source method
##################################

The tool departs from Hambsch et al. (2019) in two points:

#. **Failure days are drawn per exposure event** (ADR-0001), instead of counting 365 days
   with a closed formula for one failing step (Eq. 6) or a random 365-day sequence for
   several. With one failing step, best-case results therefore agree with a hand calculation
   with Eq. 5 and Eq. 6 only on average; worst-case differs from Eq. 6 also because of the
   second point.
#. **Worst-case uses the failure duration** (ADR-0002). In the source, worst-case removes the
   failing step's LRV on a failure day without the duration, and only best-case uses the
   mixed-water assumption (Eq. 5). In the tool, both cases use the daily LRV.

Sources
#######

- ADR-0001, failure days drawn per exposure event (``docs/adr/0001-failure-days-drawn-per-exposure-event.md``)
- ADR-0002, one daily LRV rule for both cases, with parallel units
  (``docs/adr/0002-one-daily-lrv-rule-and-parallel-units.md``)
- The failure approach and its decisions (``docs/QMRA_Failure_Approach.md``)
- Worked example of the daily LRV (``docs/failure-daily-lrv-example.md``)
- Hambsch, B., Lipp, P., Ho, J. (2019): Modelhafte Prüfung und Konzeptentwicklung zur
  quantitativen Risikobewertung der mikrobiellen Rohwasserbelastung für die
  Trinkwasseraufbereitung (Abschlussbericht), DVGW-Förderkennzeichen W 201808.
  Technologiezentrum Wasser, Karlsruhe.
