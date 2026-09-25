# QMRA Vision

## Purpose

Quantitative microbial risk assessment is well established, but applying it to a real water system means assembling pathogen data, exposure assumptions, treatment removal, dose-response and health parameters, which most water professionals cannot do from scratch. QMRA is a web application that does this for them: a user describes a source water, a treatment train and an exposure, and gets the annual probability of infection and DALYs per person per year for three reference pathogens, compared with health-based reference levels. It supports risk assessment, scenario exploration, planning, teaching and communication in drinking water and water reuse.

## Users

- **Water-process and environmental engineers** need to compare treatment trains and see how treatment assumptions change the risk.
- **Utility operators and water-safety professionals** need to assess their own plant with local values instead of literature defaults.
- **Public-health specialists and regulators** need to review the inputs, assumptions and the comparison with reference levels without running the model themselves.
- **QMRA researchers and domain experts** need to inspect inputs, distributions and references, and check results against their own calculations.
- **Students and newcomers to QMRA** need a guided path with defaults and explanations to learn how a risk assessment works.

All of them use the same functions. The only difference in access is between guests, who cannot save, and registered users.

## Main workflows

### Quick screening

1. A guest or registered user opens the assessment configurator.
2. They select a bundled source water, bundled treatment steps and a bundled exposure.
3. The application runs the Monte Carlo simulation and shows, per reference pathogen, the risk distributions of both risk measures in best-case and worst-case, with the reference-level exceedance. For a guest nothing is stored.

### Site-specific assessment

1. A guest or registered user starts from bundled data or their personal definitions.
2. They replace values with local ones: inflow concentrations (which makes the source water a site-specific source water), LRVs of treatment steps, and exposure events per year and volume per event. Recontamination is entered as a treatment step with a negative LRV.
3. The results are the same as in quick screening. The application does not check whether the entered values represent the site.

### Save, reopen and export

1. A registered user saves an assessment with a name and description.
2. They can list, reopen, edit and delete saved assessments.
3. For a saved assessment they download an export package: a ZIP with input tables, a result table, an HTML report and plots.

### Personal definitions

1. A registered user creates a reusable source water, exposure or treatment step.
2. The configurator offers it next to the bundled default data in every later assessment.

### Compare scenarios

1. A registered user selects several saved assessments on the saved-assessments page.
2. The assessment comparison shows one plot: the annual probability of infection per reference pathogen for each selected assessment, against the health-based reference level. DALYs and inputs are not compared.

## Scope

- Microbial risk in drinking water and water reuse, for three reference pathogens: Rotavirus, Campylobacter jejuni and Cryptosporidium parvum.
- Steady-state scenarios: inflow concentrations given as minimum and maximum, a treatment train whose LRVs are summed per pathogen group, and an exposure given as events per year and volume per event.
- A Monte Carlo simulation in two cases, best-case (maximum LRVs) and worst-case (minimum LRVs), reporting risk distributions with minimum, quartiles, median and maximum.
- Two risk measures, each compared with its health-based reference level: 1 × 10⁻⁴ infections per person per year and 1 × 10⁻⁶ DALYs per person per year.
- Bundled default data with references, personal definitions and site-specific inputs.
- Guest use without saving; saving, comparison and export for registered users. The tool is free to use.
- A warning when a treatment step's maximum LRV is above 6. The calculation still runs.

Known limitations of the current product:

- Uncertainty is represented only through inflow concentration ranges, random sampling and the spread between best-case and worst-case, not through a complete uncertainty model.
- Provenance is incomplete: bundled data carries references, but personal definitions and site-specific inputs do not.
- Saved assessments and export packages do not record the model version, data release or simulation settings, so a result cannot be reproduced exactly later.
- The assessment comparison covers annual probability of infection only.

## Out of scope

- Treatment process design and sizing, the order of treatment steps, and interactions between steps beyond the sum of their LRVs.
- Chemical and physical hazards.
- Conditions that change within a year, such as varying inflow concentrations or operating conditions. Results are yearly, never daily.
- Partial loss of removal in a treatment step. Treatment failure, once modelled, means the entire loss of a step's LRV.
- Proof of legal compliance. The health-based reference levels are comparison values, not legal limits, and results must not be the only basis for treatment design, regulatory or public-health decisions.

## MVP

The current application is the base. The next useful version adds **treatment failure**, including combined failures, following `docs/QMRA_Failure_Approach.md` and ADR-0001. It serves utility operators and engineers who want to know how failures of their treatment steps affect the yearly risk.

Functionalities, each one Change:

1. **Failure inputs per treatment step.** In the assessment configurator, each treatment step with at least one positive LRV gets a failure frequency (failure days per year, 0–365, default 0) and a failure duration (minutes, 1–1440, default 30). The inputs belong to the scenario.
2. **Failure inputs on personal treatment steps.** A personal treatment step can store its failure frequency and failure duration for reuse.
3. **Calculation with failure days.** Inside the Monte Carlo simulation, each exposure event falls on a failure day of each step with probability failure frequency / 365. Worst-case loses the full LRV of every failing step; best-case applies the mixed-water assumption: combined failures that fit into a day do not overlap, two steps longer than a day overlap only by the extra minutes, and three or more steps longer than a day in total count like worst-case.
4. **Results and export including failures.** The result page, the reference-level exceedance and the export package show the result including failures, and the export records the failure inputs of each step.

Waits until later:

- Extended assessment comparison with DALYs and inputs. Until then, the DALY effect of different failure inputs is read from each assessment's own result page.
- Reproducible assessment snapshots.
- Handling of historical assessments after model or data changes.
- Extended interfaces: a calculation-engine boundary, public API, batch, notebook or command-line use.
- The naming follow-ups recorded in `docs/domain-model-open-questions.md`.

## Success criteria

- A water utility can assess the effect of its own failure frequencies on the yearly risk, for both risk measures, without help from the development team.
- Results for the bundled benchmark scenarios match the reference calculation within an agreed tolerance.
- Domain experts at KWB accept the results as defensible for use in projects.

## Quality goals

### Scientific correctness

- **Goal**: calculated results match an independent reference calculation.
- **Example situation**: a domain expert recalculates the worst-case Cryptosporidium risk of a bundled scenario in a spreadsheet and gets a different median.
- **How we check it**: version-controlled benchmark scenarios with expected results from an independent calculation; regression tests run on every change and fail outside the agreed tolerance.

### Traceability

- **Goal**: for every input of an assessment, a reader can see whether it is bundled default data, a personal definition or a site-specific input, and for bundled data which reference it comes from.
- **Example situation**: a reviewer at a health authority asks where the Rotavirus concentration of a "site-specific groundwater" came from.
- **How we check it**: the export package lists the origin of each input and the reference of each bundled value; a test checks that every exported input has an origin and every bundled value a reference.

### Reproducibility

- **Goal**: a saved assessment gives the same result every time, and can be recalculated later under the same model and data.
- **Example situation**: a year after a report, a utility reopens an assessment after a model update and gets different numbers without knowing why.
- **How we check it**: each saved assessment and export package records the model version, data release and simulation settings; a test recalculates stored benchmark assessments and compares them with their recorded results.

### Input validity

- **Goal**: every input shows its unit and is checked against a plausible range; invalid values are rejected with a clear message.
- **Example situation**: a user enters 2000 as volume per event, thinking in millilitres.
- **How we check it**: form tests per input field for the unit label, the lower and upper bounds (for example failure frequency 0–365, failure duration 1–1440) and minimum ≤ maximum.

### Export stability

- **Goal**: the content and layout of the export package change only on purpose.
- **Example situation**: a utility's script that reads the result table breaks after an update renamed a column.
- **How we check it**: a test compares the export package of a benchmark assessment with a stored reference export; changing it requires updating the reference and noting it in the release notes.

### Privacy of registered-user data

- **Goal**: a registered user's saved assessments, export packages and personal definitions are accessible only to that user.
- **Example situation**: a logged-in user changes the assessment ID in the URL to one belonging to another user.
- **How we check it**: tests request every assessment, export and personal-definition URL as a different user and expect a refusal.

## Open questions

- Should model and data releases get explicit identifiers and change logs, attached to every saved assessment and export package? (Wolfgang, Malte; for Architecture)
- What must be stored so that a saved assessment can be reproduced from the same model, data, configuration and simulation settings? (Wolfgang, Malte; for Architecture)
- Should the calculation engine be separated behind a stable internal boundary? (Wolfgang, Malte; for Architecture)
- Is there a need for public API access, batch execution, notebook or command-line use, or integration with other digital-water platforms? (Wolfgang, Malte)
- Which project data is confidential or commercially sensitive even when it is not personal data, and what controls do saved assessments need? (Wolfgang, Malte)
- How should historical assessments behave when the model, data or assessment structure changes: stay frozen, be migrated, or be recalculated under a chosen version? (Wolfgang, Malte)
- Beyond DALYs, which comparisons of saved assessments are needed: inputs, best-case and worst-case side by side, saved comparisons? (Wolfgang, Malte)
- What tolerance counts as a match for the benchmark scenarios, and which domain experts accept the results? (Wolfgang, Malte)
- Where does the rule "maximum LRV above 6" come from, and should it warn or cap? See `docs/domain-model-open-questions.md`. (Wolfgang, Malte)
- Which response-time and reliability targets apply, and which deployment controls, backups, retention rules and incident-response processes are required for production use? (Wolfgang, Malte; for Architecture)
