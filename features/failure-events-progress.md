# Failure Events Progress

Date: 2026-07-16

## Completed

- Added `failure_duration_minutes` and `failure_frequency_days_per_year` to treatment models and migration support.
- Updated treatment forms, templates, and JS to show and carry the new failure-event fields.
- Added failure-aware risk calculation handling with zero-failure behavior preserved.
- Updated exports to include the new treatment fields.
- Regenerated static default treatment data.
- Added backend regression tests for models, forms, risk, and export behavior.
- Added a Playwright UI test for the full assessment flow.
- Fixed the assessment page initialization so exposure auto-fill works in the browser.

## Verification

- `.\.venv\Scripts\python.exe manage.py test qmra.risk_assessment.tests -v 2`
- `npx playwright test e2e/assessment.spec.ts --workers=1`

## Notes

- The local app was verified on `http://127.0.0.1:8002/`.
- The seeded `qmra` database remains separate from production user data.
- `UserTreatment` remains part of the application database and is covered by the rollback notes in the implementation plan.
