# QMRA Product Vision

## Purpose

QMRA is a web application for estimating microbial health risks in drinking-water and water-reuse scenarios.

The application guides users through a quantitative microbial risk assessment without requiring them to build the calculation model from scratch. It combines:

- pathogen concentrations in a selected or user-defined source water;
- human exposure assumptions; and
- treatment steps with minimum and maximum log-removal values (LRVs) for bacteria, viruses, and protozoa.

The application runs a predefined probabilistic calculation and reports annual probability of infection and disability-adjusted life years (DALYs). It also compares calculated results with two health-based reference levels used by the application:

- `1 × 10^-4` infections per person per year; and
- `1 × 10^-6` DALYs per person per year.

QMRA is intended for risk assessment, steady-state scenario exploration, planning, education, and communication. It is not a treatment-process design tool and its results are not, by themselves, proof of regulatory compliance or a sufficient basis for public-health decisions.

## The problem QMRA addresses

Quantitative microbial risk assessment is scientifically established, but applying it in practice requires users to assemble microbiological data, exposure assumptions, treatment-removal assumptions, dose-response parameters, health parameters, and uncertainty assumptions.

QMRA brings these elements together in a guided web workflow. It provides bundled scientific defaults for early-stage assessment and allows users to replace relevant values with project-specific inputs. This reduces the setup effort while keeping the main inputs, assumptions, results, and reference levels visible for review and discussion.

The application is most useful when users need to:

- perform a quick initial assessment using available defaults;
- explore how source-water, exposure, or treatment assumptions affect risk;
- assess a project using locally available values for concentrations, exposure, or treatment removal;
- communicate risk results using standard health metrics and reference levels; or
- save and export a reviewable record of an assessment.

## Value proposition

QMRA turns selected or user-entered pathogen, exposure, and treatment-removal data into probabilistic estimates of microbial health risk.

It provides:

- a guided entry point for users who are not building a QMRA model themselves;
- reusable default data for screening and scenario exploration;
- control over the principal exposure, source-water, and treatment inputs;
- distributions and summary statistics rather than one deterministic result;
- outputs in annual infection probability and DALYs per person per year;
- comparison with the application’s health-based reference levels; and
- saved assessments and exports for registered users.

The value of the result depends on the quality and local relevance of the inputs. The current model has a limited pathogen set, simplified treatment representation, and incomplete provenance metadata. It should therefore be used as a decision-support and communication tool, not as a complete representation of every operational or scientific uncertainty.

## Users

QMRA is intended for a broad set of users involved in water-risk assessment and communication:

- **Water-process and environmental engineers** can explore source-treatment-exposure combinations and test alternative treatment assumptions.
- **Utility operators and water-safety professionals** can assess steady-state operating scenarios using local or project-specific values.
- **Public-health specialists and regulatory stakeholders** can review assumptions, inputs, outputs, and health-based reference comparisons.
- **QMRA researchers and domain experts** can inspect the configured inputs, distributions, references, and exported results.
- **Students and non-expert users** can use the guided workflow, bundled defaults, validation, and explanatory content to learn about or explore QMRA.

These audiences do not have separate application roles or tailored calculation models. Registered users share the same access pattern and assessment functionality.

## Main workflows and functionalities

### Quick screening assessment

A user can run an assessment without an account using bundled exposure, source-water, and treatment definitions. The user selects or accepts the available defaults, submits the assessment, and reviews the calculated risk results.

### Site-specific assessment

A user can enter or modify:

- exposure events per year;
- ingested water volume per event in litres;
- minimum and maximum concentrations for each reference pathogen; and
- minimum and maximum treatment LRVs for bacteria, viruses, and protozoa.

The user can then run the calculation and review the results. The application does not verify whether user-entered values are representative of a particular site.

### Treatment-train scenario analysis

A user can add multiple treatment steps to a scenario. Each step contributes minimum and maximum LRVs for bacteria, viruses, and protozoa. The current calculation combines treatment steps by summing LRVs within each pathogen group.

Users can explore alternative scenarios by changing the configuration and rerunning the assessment. There is no dedicated comparison view for multiple saved assessments.

### Risk interpretation

The result view provides:

- annual probability of infection;
- DALYs per person per year;
- distributions for the minimum-LRV and maximum-LRV cases;
- minimum, maximum, first quartile, median, and third quartile summary statistics;
- grouped box plots;
- comparison with the application’s two health-based reference levels; and
- a risk category based on whether the calculated mean exceeds the displayed reference level under the relevant LRV case.

The interface warns when a maximum LRV is above six. This warning does not prevent the calculation from running.

### Saving, managing, and exporting assessments

A guest user can run an assessment without saving it. A registered user can:

- save an assessment with a name and description;
- list saved assessments;
- reopen and edit an assessment;
- delete an assessment;
- create reusable personal exposure, source-water, and treatment definitions; and
- export a saved assessment.

The export is a ZIP package containing input CSV files, result CSV data, an HTML report, and PNG plots.

### Next phase

The following capabilities are not part of the current implementation and should be treated as next-phase work rather than existing functionality:

- **Treatment failure and downtime assessment:** configure failure frequency and average failure duration for treatment steps and quantify their effect on annual risk.
- **Combined treatment failures:** represent simultaneous failures across treatment steps, including daily failure/no-failure states and corresponding treatment performance.
- **Saved-assessment comparison:** compare multiple saved assessments, including differences in source water, exposure assumptions, treatment trains, LRV cases, and risk results.
- **Reproducible assessment snapshots:** attach explicit model-version, data-library, reference, and simulation-settings metadata to saved and exported assessments.
- **Historical assessment handling:** define whether assessments remain tied to their original model and data, are migrated, or can be rerun under a selected version.
- **Extended interfaces:** assess the need for a stable calculation-engine boundary, public API, batch execution, notebook use, command-line use, or integration with other digital-water platforms.

## Current calculation model

The current engine calculates two treatment-performance cases:

- the **maximum-LRV case**, representing the lower infection-risk estimate; and
- the **minimum-LRV case**, representing the higher infection-risk estimate.

For each treatment step, LRVs are summed by pathogen group across the treatment train. Treatment performance is constant within each case. The engine does not simulate changing operating conditions, treatment outages, daily failure states, simultaneous failures, or process-order effects beyond the LRV sum.

The calculation uses stochastic sampling of source concentrations and exposure outcomes. It uses a fixed NumPy random-generator seed of `42` and default simulation sizes of 10,000 event samples and 1,000 simulated years.

The current user-facing model supports three reference pathogens:

- Rotavirus;
- Campylobacter jejuni; and
- Cryptosporidium parvum.

Pathogen-specific dose-response and health parameters are supplied by the bundled default data.

## Data and configuration

The application provides bundled default data for:

- reference pathogens;
- dose-response and health parameters;
- source-water definitions;
- treatment definitions;
- exposure definitions; and
- scientific or guideline references.

The inspected tests expect eight source-water definitions, 22 treatment definitions, and eight exposure definitions.

Registered users can create personal exposure, source-water, and treatment definitions. Users can also override assessment values in the configurator. Personal values are not accompanied by the same reference metadata as bundled defaults.

The assessment and export contain selected inputs and calculated results. They do not currently include an explicit model-version identifier, data-library release identifier, or complete simulation-settings snapshot.

## Product principles

QMRA should be:

- **Scientifically defensible:** calculation logic, parameters, thresholds, defaults, and references should be reviewable and testable.
- **Accessible:** the first valid assessment should be possible with a small number of clear steps and meaningful defaults.
- **Transparent:** users should be able to distinguish bundled defaults from user-entered values and understand the main assumptions behind a result.
- **Reproducible:** saved and exported assessments should eventually identify the exact model, data, configuration, and simulation settings used to produce the result.
- **Interoperable:** exports should support both human review and further analysis in external tools.
- **Safe to evolve:** changes to the scientific model, data, and user-facing interpretation should be versioned so historical results are not silently reinterpreted.
- **Responsible in its claims:** the application should clearly distinguish risk assessment from treatment design, legal compliance, and operational reliability analysis.

## Quality goals

The current repository provides calculation and regression tests, form validation, bundled scientific data, result plots, and export generation. These provide a foundation for quality, but they do not establish all desired quality properties.

Important quality goals are:

- scientific correctness supported by version-controlled benchmark and regression scenarios;
- valid and clearly labelled inputs with explicit units and min/max checks;
- visible references and understandable assumptions;
- reproducible results when the same complete assessment snapshot is used;
- stable and reviewable export content;
- appropriate privacy and access control for registered-user data; and
- acceptable response time and reliability under expected use.

The inspected test coverage is uneven. Calculation and form tests exist, but the plot test is empty and the API test file contains no substantive test implementation.

## Constraints and assumptions

- The current user-facing model supports only Rotavirus, Campylobacter jejuni, and Cryptosporidium parvum.
- Risk estimates depend strongly on the quality and local relevance of pathogen concentrations, exposure assumptions, and treatment LRVs.
- Bundled defaults support screening and exploration but may not represent local conditions.
- Treatment LRVs are treated as constant within each LRV case.
- Treatment steps are combined by adding their LRVs by pathogen group.
- Process order, changing influent concentrations, operating conditions, treatment interactions beyond the LRV sum, and treatment failures are not modelled.
- Minimum and maximum input values and stochastic sampling represent only part of the uncertainty in a real water system.
- The application assesses microbial risk; it does not assess chemical or physical hazards.
- The application is not a treatment-process design tool.
- Application reference levels and international guidance do not automatically establish compliance with local law.
- Results should not be used as the sole basis for treatment design, regulatory compliance, or public-health decisions.
- Guest users can run unsaved assessments; registered users can persist and export assessments.

## Known limitations and uncertainties

- The model is limited to three reference pathogens.
- The calculation uses simplified treatment assumptions and does not represent operational failures, downtime, or combined failures.
- Uncertainty is represented through input ranges, stochastic sampling, and minimum-/maximum-LRV cases, not through a complete joint uncertainty model.
- There is no dedicated comparison workflow for saved assessments.
- Export includes CSV, HTML, and PNG files in a ZIP; no Excel spreadsheet export was found in the inspected code.
- Saved assessments lack explicit model-version, data-library release, and complete simulation-settings metadata.
- Bundled references are available, but provenance is not captured completely for every saved or user-defined value.
- Repository inspection cannot verify production availability, response-time performance, TLS deployment, backups, retention and deletion behaviour, incident response, or the security posture of a deployed instance.

## Access and free use

The application supports guest use for unsaved assessments and registered-user accounts for persistence and export. The documentation describes the tool as free to use, and no billing workflow was found in the inspected repository. The operating policy and availability of any deployed service require separate verification.

## Evidence and scope of verification

This document describes the inspected repository state, including application code, templates, tests, documentation, and bundled default data. It does not make claims about deployment configuration or operational service behaviour unless those claims are separately verified.

Relevant evidence:

- [Repository README](https://github.com/KWB-R/qmra-webapp/blob/main/README.md)
- [Current QMRA documentation](https://github.com/KWB-R/qmra-webapp/blob/main/docs/source/index.rst)
- [Risk calculation](https://github.com/KWB-R/qmra-webapp/blob/main/qmra/risk_assessment/risk.py)
- [Assessment views and access paths](https://github.com/KWB-R/qmra-webapp/blob/main/qmra/risk_assessment/views.py)
- [Assessment forms and validation](https://github.com/KWB-R/qmra-webapp/blob/main/qmra/risk_assessment/forms.py)
- [Assessment and result models](https://github.com/KWB-R/qmra-webapp/blob/main/qmra/risk_assessment/models.py)
- [Default data models](https://github.com/KWB-R/qmra-webapp/blob/main/qmra/risk_assessment/qmra_models.py)
- [Export implementation](https://github.com/KWB-R/qmra-webapp/blob/main/qmra/risk_assessment/exports.py)
- [Result plots](https://github.com/KWB-R/qmra-webapp/blob/main/qmra/risk_assessment/plots.py)
- [FAQ and limitations](https://github.com/KWB-R/qmra-webapp/blob/main/qmra/risk_assessment/templates/faqs.html)
- [Calculation and regression tests](https://github.com/KWB-R/qmra-webapp/tree/main/qmra/risk_assessment/tests)

## Open questions

The following questions remain open for future product and scientific development:

- Should model and data-library versions receive explicit release identifiers and change logs, and should these identifiers be attached to every saved and exported assessment?
- What information must be stored so that a saved assessment can be reproduced from the same model, data, configuration, and simulation settings?
- Should the scientific calculation engine be separated behind a stable internal API or library boundary?
- Is there a future need for public API access, batch execution, notebook use, command-line use, or integration with other digital-water platforms?
- What project data may be confidential or commercially sensitive even when it is not personal data, and what additional controls are required for saved assessments?
- How should historical assessments behave when the scientific model, data library, or assessment schema changes: remain frozen to the original version, be migrated, or be rerunnable under a user-selected version?
- What comparison capabilities are needed for saved assessments and alternative scenarios?
- Which deployment controls, operational metrics, performance targets, backup policies, retention rules, and incident-response processes are required for production use?
