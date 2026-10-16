# QMRA Web Application

A web tool for quantitative microbial risk assessment of water: a user describes a source water, a treatment train and an exposure, and the tool estimates the yearly infection risk and health burden for three reference pathogens. Bounded to steady-state scenarios; process design is out of scope, and treatment failure is next phase.

## Language

### Assessment

**Assessment**:
A scenario together with the results of its risk calculation. Scenarios are compared by comparing assessments.
_Avoid_: risk assessment (in prose), calculation, run, project

**Scenario**:
The inputs of a risk calculation: inflow concentrations, a treatment train and an exposure. The failure frequency, failure duration and number of parallel units of each treatment step belong to the scenario, so scenarios can differ only in their failures. Each scenario is calculated in two cases, best-case and worst-case.
_Avoid_: case (reserved for best-case and worst-case), configuration

**Saved assessment**:
An assessment stored under a registered user's account so it can be listed, reopened, edited, deleted or exported.

**Guest assessment**:
An assessment run without an account. Its results are shown once and nothing is stored.
_Avoid_: free trial, anonymous assessment

**Assessment configurator**:
The form-based interface for entering or selecting assessment inputs.
_Avoid_: wizard, editor

**Export package**:
A ZIP containing the assessment's input tables, result table, HTML report and plots.
_Avoid_: download, report (the report is one file inside the package)

### Inputs

**Source water**:
A named type of water before treatment, such as raw sewage or protected surface water. A source water is described by one inflow concentration per reference pathogen.
_Avoid_: source, water type, feed water

**Site-specific source water**:
A source water in an assessment whose inflow concentrations were entered or changed by hand, even a single value, or entered without selecting any source water. It is not a bundled source water any more, even if it was derived from one, and is not called by the bundled name.
_Avoid_: custom source water, modified source water, calling it by the unprefixed bundled name

**Inflow concentration**:
The concentration of one reference pathogen in the source water entering the treatment train, in organisms per litre, given as a minimum and a maximum. An assessment has one inflow concentration per selected pathogen.
_Avoid_: inflow (alone), concentration (alone), concentration range, pathogen input, source concentration

**Outflow concentration**:
The concentration of one reference pathogen leaving the treatment train: the inflow concentration reduced by the train's LRV for the pathogen's group. It is calculated, never entered, and differs between best-case and worst-case. It determines the dose ingested per exposure event.
_Avoid_: outflow (alone), treated concentration, effluent concentration, dose

**Exposure**:
The assumed human contact with the treated water, given as events per year and ingested volume per event in litres.
_Avoid_: exposure scenario, ingestion, use

**Treatment step**:
Any step between source water and exposure that changes the pathogen concentration, with a minimum and maximum log-removal value per pathogen group. It can be a treatment technology or process, a non-technical measure such as a hygiene practice, or recontamination.
_Avoid_: treatment (alone, when a step is meant), barrier, process, technology

**Recontamination**:
A treatment step with a negative LRV, representing pathogens entering the water after treatment, for example in storage or distribution.
_Avoid_: negative treatment, contamination step

**Treatment train**:
The ordered sequence of treatment steps in a scenario. Its removal is the sum of the steps' LRVs per pathogen group.
_Avoid_: treatment chain, process chain, treatment list

**Log-removal value (LRV)**:
A logarithmic measure of pathogen reduction by a treatment step. Each step carries a minimum and a maximum LRV for bacteria, viruses and protozoa.
_Avoid_: log reduction, removal efficiency, log credit

**Reference pathogen**:
One of the three pathogens the model calculates risk for: Rotavirus, Campylobacter jejuni and Cryptosporidium parvum. Each stands for its pathogen group.
_Avoid_: organism, indicator, microbe

**Pathogen group**:
One of bacteria, viruses or protozoa. LRVs are defined per group; each reference pathogen belongs to exactly one group.
_Avoid_: pathogen class, pathogen type

### Data origin

**Bundled default data**:
Source waters, inflow concentrations, treatment steps, exposures, pathogens and references shipped with the application.
_Avoid_: defaults, static data, system data, library

**Personal definition**:
A reusable source water, exposure or treatment step created by a registered user and offered alongside the bundled defaults. A personal treatment step can carry its own failure frequency and failure duration.
_Avoid_: custom entry, user data, own data

**Site-specific input**:
A value typed in for one assessment to represent local evidence. The application does not check that it is representative.
_Avoid_: custom value, manual value, override

**Reference**:
A literature citation attached to a bundled inflow concentration, exposure or LRV to show where the value came from.
_Avoid_: source (collides with source water), citation, literature

**Provenance**:
The full record of where every input, parameter and interpretation in an assessment came from. Only partly captured today through references.

### Calculation

**Dose-response model**:
The relationship between the ingested dose of a reference pathogen and the probability of infection per event. Each reference pathogen uses one fitted model, exponential or beta-Poisson.
_Avoid_: infection model, dose model

**Monte Carlo simulation**:
Repeated random sampling of inflow concentrations and exposure events to estimate a distribution of yearly risk instead of one number.
_Avoid_: stochastic run, sampling

**Best-case**:
The case of a scenario that gives the lower infection-risk estimate. It uses every treatment step's maximum LRV, in normal operation and as the starting point of the daily LRV on failure days.
_Avoid_: maximum-LRV case, minimum risk scenario, optimistic case

**Worst-case**:
The case of a scenario that gives the higher infection-risk estimate. It uses every treatment step's minimum LRV, in normal operation and as the starting point of the daily LRV on failure days.
_Avoid_: minimum-LRV case, maximum risk scenario, conservative case

**Annual probability of infection**:
The estimated probability that a person is infected at least once in one year of exposure.
_Avoid_: infection risk (alone), yearly risk

**DALYs per person per year**:
The estimated health burden in disability-adjusted life years per person per year, derived from the annual probability of infection through the pathogen's illness-to-infection ratio and burden per case.
_Avoid_: DALY, burden, health impact

**Risk measure**:
One of the two outcomes the application reports per reference pathogen: annual probability of infection or DALYs per person per year.
_Avoid_: metric, indicator, risk type

**Risk distribution**:
The set of sampled yearly outcomes for one reference pathogen in best-case or worst-case, summarised by minimum, quartiles, median and maximum.
_Avoid_: result set, spread

**Health-based reference level**:
A comparison value shown next to results: one infection per ten thousand persons per year and one millionth DALY per person per year. It is not a legal limit.
_Avoid_: legal limit, tolerable risk level, guideline value, threshold

**Reference-level exceedance**:
The verdict for one reference pathogen and one risk measure: whether the mean result exceeds the health-based reference level in both best-case and worst-case, only in worst-case, or in neither.
_Avoid_: risk category, risk flag, pass/fail

**Uncertainty**:
Variation or lack of knowledge in an assessment. Represented today only through inflow concentration ranges, random sampling and the spread between best-case and worst-case.

### Boundaries

**Steady-state scenario**:
A scenario whose inputs are assumed to be the same every year: source water, exposure, treatment performance and, once modelled, failure frequency and failure duration. Results are given per year, never per day, so a scenario with treatment failures is still steady-state. This is the only kind the application models.

**Normal operation**:
Every treatment step performing within its configured minimum and maximum LRVs. The only state the application models today.
_Avoid_: regular operation, steady operation

**Treatment failure**:
One parallel unit of a treatment step stopping for a period, so that the water it handles is not treated while it lasts. A step with one unit loses all its positive LRVs during the failure; a step with more units keeps the share treated by the other units (failure LRV). LRVs of zero or below are not affected: a step with regrowth for one pathogen group keeps that negative LRV during a failure. Any treatment step with at least one positive LRV can fail, including non-technical measures; recontamination, having no positive LRV, cannot. A step fails only if it has a failure frequency above zero. Partial loss of removal is modelled only through parallel units. Not modelled today; a next-phase concept.
_Avoid_: damage, incident, outage, malfunction, downtime (alone)

**Failure event**:
One occurrence of a treatment failure in one treatment step. It stops one parallel unit of the step. A step has at most one failure event per day.
_Avoid_: damage event, incident

**Failure day**:
A day on which at least one treatment step has a failure event. Exposure events on a failure day are calculated with the daily LRV of each failing step.
_Avoid_: damage day, incident day

**Failure frequency**:
The expected number of failure days per year for one treatment step, counting a day on which any one of its parallel units fails. It is zero unless the user enters it. Which days fail is drawn at random, so a simulated year can have more or fewer failure days than expected.
_Avoid_: failure rate, failure probability

**Failure duration**:
The average length of one failure event of one treatment step, in minutes within a day. It sets the share of the day weighted with the failure LRV in the daily LRV, in best-case and worst-case.
_Avoid_: downtime, outage time

**Parallel units**:
The number of equal units of a treatment step that share its water, a whole number of 1 or more (default 1). A failure event stops one unit while the others keep working. Units failing together, for example through a shared power supply, are not modelled; such a step is entered with one unit. Every treatment step that accepts failure inputs has it, and a personal treatment step can store it.
_Avoid_: lines, trains (reserved for treatment train), redundancy

**Failure LRV**:
The LRV of one treatment step while one of its N parallel units is stopped: −log10((N − 1)/N · 10^−LRV + 1/N), with the untreated and the treated water mixed by concentration. It is 0 for one unit and at most log10 N, for example 0.3 for two units. LRVs of zero or below stay unchanged.
_Avoid_: reduced LRV, residual LRV

**Mixed-water assumption**:
The assumption, in best-case and worst-case, that water consumed on a failure day is a mixture of water treated during the failure event and water treated in normal operation, in proportion to the failure duration.
_Avoid_: mixed concentration, dilution, storage effect

**Daily LRV**:
The LRV of one failing treatment step on a failure day under the mixed-water assumption: −log10(d · 10^−failure LRV + (1 − d) · 10^−LRV), with d = failure duration / 1440 minutes, averaged by concentration, never by LRV. The LRV is the step's maximum LRV in best-case and its minimum LRV in worst-case. The treatment train's LRV on a failure day is the sum of the daily LRVs of its failing steps and the LRVs of the other steps.
_Avoid_: average LRV, mixed LRV

**Combined failure**:
Failure events in two or more treatment steps on the same day. Each failing step gets its own daily LRV and the daily LRVs are summed. This equals placing each failure event at a random time of day, independently of the other steps, so no overlap rules are needed.

**Next phase**:
Capabilities identified for future development and not present in the application today.
_Avoid_: roadmap, backlog, planned

**Reproducible assessment snapshot**:
A saved assessment that records the model version, data release, configuration and simulation settings needed to reproduce its result exactly. Not stored today.

**Historical assessment**:
A saved assessment created under an earlier model or data version. Its treatment is an open question.

**Assessment comparison**:
Viewing the results of several saved assessments side by side. Today this is one plot of infection-risk results per reference pathogen; comparing inputs or DALYs is next phase.
_Avoid_: benchmark, diff
