# 11: Failure inputs in the treatment table of the export

**What to build:** The export package records which failures a result is based on. The treatment table `treatments.csv` gets two more columns, "Failure frequency (days per year)" and "Failure duration (minutes)". They are repeated on each of the step's three rows (one per pathogen group), so the file keeps its layout of one row per step and pathogen group.

The HTML report stays as it is: it shows no inputs at all today, so it doesn't show failure inputs either. The roadmap's C3 entry is corrected to say so.

This is an intended change to the export package, so the reference export from #30 is updated in the same commit. The pull request notes the change for the release notes (the repository has no release-notes file).

Source: Change C3 in `docs/failure_roadmap.md` (Small, no Spec), decisions of 2026-09-25 (report without inputs; failure columns repeated on the step's rows). GitHub issue #31.

**Blocked by:** 10 (#30)

**Status:** ready-for-agent

- [ ] `treatments.csv` has the columns "Failure frequency (days per year)" and "Failure duration (minutes)", with each step's values on all three of its rows.
- [ ] An assessment saved with failure inputs exports exactly those values per step, and an assessment without failure inputs exports 0 and 30.
- [ ] No other file of the export package changes; the HTML report shows no inputs, as before.
- [ ] The reference export is updated in the same commit, and the reference test passes.
- [ ] The roadmap's C3 entry says that the HTML report is left out because it shows no inputs.
- [ ] The pull request notes the export change for the release notes.
