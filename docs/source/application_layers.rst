Application Layers
==================

This project can be understood in two documentation levels:

* **UI layer**: templates, static assets, and page-level interactions that users see.
* **Backend layer**: Django views, forms, models, routing, and risk computation logic.

UI Layer
--------

The UI is server-rendered with Django templates and enhanced with JavaScript snippets embedded in template partials.

Key entry points
~~~~~~~~~~~~~~~~

* `qmra/templates/layout.html` provides the shared shell (page frame) for most pages.
* `qmra/templates/index.html` is the public landing page.
* `qmra/risk_assessment/templates/assessment-configurator.html` is the main guided workflow for creating a risk assessment.
* `qmra/risk_assessment/templates/assessment-result.html` presents simulation outputs and charts.
* `qmra/user/templates/*.html` handles authentication and account-facing screens.

UI building blocks
~~~~~~~~~~~~~~~~~~

* **Global styling** is defined in `qmra/static/css/styles.css`.
* **Images/icons** are served from `qmra/static/img/`.
* **Dynamic form behavior** is placed in template fragments such as:

  * `qmra/risk_assessment/templates/inflows-form-js.html`
  * `qmra/risk_assessment/templates/treatments-form-js.html`
  * `qmra/risk_assessment/templates/risk-assessment-form-js.html`

Typical UI flow
~~~~~~~~~~~~~~~

1. User opens the configurator page.
2. User selects/creates inflows, treatments, and exposure settings.
3. User submits the form.
4. Backend computes Monte Carlo outcomes.
5. Results page renders plots and export options.

Backend Layer
-------------

The backend is a Django application split into project-level wiring and feature apps (`risk_assessment` and `user`).

Project-level backend
~~~~~~~~~~~~~~~~~~~~~

* `qmra/settings.py` contains Django configuration.
* `qmra/urls.py` maps root URL patterns to app routes.
* `qmra/views.py` contains project-level views (e.g., landing page).
* `manage.py` is the command entrypoint for local operations.

Risk assessment domain backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* `qmra/risk_assessment/models.py` stores persisted domain entities.
* `qmra/risk_assessment/qmra_models.py` defines QMRA reference data structures used by the simulation logic.
* `qmra/risk_assessment/forms.py` validates and structures UI submissions.
* `qmra/risk_assessment/views.py` implements the request/response workflow for configurator, results, and CRUD operations.
* `qmra/risk_assessment/risk.py` executes core risk calculations and simulation logic.
* `qmra/risk_assessment/plots.py` prepares data visualizations returned to templates.
* `qmra/risk_assessment/exports.py` handles export generation for assessment results.
* `qmra/risk_assessment/urls.py` exposes risk-assessment routes.

User/account backend
~~~~~~~~~~~~~~~~~~~~

* `qmra/user/models.py` contains user-facing data models.
* `qmra/user/views.py` handles registration, login-related pages, and account actions.
* `qmra/user/urls.py` defines account URL patterns.

Data bootstrap and operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* `qmra/management/commands/seed_default_db.py` loads default entities.
* `qmra/management/commands/collect_static_default_entities.py` snapshots configured defaults into static JSON.
* `qmra/management/commands/export_default.py` exports default data sets.
* `qmra/static/data/*.json` stores default inflow, pathogen, treatment, source, reference, and exposure datasets consumed by backend workflows.

Request lifecycle (high-level)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. URL dispatch in `qmra/urls.py` or app `urls.py` selects a view.
2. View instantiates forms, loads defaults/database entities, and validates input.
3. Risk logic in `risk.py` and helper modules computes outputs.
4. View sends context to templates for HTML rendering (and optional exports).
