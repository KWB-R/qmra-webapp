# 10: Reference test for the export package

**What to build:** Tidy-up before the export package changes. The "Export stability" Quality goal asks for a test that compares the export package of a benchmark assessment with a stored reference export, so that the content and layout of the export package change only on purpose. That test doesn't exist yet.

A fixed benchmark assessment is exported through the application and compared with a reference export stored in the repository:
- the same files in the ZIP;
- every CSV table and the HTML report identical;
- the two plots present. Their image bytes aren't compared, because plot rendering can differ between machines.

A short, documented way to update the reference on purpose is part of this Ticket. The export itself doesn't change.

Delivered on a new branch based on `c2-failure-calculation`, together with #31 as the C3 pull request. The PR targets `main` as a draft only so that it deploys to dev, and it is not merged before the release (D5).

Source: Change C3 in `docs/failure_roadmap.md` (Small, no Spec), the "Export stability" Quality goal in `docs/vision.md`, and the decisions of 2026-09-25. GitHub issue #30.

**Blocked by:** None (can start immediately)

**Status:** review (built in pull request #34, draft; CI green on `27b5268`; stays open until the release, D5)

- [x] A test exports a fixed benchmark assessment and compares it with the stored reference export: the same files, identical CSV tables and HTML report, and both plots present.
- [x] The test fails when a column, a file or a value of the export changes, and its message says which file differs.
- [x] How to update the reference on purpose is documented next to the reference files.
- [x] The export package itself is unchanged, and the existing test suite passes.

Review on 2026-09-28 (commits `7085d78`, `305ec0f`, `27b5268`):

- [x] The test exports a fixed benchmark assessment with fixed inputs, not bundled data, and one failing step, so it also covers the C2 calculation. Plots are checked for presence only and masked inside the report.
- [x] The comparison is not byte-identical, as this ticket first said: text must be identical and each number within 0.1 % relative. The reason is recorded in the README and the PR: tiny probabilities from 1 − exp(−k · dose) differ by up to 10⁻⁵ between CI and the server. A renamed column, a missing file or a 1 % change still fails.
- [ ] Follow-up, not part of C3: computing those probabilities with `expm1` would remove the cancellation and allow a tighter tolerance. That is a change to the calculation and needs its own ticket if wanted.
