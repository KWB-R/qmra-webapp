# QMRA Glossary

This glossary defines the essential vocabulary for the current QMRA web application. It is intentionally concise and should be used as the shared language for the vision, documentation, and future work.

## Core concepts

**QMRA — Quantitative microbial risk assessment**
A structured assessment of health risk from exposure to microbial pathogens. In this application, it combines source-water, exposure, and treatment inputs.

**Assessment**
One configured QMRA calculation, including its inputs and results. A saved assessment also has a name, description, and stored record.

**Scenario**
One combination of source-water, exposure, and treatment assumptions.

**Source water**
Water before the configured treatment train, represented by minimum and maximum pathogen concentrations.

**Exposure**
The assumed human contact with or ingestion of water. The current inputs are events per year and ingested volume per event in litres.

**Treatment step**
One treatment technology or process step with configured pathogen-removal values.

**Treatment train**
The collection of treatment steps used in a scenario. The current calculation combines steps by adding their LRVs by pathogen group.

**Log-removal value (LRV)**
A logarithmic measure of pathogen reduction. The application uses minimum and maximum LRVs for bacteria, viruses, and protozoa.

**Reference pathogen**
A pathogen included in the current model. The three reference pathogens are Rotavirus, Campylobacter jejuni, and Cryptosporidium parvum.

## Calculation and results

**Probabilistic risk model**
A model that produces a distribution of possible outcomes instead of one deterministic value.

**Monte Carlo simulation**
Repeated stochastic sampling used to estimate risk distributions. The current implementation uses seed `42`, with default settings of 10,000 event samples and 1,000 simulated years.

**Dose-response model**
The relationship between ingested pathogen dose and the probability of infection.

**Maximum-LRV case**
The case using maximum configured LRVs. It represents the lower infection-risk estimate.

**Minimum-LRV case**
The case using minimum configured LRVs. It represents the higher infection-risk estimate.

**Annual probability of infection**
The estimated probability of infection over one year.

**DALYs per person per year**
The estimated health burden, expressed as disability-adjusted life years per person per year.

**Health-based reference level**
A comparison value shown by the application: `1 × 10^-4` infections per person per year and `1 × 10^-6` DALYs per person per year. These values are not automatically legal limits.

**Risk distribution**
The set of sampled risk outcomes for a pathogen and LRV case.

**Uncertainty**
Variation or lack of knowledge represented in an assessment. The current application represents only part of it through input ranges, stochastic sampling, and the two LRV cases.

## Data and users

**Bundled default data**
Data shipped with the application for pathogens, parameters, source waters, treatments, exposures, and references.

**Site-specific input**
A value entered to represent local or project evidence. The application does not verify that it is representative of the site.

**Personal definition**
A reusable exposure, source-water, or treatment definition created by a registered user.

**Provenance**
Information showing where data, parameters, and interpretations came from. The current application provides some references but does not store complete provenance for every assessment.

**Guest assessment**
An unsaved assessment run without an account.

**Registered user**
An authenticated user who can save assessments and create personal definitions. There are no separate professional roles in the application.

**Saved assessment**
An assessment stored for a registered user so it can be listed, reopened, edited, deleted, or exported.

**Assessment configurator**
The form-based interface for entering or selecting assessment inputs.

**Export package**
A ZIP containing input CSV files, result CSV data, an HTML report, and PNG plots.

## Boundaries and next phase

**Steady-state scenario**
A scenario in which source-water, exposure, and treatment assumptions are treated as stable. This is the current scope; changing operating conditions and failures are not modelled.

**Treatment-process design**
Engineering design of a treatment process. This is outside the scope of the application.

**Regulatory compliance**
Conformance with applicable local law. The application’s reference levels do not automatically establish compliance.

**Next phase**
Capabilities identified for future development, not current functionality.

**Treatment failure / downtime**
A treatment step operating below its intended performance or being unavailable. Failure frequency, failure duration, and downtime are not currently modelled.

**Combined failure**
Simultaneous failures of multiple treatment steps. Not currently modelled.

**Assessment comparison**
A future workflow for comparing multiple saved assessments. Not currently implemented.

**Reproducible assessment snapshot**
A saved assessment containing the exact model version, data release, configuration, and simulation settings needed to reproduce its result. The current application does not store this complete snapshot.

**Historical assessment**
A saved assessment created under an earlier model or data version. How such assessments should be preserved, migrated, or rerun remains open.

**Scientific calculation engine**
The logic that converts assessment inputs into risk results. A stable internal API or library boundary is a future design question.

## Preferred language

- Use **assessment** for a configured calculation and its saved record.
- Use **scenario** for one combination of assumptions.
- Use **maximum-LRV case** and **minimum-LRV case**, rather than “best case” and “worst case.”
- Use **health-based reference level**, rather than “legal limit.”
- Use **personal definition** for reusable user-created data.
- Use **next phase** for capabilities that are not implemented yet.
