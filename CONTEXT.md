# QMRA Web Application

A web tool for quantitative microbial risk assessment of water: a user describes a source water, a treatment train and an exposure, and the tool estimates the yearly infection risk and health burden for three reference pathogens. Bounded to steady-state scenarios; treatment failure, downtime and process design are out of scope.

## Language

### Assessment

**Assessment**:
One configured QMRA calculation together with its inputs and results. It holds exactly one scenario.
_Avoid_: risk assessment (in prose), calculation, run, project

**Scenario**:
One combination of source-water, exposure and treatment-train assumptions. Today an assessment contains exactly one scenario; the term exists so that multi-scenario comparison can be discussed later.
_Avoid_: case (reserved for LRV cases), configuration

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
A named type of water before treatment, such as raw sewage or protected surface water. A source water is described by one inflow per reference pathogen.
_Avoid_: source, water type, feed water

**Inflow**:
The minimum and maximum concentration of one reference pathogen in a source water, in organisms per litre. An assessment has one inflow per selected pathogen.
_Avoid_: concentration range, pathogen input, source concentration

**Exposure**:
The assumed human contact with the treated water, given as events per year and ingested volume per event in litres.
_Avoid_: exposure scenario, ingestion, use

**Treatment step**:
One treatment technology or process with a minimum and maximum log-removal value per pathogen group.
_Avoid_: treatment (alone, when a step is meant), barrier, process, technology

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
Source waters, inflows, treatment steps, exposures, pathogens and references shipped with the application.
_Avoid_: defaults, static data, system data, library

**Personal definition**:
A reusable source water, exposure or treatment step created by a registered user and offered alongside the bundled defaults.
_Avoid_: custom entry, user data, own data

**Site-specific input**:
A value typed in for one assessment to represent local evidence. The application does not check that it is representative.
_Avoid_: custom value, manual value, override

**Reference**:
A literature citation attached to a bundled inflow, exposure or LRV to show where the value came from.
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

**Maximum-LRV case**:
The calculation using every step's maximum LRV. It gives the lower infection-risk estimate.
_Avoid_: best case, minimum risk scenario, optimistic case

**Minimum-LRV case**:
The calculation using every step's minimum LRV. It gives the higher infection-risk estimate.
_Avoid_: worst case, maximum risk scenario, conservative case

**Annual probability of infection**:
The estimated probability that a person is infected at least once in one year of exposure.
_Avoid_: infection risk (alone), yearly risk

**DALYs per person per year**:
The estimated health burden in disability-adjusted life years per person per year, derived from the annual probability of infection through the pathogen's illness-to-infection ratio and burden per case.
_Avoid_: DALY, burden, health impact

**Risk distribution**:
The set of sampled yearly outcomes for one reference pathogen and one LRV case, summarised by minimum, quartiles, median and maximum.
_Avoid_: result set, spread

**Health-based reference level**:
A comparison value shown next to results: one infection per ten thousand persons per year and one millionth DALY per person per year. It is not a legal limit.
_Avoid_: legal limit, tolerable risk level, guideline value, threshold

**Reference-level exceedance**:
The verdict for one reference pathogen: whether the mean risk exceeds the health-based reference level in both LRV cases, only in the minimum-LRV case, or in neither.
_Avoid_: risk category, risk flag, pass/fail

**Uncertainty**:
Variation or lack of knowledge in an assessment. Represented today only through inflow ranges, random sampling and the two LRV cases.

### Boundaries

**Steady-state scenario**:
A scenario whose source water, exposure and treatment performance are assumed constant over the year. This is the only kind the application models.

**Treatment failure**:
A treatment step performing below its configured LRVs or being unavailable for a period. Not modelled; a next-phase concept.
_Avoid_: outage, malfunction, downtime (alone)

**Combined failure**:
Two or more treatment steps failing at the same time. Not modelled.

**Next phase**:
Capabilities identified for future development and not present in the application today.
_Avoid_: roadmap, backlog, planned

**Reproducible assessment snapshot**:
A saved assessment that records the model version, data release, configuration and simulation settings needed to reproduce its result exactly. Not stored today.

**Historical assessment**:
A saved assessment created under an earlier model or data version. Its treatment is an open question.

**Assessment comparison**:
A workflow for viewing several saved assessments side by side. Next phase.
