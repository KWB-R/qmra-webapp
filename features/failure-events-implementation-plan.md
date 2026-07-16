# Failure Events Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add per-treatment failure duration and failure frequency inputs to QMRA, propagate them through the treatment UI and default data, and update annual risk calculations so `failure_frequency_days_per_year = 0` preserves current behavior.

**Current Status:** Implemented locally and verified with backend tests plus a Playwright UI test on `http://127.0.0.1:8002/`.

**Architecture:** Persist the new fields on editable treatments, user-created treatments, and the static default treatment model. Surface them in the Django formsets and JSON-driven treatment picker, then branch the annual risk calculation into a normal-day path and a failure-day path using the same annual product structure. Keep the result schema unchanged so downstream exports and plots stay stable. Treat the seeded `qmra` database as a deployment artifact that must be rebuilt from the exported static JSON, not hand-edited in production.

**Tech Stack:** Django models and migrations, crispy-forms, vanilla JS, numpy, Django TestCase.

---

### Production Runbook

Use this sequence whenever the feature is promoted beyond a local branch.

**Backup**
- Export application data before touching schema or seed data:

```bash
python manage.py dumpdata risk_assessment.Treatment risk_assessment.UserTreatment --indent 2 --output backups/treatments-YYYYMMDD-HHMMSS.json
```

- Back up the seeded static database used for default entities:

```bash
Copy-Item qmra.db qmra.db.backup-YYYYMMDD-HHMMSS
```

- Back up the generated static treatment JSON:

```bash
Copy-Item qmra/static/data/default-treatments.json qmra/static/data/default-treatments.json.backup-YYYYMMDD-HHMMSS
```

**Deploy**
- Apply the migration for the app database.
- Regenerate `qmra/static/data/default-treatments.json`.
- Re-seed the `qmra` database only from the refreshed JSON.
- Do not point the seed command at production user tables.
- Treat `UserTreatment` as application data in the main app database, not as seeded default data.

**Verify**
- Run the treatment form tests.
- Run the risk calculation regression tests.
- Run the export tests if the CSV or report output is affected.
- Manually confirm the configurator shows `failure_duration_minutes` and `failure_frequency_days_per_year` for a blank treatment row and for an existing user treatment.

**Rollback**
- Restore `qmra/static/data/default-treatments.json` from the backup if the export is wrong.
- Restore `qmra.db` from the backup if the seeded default database is corrupted.
- Restore the application database backup if the migration or data backfill breaks `Treatment` or `UserTreatment`.
- Re-run `seed_default_db` only after the JSON backup has been restored or verified.
- If rollback is limited to application data, restore `Treatment` and `UserTreatment` together so the schema and user-created records remain aligned.

---

### Task 1: Add failure-event fields to treatment models and default data

**Files:**
- Modify `qmra/risk_assessment/models.py`
- Modify `qmra/risk_assessment/user_models.py`
- Modify `qmra/risk_assessment/qmra_models.py`
- Modify `qmra/risk_assessment/admin.py`
- Create `qmra/risk_assessment/migrations/0011_treatment_failure_events.py`
- Regenerate `qmra/static/data/default-treatments.json`

- [x] **Step 1: Write the failing tests**

Add a focused test module or extend `qmra/risk_assessment/tests/test_risk_assessment_form.py` with assertions like:

```python
def test_treatment_defaults_include_failure_fields(self):
    treatment = Treatment.from_default(QMRATreatments.get("Primary treatment"), given_ra)
    assert treatment.failure_duration_minutes == 30
    assert treatment.failure_frequency_days_per_year == 0
```

Also add a model-level smoke check that the static treatment loader exposes the same keys:

```python
def test_default_treatment_json_contains_failure_keys(self):
    treatment = QMRATreatments.get("Primary treatment")
    assert treatment.failure_duration_minutes == 30
    assert treatment.failure_frequency_days_per_year == 0
```

- [x] **Step 2: Run the tests to confirm they fail**

Run:

```bash
python manage.py test qmra.risk_assessment.tests.test_risk_assessment_form qmra.risk_assessment.tests.test_assess_risk -v 2
```

Expected: failures showing the new fields are missing from the model and default-data path.

- [x] **Step 3: Add the new model fields and defaults**

Add these fields to `Treatment`, `UserTreatment`, and `QMRATreatment`:

```python
failure_duration_minutes = models.IntegerField(default=30)
failure_frequency_days_per_year = models.FloatField(default=0)
```

Update `Treatment.from_default(...)` to copy both fields from the static treatment object. Update `QMRATreatment.from_dict(...)` and `QMRATreatment.to_dict(...)` so the static JSON round-trips the new keys. Update `admin.py` so the admin list and edit form expose the new fields with the existing LRV columns.

- [x] **Step 4: Create and apply the migration**

Run:

```bash
python manage.py makemigrations risk_assessment
python manage.py migrate
```

Expected: a new migration adds the two fields to the editable treatment tables without changing existing rows.

- [x] **Step 5: Regenerate default treatment JSON**

Run:

```bash
python manage.py collect_static_default_entities
```

Then verify `qmra/static/data/default-treatments.json` now contains `failure_duration_minutes` and `failure_frequency_days_per_year` for every default treatment.

- [x] **Step 6: Re-seed the QMRA default database if the test path depends on it**

Run:

```bash
python manage.py seed_default_db
```

Expected: the static `qmra` database still loads cleanly with the updated treatment schema.

Important:
- this command updates the seeded `qmra` database that backs static default entities
- it should be run only against the seed database or a local/dev copy
- it should not be pointed at production user tables
- production user data lives in the app database and is not overwritten by this seed step
- user-created treatments live in `UserTreatment` in the app database and need their own backup/rollback plan

- [ ] **Step 7: Commit**

```bash
git add qmra/risk_assessment/models.py qmra/risk_assessment/user_models.py qmra/risk_assessment/qmra_models.py qmra/risk_assessment/admin.py qmra/risk_assessment/migrations/0011_treatment_failure_events.py qmra/static/data/default-treatments.json
git commit -m "feat: add treatment failure-event fields"
```

- [x] **Step 8: Record backup and rollback procedure**

Confirm the production runbook above covers backup, deploy, verify, and rollback for `Treatment`, `UserTreatment`, and the seeded `qmra` database.

---

### Task 2: Expose failure-event inputs in the treatment forms and table UI

**Files:**
- Modify `qmra/risk_assessment/forms.py`
- Modify `qmra/risk_assessment/user_models.py`
- Modify `qmra/risk_assessment/templates/treatments-form-fieldset.html`
- Modify `qmra/risk_assessment/templates/treatments-form-js.html`
- Extend `qmra/risk_assessment/tests/test_risk_assessment_form.py`

- [x] **Step 1: Write the failing form tests**

Add test coverage for:

```python
def test_treatment_form_accepts_failure_fields(self):
    data = dict(
        name="Primary treatment",
        bacteria_min=0, bacteria_max=1,
        viruses_min=0, viruses_max=1,
        protozoa_min=0, protozoa_max=1,
        failure_duration_minutes=30,
        failure_frequency_days_per_year=0,
    )
```

Add validation cases for the explicit bounds:

```python
def test_treatment_failure_fields_validate_ranges(self):
    data = dict(
        name="Primary treatment",
        bacteria_min=0, bacteria_max=1,
        viruses_min=0, viruses_max=1,
        protozoa_min=0, protozoa_max=1,
        failure_duration_minutes=0,
        failure_frequency_days_per_year=366,
    )
```

Expected assertions:
- duration rejects values below `1` and above `1440`
- frequency rejects values below `0` and above `365`
- blank treatment rows still start with `30` and `0`

- [x] **Step 2: Run the form tests and confirm they fail**

Run:

```bash
python manage.py test qmra.risk_assessment.tests.test_risk_assessment_form -v 2
```

Expected: missing-field and invalid-range failures.

- [x] **Step 3: Update the Django forms**

In `TreatmentForm` and `UserTreatmentForm`, add the two new fields to `Meta.fields`, set labels and min/max widget attributes in `__init__`, and extend the crispy layout with two more rows or a single row that matches the current table style. Keep the existing LRV rows intact.

Use explicit widget settings:

```python
self.fields["failure_duration_minutes"].widget.attrs["min"] = 1
self.fields["failure_duration_minutes"].widget.attrs["max"] = 1440
self.fields["failure_frequency_days_per_year"].widget.attrs["min"] = 0
self.fields["failure_frequency_days_per_year"].widget.attrs["max"] = 365
```

- [x] **Step 4: Update the treatment table template and JS**

In `treatments-form-fieldset.html`, ensure the formset renders the new inputs in each treatment row and that the hidden empty form includes them.

In `treatments-form-js.html`:
- extend `TreatmentForm.fields` with selectors for the two new inputs
- include the two fields in `setValues()` and `getValues()`
- add the fields to the summary info table rendered in `renderInfos()`
- keep `createForm()` working for dynamically added rows by cloning the empty form after the new inputs exist

The UI should show the default values immediately on blank rows, not only after a user types into the form.

- [x] **Step 5: Re-run the form tests**

Run:

```bash
python manage.py test qmra.risk_assessment.tests.test_risk_assessment_form -v 2
```

Expected: the new fields validate, the defaults are present, and the existing LRV tests still pass.

- [ ] **Step 6: Commit**

```bash
git add qmra/risk_assessment/forms.py qmra/risk_assessment/user_models.py qmra/risk_assessment/templates/treatments-form-fieldset.html qmra/risk_assessment/templates/treatments-form-js.html qmra/risk_assessment/tests/test_risk_assessment_form.py
git commit -m "feat: expose treatment failure inputs in the UI"
```

---

### Task 3: Make the annual risk calculation failure-aware

**Files:**
- Modify `qmra/risk_assessment/risk.py`
- Extend `qmra/risk_assessment/tests/test_assess_risk.py`

- [x] **Step 1: Write regression tests for the calculation path**

Add one test that proves the old behavior remains unchanged when failure frequency is zero:

```python
def test_zero_failure_frequency_matches_current_results(self):
    base_results = assess_risk(given_ra, given_inflows, given_treatments)
    updated_results = assess_risk(given_ra, given_inflows, given_treatments_with_failure_defaults)
    assert_that(updated_results["Rotavirus"].infection_maximum_lrv_median).is_close_to(
        base_results["Rotavirus"].infection_maximum_lrv_median, tolerance=1e-12
    )
```

Add one test that proves a non-zero failure frequency changes the output in the expected direction for a controlled toy case:

```python
def test_nonzero_failure_frequency_changes_daily_probability(self):
    # One treatment, one pathogen, fixed inputs, failure_frequency_days_per_year=365.
    # Assert the failure-aware output differs from the zero-failure baseline.
```

- [x] **Step 2: Run the risk tests and confirm they fail**

Run:

```bash
python manage.py test qmra.risk_assessment.tests.test_assess_risk -v 2
```

Expected: the new tests fail until the calculation branch exists.

- [x] **Step 3: Implement the failure-aware helper**

Update the risk pipeline so it keeps the current annual product structure, but uses a failure-adjusted daily probability when any treatment has a non-zero failure frequency.

Use this structure:
- compute the current normal-path LRV exactly as today
- compute a failure-path LRV for each treatment chain using `failure_duration_minutes / 1440` as the active fraction of the day
- aggregate the daily probability as `normal` for `365 - n_fail` days and `failure` for `n_fail` days
- keep the returned `RiskAssessmentResult` shape unchanged

Keep the implementation local to `risk.py`; do not change the result model unless a test proves it is required.

- [x] **Step 4: Re-run the risk tests**

Run:

```bash
python manage.py test qmra.risk_assessment.tests.test_assess_risk -v 2
```

Expected: the zero-failure regression passes and the non-zero failure case shows the failure branch is active.

- [ ] **Step 5: Commit**

```bash
git add qmra/risk_assessment/risk.py qmra/risk_assessment/tests/test_assess_risk.py
git commit -m "feat: add failure-aware risk calculation"
```

---

### Task 4: Update exports and finish the regression pass

**Files:**
- Modify `qmra/risk_assessment/exports.py`
- Extend `qmra/risk_assessment/tests/test_export.py`
- Optionally revisit `qmra/risk_assessment/templates/assessment-result-export.html` only if the export format changes

- [x] **Step 1: Write an export regression test**

Add a test that exports a risk assessment with a treatment carrying the new fields and asserts the CSV contains both `failure_duration_minutes` and `failure_frequency_days_per_year`.

- [x] **Step 2: Run the export tests and confirm they fail**

Run:

```bash
python manage.py test qmra.risk_assessment.tests.test_export -v 2
```

Expected: the treatment export is missing the new columns until the exporter is updated.

- [x] **Step 3: Add the new columns to the exporter**

Update the treatment CSV export so it includes the failure-event fields alongside the current LRV columns. Keep the row ordering stable so existing downstream consumers only see two appended columns.

- [x] **Step 4: Run the full risk-assessment test slice**

Run:

```bash
python manage.py test qmra.risk_assessment.tests -v 2
```

Expected: all treatment, risk, and export tests pass together.

- [ ] **Step 5: Commit**

```bash
git add qmra/risk_assessment/exports.py qmra/risk_assessment/tests/test_export.py
git commit -m "feat: include failure fields in exports"
```

---

### Self-Review Checklist

- [x] Every spec requirement maps to a task: treatment data model, default data, UI inputs, failure-aware risk calculation, and tests.
- [x] No placeholder language remains, such as `TBD`, `TODO`, or "add appropriate validation".
- [x] Field names are consistent across models, forms, templates, JS, exports, and tests.
- [x] Zero failure frequency is covered by a regression test and keeps the existing calculation path unchanged.
- [x] The seeded `qmra` database is explicitly treated as separate from production user data, with backup and rollback steps documented.
- [x] `UserTreatment` backup and rollback are documented separately from the seeded `qmra` database.
- [x] The production runbook clearly separates backup, deploy, verify, and rollback steps.
- [x] The plan stays within one feature slice and does not expand into unrelated refactors.
