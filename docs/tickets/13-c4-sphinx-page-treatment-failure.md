# 13: Sphinx page Treatment failure

**Revised 2026-10-17** for D6 and D7 (ADR-0002, `docs/review-2026-10-dev-scenarios.md`): the first version described the worst-case full loss for the whole day, Eq. 5 in best-case only and the overlap rules for combined failures; these were replaced. Not built yet.

**What to build:** The Sphinx documentation (`docs/source/`) gets a page "Treatment failure", linked from `index.rst`. It explains the method in more detail than the FAQ:
- the three failure inputs and their ranges: failure frequency (0–365 days per year, default 0), failure duration (1–1,440 minutes, default 30) and number of parallel units (a whole number of 1 or more, default 1);
- failure days per exposure event, and why the application departs from the 365-day sequence of the source method (ADR-0001);
- the failure LRV of a step with N parallel units, −log₁₀((N − 1)/N · 10^(−LRV) + 1/N), with the table of examples from the review (D7);
- the daily LRV under the mixed-water assumption, −log₁₀(d · 10^(−failure LRV) + (1 − d) · 10^(−LRV)) with d = failure duration / 1,440, averaged by concentration and never by LRV, used by both cases from the maximum or minimum LRV (D6);
- combined failures: the failing steps' daily LRVs add up, which equals placing each failure event at a random time of day, with the worked example's numbers;
- D4: only positive LRVs are affected;
- how the method differs from the source (Hambsch et al., 2019): per-event draws instead of 365 days (ADR-0001), and worst-case using the failure duration (ADR-0002).

It cites ADR-0001, ADR-0002, `docs/QMRA_Failure_Approach.md` and `docs/failure-daily-lrv-example.md`.

The text is a draft written by Claude for domain expert review before the release.

Source: Change C4 in `docs/failure_roadmap.md` (Small, no Spec), the same method sources as #32. GitHub issue #33.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] `docs/source/` has a page "Treatment failure" covering the points above, linked from `index.rst`.
- [ ] The formulas and the worked example's numbers on the page agree with ADR-0002, the worked example and the implemented calculation.
- [ ] The page describes no worst-case full loss regardless of the duration and no overlap rules for combined failures.
- [ ] The documentation builds without errors, checked in a local Sphinx environment (Sphinx isn't in the requirements).
- [ ] The page uses the glossary terms and agrees with `CONTEXT.md` and the implemented calculation.
- [ ] The pull request marks the text as a draft for domain expert review.
