# Reference export

The stored export package of a fixed benchmark assessment, checked by
`test_reference_export.py` (quality goal *Export stability* in `docs/vision.md`): the content
and layout of the export package change only on purpose.

- `files.txt` lists every entry of the ZIP.
- `package/` holds the exported tables and the HTML report. The report embeds the plots,
  which are masked as `<plot>`. The plots themselves are only checked for presence, because
  their rendering can differ between machines.
- Decimal numbers are stored and compared rounded to 10 significant digits. Numpy versions,
  Python versions and processors differ in the last digits of the Monte Carlo results (CI
  and a developer machine did); a real change to a value is far larger than that.

The benchmark assessment's inputs are fixed values in the test, not bundled default data, so
a new release of bundled source waters or treatment steps doesn't change the reference. The
pathogens' dose-response and DALY parameters still come from the bundled data: if they change,
the result values change, and the test shows it.

## Updating the reference on purpose

When a change to the export package is intended, rewrite the reference from the repository
root and review the difference before committing it together with the change:

```bash
UPDATE_REFERENCE_EXPORT=1 python manage.py test qmra.risk_assessment.tests.test_reference_export
git diff qmra/risk_assessment/tests/reference_export/
```

The test is skipped while it writes the reference. Note the change for the release notes in
the pull request.
