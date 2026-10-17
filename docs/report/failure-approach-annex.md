---
title: "Annex: algorithm of the treatment failure approach"
subtitle: "Annex text for the report (draft, 2026-10-17)"
---

# Overview

This annex describes the algorithm the QMRA tool uses to include treatment failures. It
gives all equations and simulation settings needed to rebuild a comparable calculation, for
example in a spreadsheet or in R. A worked hand calculation (section 9) and a short R script
(section 10) are included. Numbers in brackets refer to the equations.

The algorithm has two parts:

1. the QMRA Monte Carlo simulation without failures (sections 2 to 4), and
2. the failure extension, which changes the LRV of the treatment train for the exposure
   events that fall on a failure day (sections 5 to 7).

Everything is calculated separately for each reference pathogen and for the two cases:
best-case uses the maximum LRV of every treatment step, worst-case the minimum LRV.

# Inputs

| Symbol | Input | Unit | Range, default |
|---|---|---|---|
| $c_{min}$, $c_{max}$ | minimum and maximum pathogen concentration in the source water | pathogens per L | $c_{max} > 0$ |
| $E$ | exposure events per year | 1/year | whole number |
| $V$ | volume ingested per exposure event | L | |
| $LRV_{j}$ | LRV of treatment step $j$ for the pathogen group: maximum (best-case) or minimum (worst-case) | log~10~ | may be 0 or negative |
| $f_j$ | failure frequency of step $j$ | failure days per year | 0–365, default 0 |
| $t_j$ | failure duration of step $j$ | minutes | 1–1,440, default 30 |
| $N_j$ | number of parallel units of step $j$ | – | whole number ≥ 1, default 1 |

The failure inputs belong to the treatment step and apply to all three pathogen groups.

# Pathogen concentration and exposure events

The log~10~ concentration in the source water is normally distributed. The minimum and
maximum concentration are read as the limits of the range mean ± 2 standard deviations
(about the 2.5 % and 97.5 % percentiles):

$$\mu = \frac{\log_{10}(c_{min} + 10^{-8}) + \log_{10}(c_{max})}{2}, \qquad
\sigma = \frac{\log_{10}(c_{max}) - \log_{10}(c_{min} + 10^{-8})}{4} \qquad (1)$$

The term $10^{-8}$ only prevents $\log_{10}(0)$ for a minimum concentration of 0.

The tool draws $n_s$ = 10,000 log~10~ concentrations $x_1, \dots, x_{n_s}$ from
$\mathcal{N}(\mu, \sigma)$. It simulates $n_y$ = 1,000 years with $E$ exposure events
each. Every exposure event $(y, e)$ of year $y$ takes one of the $n_s$ concentrations,
drawn at random with replacement, $x_{y,e}$.

Both cases use the same concentrations and exposure events, so they differ only in their
LRVs.

# Dose, infection and annual risk

The dose of exposure event $(y, e)$ with the train LRV $LRV_{y,e}$ (section 7) is

$$D_{y,e} = 10^{\,x_{y,e} - LRV_{y,e}} \cdot V \qquad (2)$$

The probability of infection per exposure event follows the dose-response model of the
pathogen, exponential (3a) or beta-Poisson (3b):

$$p_{y,e} = 1 - e^{-k D_{y,e}} \qquad (3a)$$

$$p_{y,e} = 1 - \left(1 + D_{y,e}\,\frac{2^{1/\alpha} - 1}{N_{50}}\right)^{-\alpha} \qquad (3b)$$

| Reference pathogen | Pathogen group | Model | Parameters | Illness per infection | DALYs per case |
|---|---|---|---|---|---|
| Rotavirus | viruses | beta-Poisson | $\alpha = 0.253$, $N_{50} = 6.17$ | 0.5 | 0.014 |
| *Campylobacter jejuni* | bacteria | beta-Poisson | $\alpha = 0.144$, $N_{50} = 890$ | 0.3 | 0.0046 |
| *Cryptosporidium parvum* | protozoa | exponential | $k = 0.0572$ | 0.7 | 0.0015 |

The annual probability of infection of year $y$ combines its exposure events:

$$P_{y} = 1 - \prod_{e=1}^{E} \left(1 - p_{y,e}\right) \qquad (4)$$

The disease burden in DALYs per person per year is

$$DALY_{y} = P_{y} \cdot P_{ill|inf} \cdot DALY_{case} \qquad (5)$$

From the 1,000 annual values, the tool reports the minimum, 25 % percentile, median, 75 %
percentile and maximum for each case. A case exceeds the tolerable risk level if the mean
of its annual values exceeds $10^{-4}$ infections or $10^{-6}$ DALYs per person per year.

# Failure days

For each treatment step $j$ with $f_j > 0$, each exposure event $(y, e)$ falls on a failure
day of that step with probability

$$\pi_j = \frac{f_j}{365} \qquad (6)$$

independently for each step and each exposure event (a Bernoulli draw, $F_{j,y,e} = 1$ on
a failure day). The same failure days are used for both cases and for all three reference
pathogens.

Over many years, a step has on average $\pi_j \cdot E$ failure events per year, but the
number varies from year to year.

# Failure LRV and daily LRV of one step

**Failure LRV.** During a failure event, one of the $N_j$ parallel units is stopped. Its
share $1/N_j$ of the water is not treated; the share $(N_j-1)/N_j$ is treated with the
step's LRV. Mixed by concentration:

$$LRV_{fail,j} = -\log_{10}\left(\frac{N_j - 1}{N_j} \cdot 10^{-LRV_j} + \frac{1}{N_j}\right) \qquad (7)$$

For $N_j = 1$, $LRV_{fail,j} = 0$. For any LRV, $LRV_{fail,j} \le \log_{10} N_j$.

| $N$ | LRV 1 | LRV 2 | LRV 4 | LRV 6 |
|---|---|---|---|---|
| 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2 | 0.26 | 0.30 | 0.30 | 0.30 |
| 3 | 0.40 | 0.47 | 0.48 | 0.48 |
| 4 | 0.49 | 0.59 | 0.60 | 0.60 |
| 10 | 0.72 | 0.96 | 1.00 | 1.00 |

: Failure LRV (7) for selected LRVs and numbers of parallel units.

**Daily LRV.** The water used on a failure day is a mixture of water treated during the
failure (share $d_j$) and in normal operation (share $1-d_j$), with

$$d_j = \frac{t_j}{1440} \qquad (8)$$

The daily LRV of the failing step, again mixed by concentration, is

$$LRV_{day,j} = -\log_{10}\left(d_j \cdot 10^{-LRV_{fail,j}} + (1 - d_j) \cdot 10^{-LRV_j}\right) \qquad (9)$$

and the LRV the step loses on a failure day is

$$\Delta_j = LRV_j - LRV_{day,j} \qquad (10)$$

Equations (7) to (10) are applied with the maximum LRV in best-case and the minimum LRV in
worst-case. They are applied only to a positive LRV: if $LRV_j \le 0$, then $\Delta_j = 0$.
A failure frequency above 0 is only accepted for a step with at least one positive LRV.

Never average LRVs directly: for $LRV_j = 3$, $N_j = 1$ and $t_j = 240$ min, (9) gives 0.78,
whereas $(1 - d_j) \cdot LRV_j$ would give 2.5.

# Train LRV of an exposure event

The LRV of the treatment train for exposure event $(y, e)$ is the sum of the steps' LRVs,
minus the loss of every step that fails on that day:

$$LRV_{y,e} = \sum_{j} LRV_j - \sum_{j} F_{j,y,e} \cdot \Delta_j \qquad (11)$$

On a day with one failing step, the train LRV is the sum of the step's daily LRV and the
LRVs of the other steps. On a day with several failing steps (combined failure), the
losses add up. This equals placing each failure event at a random time of day,
independently of the other steps; no rules for overlapping failures are needed.

Equation (11) replaces $LRV_{y,e}$ in the dose (2); everything else stays as without
failures.

# Algorithm in steps

For each reference pathogen:

1. Calculate $\mu$ and $\sigma$ (1) and draw 10,000 log~10~ concentrations.
2. For 1,000 years × $E$ events, draw which concentration each event uses.
3. For each step with $f_j > 0$, draw the failure days $F_{j,y,e}$ (6), once for all
   pathogens and both cases.
4. For each case (maximum LRVs, minimum LRVs):
   a. calculate $\Delta_j$ of every step (7)–(10);
   b. calculate the train LRV of every event (11);
   c. calculate dose (2), probability of infection (3) and annual risk (4) and DALYs (5);
   d. summarise the 1,000 annual values and compare their mean with the tolerable risk
      levels.

The tool uses fixed random seeds, so a calculation can be repeated with the same result.
A rebuilt calculation with other random numbers gives results that agree within the Monte
Carlo variation (a few per cent for the median with 1,000 years).

# Worked hand calculation

This example can be rebuilt in a spreadsheet. It uses a fixed concentration of 1
*Cryptosporidium* oocyst per litre instead of the random draw, and exactly 10 failure days
per year instead of the random draw of failure days, so it shows only the failure part.

Inputs: drinking water, $E = 365$, $V = 1$ L; step A filtration, protozoa LRV 3 (best-case),
no failures; step B UV disinfection, protozoa LRV 3 (best-case), $f = 10$ days per year,
$t = 240$ min; $k = 0.0572$.

| Quantity | Equation | 1 unit | 2 units |
|---|---|---|---|
| Probability of a failure day per event | (6) | 0.0274 | 0.0274 |
| Failure LRV of UV | (7) | 0 | 0.30 |
| Failing share of the day $d$ | (8) | 0.1667 | 0.1667 |
| Daily LRV of UV | (9) | 0.776 | 1.074 |
| Train LRV, normal day | (11) | 6 | 6 |
| Train LRV, failure day | (11) | 3.776 | 4.074 |
| Dose, normal day (oocysts) | (2) | 1.00 × 10^-6^ | 1.00 × 10^-6^ |
| Dose, failure day (oocysts) | (2) | 1.68 × 10^-4^ | 8.42 × 10^-5^ |
| Probability of infection, normal day | (3a) | 5.72 × 10^-8^ | 5.72 × 10^-8^ |
| Probability of infection, failure day | (3a) | 9.58 × 10^-6^ | 4.82 × 10^-6^ |
| Annual probability, 355 normal and 10 failure days | (4) | 1.16 × 10^-4^ | 6.85 × 10^-5^ |
| Annual probability without failures | (4) | 2.09 × 10^-5^ | 2.09 × 10^-5^ |

With exactly $n$ failure days, (4) becomes
$P = 1 - (1 - p_{normal})^{365 - n} \cdot (1 - p_{failure})^{n}$, which is Eq. 6 of
Hambsch et al. (2019). The tool draws the failure days instead, so its results agree with
this formula only on average.

For a spreadsheet Monte Carlo version: one row per exposure event and one block of $E$ rows
per simulated year; columns for the random concentration (`NORM.INV(RAND(); μ; σ)`), one
column per failing step with `RAND() < f/365`, the train LRV (11), the dose (2) and the
probability (3); then (4) per year as `1 - PRODUCT(1 - p)` over the year's rows. Fewer years
than 1,000 give a rougher distribution.

# R script

The following script rebuilds the calculation for one pathogen with an exponential
dose-response model. It uses R's own random numbers, so results differ from the tool within
the Monte Carlo variation.

```r
set.seed(1)
n_years <- 1000; n_samples <- 10000
E <- 365; V <- 1                 # exposure events per year, litres per event
c_min <- 0.1; c_max <- 10        # pathogens per litre
k <- 0.0572                      # exponential dose-response (Cryptosporidium parvum)
steps <- data.frame(             # one row per treatment step
  lrv_max = c(3, 3), lrv_min = c(2, 2.5),
  freq = c(0, 10), duration = c(30, 240), units = c(1, 1))

mu    <- (log10(c_min + 1e-8) + log10(c_max)) / 2             # (1)
sigma <- (log10(c_max) - log10(c_min + 1e-8)) / 4
log_c <- rnorm(n_samples, mu, sigma)
x <- matrix(log_c[sample.int(n_samples, n_years * E, replace = TRUE)], n_years, E)

failing <- lapply(steps$freq, function(f)                     # (6), shared by both cases
  matrix(runif(n_years * E) < f / 365, n_years, E))

failure_lrv <- function(lrv, n) -log10((n - 1) / n * 10^-lrv + 1 / n)          # (7)
daily_lrv <- function(lrv, duration, n) {                                       # (8), (9)
  d <- duration / 1440
  -log10(d * 10^-failure_lrv(lrv, n) + (1 - d) * 10^-lrv)
}

annual_risk <- function(lrv) {   # lrv: each step's maximum or minimum LRV
  train_lrv <- matrix(sum(lrv), n_years, E)
  for (j in seq_len(nrow(steps))) {
    if (steps$freq[j] > 0 && lrv[j] > 0) {
      loss <- lrv[j] - daily_lrv(lrv[j], steps$duration[j], steps$units[j])     # (10)
      train_lrv[failing[[j]]] <- train_lrv[failing[[j]]] - loss                 # (11)
    }
  }
  dose <- 10^(x - train_lrv) * V                                                # (2)
  p <- 1 - exp(-k * dose)                                                       # (3a)
  1 - apply(1 - p, 1, prod)                                                     # (4)
}

best <- annual_risk(steps$lrv_max)
worst <- annual_risk(steps$lrv_min)
rbind(best = quantile(best), worst = quantile(worst))
c(best = mean(best) > 1e-4, worst = mean(worst) > 1e-4)    # exceeds the tolerable risk level
```

For these inputs the tool gives a median annual probability of infection of about
2.0 × 10^-4^ (best-case) and 2.9 × 10^-3^ (worst-case).

# Differences from Hambsch et al. (2019)

| Topic | Hambsch et al. (2019) | QMRA tool |
|---|---|---|
| Failure days | 365 days per year; Eq. 6 for one failing step, random 365-day sequence for several | random draw per exposure event (6) |
| Worst-case on a failure day | LRV of the failing step removed for the whole day | daily LRV (9) with the failure duration, as in best-case |
| Best-case on a failure day | mixed-water assumption (Eq. 5) | daily LRV (9); same result with one unit |
| LRV during the failure | 0 | failure LRV (7) from the number of parallel units |
| Combined failures | an LRV for each combination of failing steps, not further specified | losses added up (11) |

# Reference

Hambsch, B., Lipp, P., Ho, J. (2019): Modelhafte Prüfung und Konzeptentwicklung zur
quantitativen Risikobewertung der mikrobiellen Rohwasserbelastung für die
Trinkwasseraufbereitung (Abschlussbericht). DVGW-Förderkennzeichen W 201808.
Technologiezentrum Wasser, Karlsruhe.
