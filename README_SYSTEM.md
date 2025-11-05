# QMRA System Overview

This document provides a high-level overview of the Quantitative Microbial Risk Assessment (QMRA) web application, highlighting its principal components and the data sources that power the risk calculations.

## Architecture Summary

The project is a Django-based web application composed of a core project configuration and several domain-specific apps:

- **Project configuration (`qmra/`)** – Defines global settings, URL routing, and shared views for landing, health, and readiness endpoints.【F:qmra/urls.py†L1-L17】【F:qmra/views.py†L1-L31】
- **Risk assessment app (`qmra/risk_assessment/`)** – Implements the workflows for creating assessments, listing inputs, rendering results, and exporting data. It exposes URL routes for assessments, exposures, sources, inflows, treatments, and Prometheus metrics.【F:qmra/risk_assessment/urls.py†L1-L48】 The app contains forms, views, and models that calculate infection risk using predefined pathogen and treatment parameters.【F:qmra/risk_assessment/models.py†L1-L116】
- **User management app (`qmra/user/`)** – Extends Django's authentication to handle user registration and profile management, supporting secure access to saved assessments.【F:qmra/user/urls.py†L1-L10】
- **Templates and static assets (`qmra/templates/`, `qmra/static/`)** – Provide the user interface for the risk assessment workflows and serve precomputed reference data consumed by the forms and calculators.

The application exposes both web views for interactive risk calculations and operational endpoints (`/ready`, `/health`) that verify database connectivity for deployment environments.【F:qmra/views.py†L18-L31】

## Core Components

| Component | Purpose |
| --- | --- |
| **RiskAssessment models and calculators** (`qmra/risk_assessment/models.py`, `risk.py`) | Represent inflows, exposures, treatments, and pathogen models, and execute dose-response calculations using exponential or beta-Poisson distributions.【F:qmra/risk_assessment/models.py†L17-L96】 |
| **Forms & Views** (`qmra/risk_assessment/forms.py`, `views.py`) | Collect user inputs for water sources, treatment trains, and exposure scenarios, then render dynamic result pages and exports. |
| **Exports** (`qmra/risk_assessment/exports.py`) | Generate CSV/Excel outputs so users can archive model inputs and computed risk metrics. |
| **User accounts** (`qmra/user/`) | Manage authentication, sessions, and user-specific data storage. |
| **Prometheus integration** (`django_prometheus`) | Exposes application metrics for monitoring, included through the risk assessment URL configuration.【F:qmra/risk_assessment/urls.py†L41-L48】 |

## Data Sources

The QMRA models rely on curated microbiological and treatment performance data supplied with the repository:

- **Raw public datasets (`raw_public_data/`)** – CSV files sourced from published literature and guidelines providing pathogen characteristics, dose-response parameters, water sources, inflow concentrations, treatment log removals, and exposure assumptions.【F:raw_public_data/tbl_pathogen.csv†L1-L2】【F:raw_public_data/tbl_treatment.csv†L1-L2】 These serve as the authoritative reference tables.
- **Static JSON datasets (`qmra/static/data/`)** – The application loads default pathogens, inflows, treatments, exposures, sources, and citations from JSON files embedded in the static directory.【F:qmra/static/data/default-pathogens.json†L1-L20】 They are derived from the raw CSV inputs via the `collect_static_default_entities` management command, which merges, filters, and normalizes the raw tables into the JSON structures consumed by the UI forms.【F:qmra/management/commands/collect_static_default_entities.py†L1-L69】【F:qmra/management/commands/collect_static_default_entities.py†L94-L121】

### Runtime data loading

- **Default reference values** – When users open the configurator, the front-end JavaScript fetches the static JSON bundles (for example `default-treatments.json`, `default-exposures.json`, `default-sources.json`) through Django's static file handler to populate the dropdowns and helper panels.【F:qmra/risk_assessment/templates/treatments-form-js.html†L2-L452】【F:qmra/risk_assessment/templates/risk-assessment-form-js.html†L44-L97】【F:qmra/risk_assessment/templates/inflows-form-js.html†L2-L203】 No database lookups are required for these defaults at runtime—the values are read directly from the generated static assets.
- **User-defined entries and saved assessments** – Any data a signed-in user creates (custom sources, exposures, treatments, and complete risk assessments) is persisted in the PostgreSQL database via the Django ORM and is exposed back to the UI through JSON endpoints such as `/sources`, `/inflows`, and `/exposures` that combine database rows with the static defaults.【F:qmra/risk_assessment/views.py†L43-L140】【F:qmra/risk_assessment/templates/inflows-form-js.html†L166-L198】【F:qmra/risk_assessment/templates/risk-assessment-form-js.html†L80-L93】

In short, the shipped literature-based reference data is served from static JSON generated from the CSVs, while user-generated content and saved configurations flow through the database connection.

To refresh the static defaults when raw data changes, run:

```bash
python manage.py collect_static_default_entities
```

This command regenerates the JSON assets in `qmra/static/data/` from the CSV files in `raw_public_data/`, ensuring that the application's default selections align with the latest scientific references.【F:qmra/management/commands/collect_static_default_entities.py†L101-L121】

## Deployment Considerations

- **Database connectivity** – Health and readiness views explicitly check database connections, making it straightforward to wire the app into container-based health checks.【F:qmra/views.py†L18-L31】
- **Static asset generation** – Collect static files (`python manage.py collectstatic`) before deployment to serve the UI assets referenced by the templates.
- **Monitoring** – Include the Prometheus endpoint provided by `django_prometheus` in your monitoring stack for observability of request and database metrics.【F:qmra/risk_assessment/urls.py†L41-L48】

## Further Reading

For setup instructions, refer to the root [`README.md`](README.md). For in-depth developer documentation, see the Sphinx docs under `docs/`.
