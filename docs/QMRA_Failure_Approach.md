# Integration of Failure Events into the QMRA Framework

## Current Calculation of the infection risk

All equations in this chapter are taken from Hambsch et al., 2019, pp. 61.

The annual risk of infection is described as the product of the daily risks of infection

| Eq. 1 | ${P}_{inf-year}=1-\prod_{i=1}^{365} \left( 1-{p}_{inf-day,i} \right)$ |
|---|---|
| with | ${P}_{inf-year}$: Annual risk of infection<br>${p}_{inf-day,i}$: Daily risk of infection on day i |

The daily risk of infection, again, depends on

1. the inflow concentration
2. the log-removal value (LRV) of the entire treatment train
3. the specific probability of infection per pathogen: r
4. the volume ingested: V

| Eq. 2 | ${p}_{inf-day}=1-{e}^{-\frac{r{c}_{in}V}{{10}^{LRV}}}$ |
|---|---|
| with | ${p}_{inf-day}$: Daily risk of infection<br>$r$: Specific probability of infection [per pathogen]<br>${c}_{in}$: Inflow concentration [Pathogen per Liter]<br>$V$: Ingested volume [Liter]<br>$LRV$: Log-removal of the entire treatment train |

Accordingly, the risk of infection is 0 if either the specific probability of infection per pathogen, the inflow concentration, or the volume ingested is equal to 0.

Furthermore, the risk approaches 0 as the log-removal of the treatment train increases.

In the QMRA tool, the inflow concentration for each exposure event is drawn from a distribution as part of a Monte Carlo simulation. The calculation is performed in two cases: best-case (maximum LRV per treatment step: LRV_max) and worst-case (minimum LRV per treatment step: LRV_min).

The distribution of the infection risk is therefore based on the distribution of the inflow concentration and is calculated for each case using separate LRVs.

## Calculation of LRVs with failure events

The distinction between best-case and worst-case remains the same on failure days.

The specific probability of infection, the inflow concentration, and the volume ingested do not change as a result of the failure. The LRV, however, is directly affected by the failure of a treatment step. Depending on the case, a distinction should also be made between whether the treated water was consumed exclusively during the failure event (worst-case) or whether it was a mixture of water from normal operation and the failure event (best-case, the mixed-water assumption)—as is likely often the case when water is stored somewhere.

If a treatment step in the treatment train fails, the total LRV is reduced by the treatment-specific LRV. This is calculated for both cases.

| Eq. 3 / Eq. 4 | $LRV_{failure,min}=LRV_{min}-LRV_{treatment,min}$<br>$LRV_{failure,max}=LRV_{max}-LRV_{treatment,max}$ |
|---|---|
| with | $LRV_{failure,min}\ \text{and}\ LRV_{failure,max}$: Minimum and maximum log-removal of the entire treatment train during the failure event<br>$LRV_{treatment,min}\ \text{and}\ LRV_{treatment,max}$: Minimum and maximum log-removal of the failing treatment step |

In worst-case, $LRV_{failure,min}$ is used directly to calculate the daily risk of infection on a failure day. In best-case, the mixed-water assumption gives an average LRV using the following equation:

| Eq. 5 | $LRV_{failure,mix}=-\log \left( \frac{{x}_{fail}}{{10}^{LRV_{failure,max}}}+\frac{1-{x}_{fail}}{{10}^{LRV_{max}}} \right)$ |
|---|---|
| with | $LRV_{failure,mix}$: Average log-removal of the entire treatment train with failure event<br>${x}_{fail}$: Time portion of the failure event calculated as the duration of the failure in minutes divided by 1,440 min |

For best-case, the failure duration is therefore required as an additional input variable.

The daily infection risk is calculated using Equation 2, in the same way as for the calculation without failure. When calculating the annual infection risk, a distinction must then be made between days with and without failure.

| Eq. 6 | ${P}_{inf-year}=1-{\left( 1-P_{inf-day,normal} \right)}^{365-n}{\left( 1-{P}_{inf-day,failure} \right)}^{n}$ |
|---|---|
| with | ${P}_{inf-year}$: Annual risk of infection<br>$P_{inf-day,normal}$: Daily risk of infection without failure<br>${P}_{inf-day,failure}$: Daily risk of infection with failure<br>$n$: Failure frequency in failure days per year |

The day of the year on which the failure occurs or time of the failure within a given day is not relevant for the calculation.

**Required information in the QMRA tool for integrating failure events, per treatment step:**

- **Failure duration: average duration of one failure event in minutes (integers between 1 and 1440)  Default 30 min**
- **Failure frequency: failure days per year (float between 0 and 365)  Default is 0**

## Next Step: Combined failures across multiple treatment steps

A failure frequency is given for each treatment step. From this information, a sequence of length 365 consisting of zeros and ones can be randomly selected, where zeros represent days without a failure event and ones represent failure days. The draw is performed using a binomial distribution, in which the probability corresponds to the number of days per year (e.g., 1.37% for 5 days per year means that for each day, a 1 is drawn with a probability of 1.37%). This results in years in which there may be more or fewer failure events than assumed. The random draws become part of the Monte Carlo simulation and can thus be accounted for along with the varying inflow concentrations.

This process is carried out for each treatment step, so it is possible that several treatment steps could fail at the same time, although this is rather unlikely given the expected low frequency of such occurrences.

The following table shows an example of one week in a year.

|  | Failure (1: yes, 0: no) |  |  | LRV |
|---|---|---|---|---|
| Day | Tech1 | Tech2 | Tech3 |  |
| 1 | 0 | 1 | 1 | Failure, Tech2-Tech3 |
| 2 | 0 | 0 | 0 | Normal |
| 3 | 0 | 0 | 0 | Normal |
| 4 | 1 | 0 | 0 | Failure, Tech1 |
| 5 | 0 | 0 | 0 | Normal |
| 6 | 0 | 0 | 0 | Normal |
| 7 | 0 | 0 | 1 | Failure, Tech3 |

For each combination of failing treatment steps, an LRV must then be calculated for best-case and worst-case, and Equation 6 must be extended accordingly.

## Decisions (2026-09-23)

Agreed in a domain-modeling session. Terms follow `CONTEXT.md`; the calculation approach
is recorded in `docs/adr/0001-failure-days-drawn-per-exposure-event.md`.

1. **Entire loss only.** A failing treatment step loses its entire LRV, for all three
   pathogen groups at once. Partial loss of removal is not modelled and not planned.
2. **Which steps can fail.** Any treatment step with a positive LRV, including
   non-technical measures such as hygiene practices. Recontamination steps (negative LRV)
   cannot fail. A step fails only if its failure frequency is above zero.
3. **Inputs per treatment step.** Each step has one failure frequency (failure days per
   year, 0–365, default 0) and one failure duration (minutes, 1–1440, default 30). They
   are the same in best-case and worst-case. They are user input only; there is no
   bundled failure data. They belong to the scenario, and a personal treatment step can
   store them for reuse.
4. **Worst-case ignores the failure duration.** On a failure day, worst-case assumes all
   consumed water was treated during the failure event, so a 1-minute and a 24-hour
   failure give the same result. Only best-case uses the duration (Eq. 5, the
   mixed-water assumption).
5. **Draws per exposure event, one calculation path.** The application builds yearly risk
   from exposure events, not from 365 days. Each exposure event falls on a failure day of
   each treatment step independently, with probability failure frequency / 365, inside
   the existing Monte Carlo simulation. The section-3 approach is implemented directly;
   Eq. 6 is not implemented as a separate path, not even for a single failing step. See
   ADR-0001.
6. **Combined failures in best-case.** Eq. 5 is extended so that failure events of
   different steps on the same day overlap as little as possible: not at all if their
   durations fit into 1,440 minutes, otherwise only by the minutes beyond a full day.
   Example (best-case LRV 10 = UV 4 + UF 4 + other steps 2): UV down 60 min and UF down
   120 min give 4.2 % of the day at LRV 6, 8.3 % at LRV 6 and 87.5 % at LRV 10, a mixed
   LRV of about 6.9. UV and UF each down 900 min overlap by 360 min: 25 % at LRV 2 and
   2 × 37.5 % at LRV 6, a mixed LRV of about 2.6. Worst-case loses all failing steps'
   LRVs for the whole day.
7. **Results.** Only the result including failures is shown, and the reference-level
   exceedance is taken on it. The effect of failures is seen by comparing scenarios with
   different failure inputs in the assessment comparison view.
8. **Still steady-state.** Failure frequency and duration are the same every year and
   results are yearly, so a scenario with failures remains a steady-state scenario.

## Literatur

Hambsch, Beate, Lipp, Pia, Ho, Johannes, 2019. Modelhafte Prüfung und Konzeptentwicklung zur quantitativen Risikobewertung der mikrobiellen Rohwasserbelastung für die Trinkwasseraufbereitung (Abschlussbericht), DVGW-Förderkennzeichen W 201808. Technologiezentrum Wasser, Karlsruhe.
