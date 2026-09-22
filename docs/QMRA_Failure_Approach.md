# Integration of Failure Events into the QMRA Framework

## Current Calculation of the infection risk

All equations in this chapter are taken from Hambsch et al., 2019, pp. 61.

The annual risk of infection is described as the product of the daily risks of infection

| Eq. 1 | ${P}_{inf-year}=1-\prod_{i=1}^{365} \left( 1-{p}_{inf-day,i} \right)$ |
|---|---|
| with | ${P}_{inf-year}$: Annual risk of infection<br>${p}_{inf-day,i}$: Daily risk of infection on day i |

The daily risk of infection, again, depends on

1. the initial concentration before treatment
2. the removal efficiency throughout the entire treatment chain, expressed as log removal (LRV)
3. the specific probability of infection per pathogen: r
4. the volume ingested: V

| Eq. 2 | ${p}_{inf-day}=1-{e}^{-\frac{r{c}_{in}V}{{10}^{LRV}}}$ |
|---|---|
| with | ${p}_{inf-day}$: Daily risk of infection<br>$r$: Specific probability of infection [per pathogen]<br>${c}_{in}$: Input concentration [Pathogen per Liter]<br>$V$: Ingested volumen [Liter]<br>$LRV$: Log-removal throughout the entire treatment chain |

Accordingly, the risk of infection is 0 if either the specific probability of infection per pathogen, the concentration of the pathogen in the influent, or the volume ingested is equal to 0.

Furthermore, the risk approaches 0 as the log-removal in the treatment chain increases.

In the QMRA tool, the inlet concentration for each day is drawn from a distribution as part of a Monte Carlo simulation. The calculation is performed in two scenarios: one for the best-case scenario (maximum log removal per process: LRV_max) and one for the worst-case scenario (minimum log removal per process: LRV_min).

The distribution of the infection risk is therefore based on the distribution of the input concentration and is calculated for each scenario using separate LRVs.

## Calculation of LRVs with failure events

The distinction between best-case and worst-case scenarios remains the same in the event of a failure.

The specific probability of infection, the initial concentration, and the volume ingested do not change as a result of the failure. The LRV, however, is directly affected by the failure of a treatment step. Depending on the scenario, a distinction should also be made between whether the treated water was consumed exclusively during the failure event (worst-case) or whether it was a mixture of water from normal operation and the failure event (best-case)—as is likely often the case when water is stored somewhere.

If a treatment step in the treatment chain fails, the total LRV is reduced by the treatment-specific LRV. This is calculated for both scenarios.

| Eq. 3 / Eq. 4 | $LRV_{failure,min}=LRV_{min}-LRV_{treatment,min}$<br>$LRV_{failure,max}=LRV_{max}-LRV_{treatment,max}$ |
|---|---|
| with | $LRV_{failure,min}\ \text{and}\ LRV_{failure,max}$: Minimum and maximum log-removal of the entire treatment chain during the failure event<br>$LRV_{treatment,min}\ \text{and}\ LRV_{treatment,max}$: Minimum and maximum log-removal of the failing treatment step |

In the worst-case scenario, the minimum LRV is used directly to calculate the daily risk of infection in the event of an incident. In the best-case scenario, the mixed concentration is calculated using the following equation:

| Eq. 5 | $LRV_{failure,mix}=-\log \left( \frac{{x}_{fail}}{{10}^{LRV_{failure,max}}}+\frac{1-{x}_{fail}}{{10}^{LRV_{max}}} \right)$ |
|---|---|
| with | $LRV_{failure,mix}$: Average log-removal of the entire treatment train with failure event<br>${x}_{fail}$: Time portion of the failure event calculated as the duration of the failure in minutes divided by 1,440 min |

For the best-case scenario, the duration of the failure is therefore required as an additional input variable.

The daily infection risk is calculated using Equation 2, in the same way as for the calculation without damage. When calculating the annual infection risk, a distinction must then be made between days with and without failure.

| Eq. 6 | ${P}_{inf-year}=1-{\left( 1-P_{inf-day,normal} \right)}^{365-n}{\left( 1-{P}_{inf-day,failure} \right)}^{n}$ |
|---|---|
| with | ${P}_{inf-year}$: Annual risk of infection<br>$P_{inf-day,normal}$: Daily risk of infection without failure<br>${P}_{inf-day,failure}$: Daily risk of infection with failure<br>$n$: Frequency of failure events in days per year |

The day of the year on which the failure occurs or time of the failure within a given day is not relevant for the calculation.

**Required information in the QMRA tool for integrating failure events:**

- **Average duration of the failure in minutes (integers between 1 and 1440)  Default 30 min**
- **Frequency of failure events in days per year (float between 0 and 365)  Default is 0**

## Next Step: Combination of damage across multiple technologies

Information on the frequency of damage is available for each treatment step. From this information, a sequence of length 365 consisting of zeros and ones can be randomly selected, where zeros represent days without a damage event and ones represent days with a damage event. The draw is performed using a binomial distribution, in which the probability corresponds to the number of days per year (e.g., 1.37% for 5 days per year means that for each day, a 1 is drawn with a probability of 1.37%). This results in years in which there may be more or fewer damage events than assumed. The random draws become part of the Monte Carlo simulation and can thus be accounted for along with the varying input concentrations.

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

For each combination of damages, an LRV must then be calculated for the best-case and worst-case scenarios, and Equation 6 must be extended accordingly.

## Literatur

Hambsch, Beate, Lipp, Pia, Ho, Johannes, 2019. Modelhafte Prüfung und Konzeptentwicklung zur quantitativen Risikobewertung der mikrobiellen Rohwasserbelastung für die Trinkwasseraufbereitung (Abschlussbericht), DVGW-Förderkennzeichen W 201808. Technologiezentrum Wasser, Karlsruhe.
