# 18: Number of parallel units in the treatment table of the export

**What to build:** The export package records the third failure input as well (D7). The treatment table `treatments.csv` gets the column "Number of parallel units" at the end, after "Failure frequency (days per year)" and "Failure duration (minutes)". Like the other two failure inputs, it is repeated on each of the step's three rows (one per pathogen group), so the file keeps its layout of one row per step and pathogen group.

The HTML report stays as it is: it shows no inputs at all, so it doesn't show failure inputs either (decided 2026-09-25).

This is an intended change to the export package, so the reference export is updated in the same commit, by the new column only. The benchmark assessment's inputs stay unchanged, so its results don't change and its step shows 1 parallel unit. The change is noted for the release notes in `docs/progress.md` and in the C3 pull request.

This Ticket also completes the manual check on dev that Ticket 11 left open.

Delivered on branch `c3-failure-inputs-in-export` as part of the C3 pull request (#34). The pull request is tested on the dev environment again and not merged before the release (D5).

Source: Change C3 in `docs/failure_roadmap.md` (Small, no Spec), roadmap decision D7, decisions of 2026-09-25 (report without inputs; failure columns repeated on the step's rows). GitHub issue #40.

**Blocked by:** None (can start immediately; Tickets 14 and 15, which store the number of parallel units, are merged into this branch)

**Status:** ready-for-agent

- [x] `treatments.csv` has the column "Number of parallel units" after the two failure columns, with each step's value on all three of its rows.
- [x] An assessment saved with a number of parallel units exports exactly those values per step, and an assessment saved before C1 exports 1.
- [x] No other file of the export package changes; the HTML report shows no inputs, as before.
- [x] The reference export is updated in the same commit, by the new column only, and the reference test passes.
- [ ] The change is noted for the release notes in `docs/progress.md` and in the C3 pull request.
- [x] Manual check on the dev environment, announced to the team first (also completes Ticket 11's open check) (2026-10-17, passed):
  - Download the export of an assessment with failure inputs, including a number of parallel units above 1.
  - Check the three failure columns in `treatments.csv` and that the report is unchanged.

Quality goals (`docs/vision.md`): Traceability (a reader can see which failure inputs a result is based on), Export stability (the reference export changes only on purpose, by the new column).
