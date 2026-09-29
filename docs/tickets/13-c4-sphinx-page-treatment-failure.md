# 13: Sphinx page Treatment failure

**What to build:** The Sphinx documentation (`docs/source/`) gets a page "Treatment failure", linked from `index.rst`. It explains the method in more detail than the FAQ:
- the inputs and their ranges;
- failure days per exposure event, and why the application departs from the 365-day sequence of the source method (ADR-0001);
- worst-case full loss for the whole day;
- the mixed-water assumption with Eq. 5;
- the rules for combined failures;
- D4 (only positive LRVs are lost).

It cites ADR-0001 and `docs/QMRA_Failure_Approach.md`.

The text is a draft written by Claude for domain expert review before the release.

Source: Change C4 in `docs/failure_roadmap.md` (Small, no Spec), the same method sources as #32. GitHub issue #33.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] `docs/source/` has a page "Treatment failure" covering the points above, linked from `index.rst`.
- [ ] The documentation builds without errors, checked in a local Sphinx environment (Sphinx isn't in the requirements).
- [ ] The page uses the glossary terms and agrees with `CONTEXT.md` and the implemented calculation.
- [ ] The pull request marks the text as a draft for domain expert review.
