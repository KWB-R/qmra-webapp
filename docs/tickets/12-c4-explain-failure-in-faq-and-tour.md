# 12: Explain treatment failure in the FAQ and the guided tour

**Revised 2026-10-17** for D6 and D7 (ADR-0002, `docs/review-2026-10-dev-scenarios.md`): the first version explained why worst-case ignores the failure duration and the overlap rules for combined failures; both were replaced. Not built yet.

**What to build:** Users of the application learn what the failure inputs mean and how the result uses them, without reading the method documents.

- **FAQ:** a new question on treatment failure explains:
  - the three failure inputs of a treatment step: failure frequency (failure days per year), failure duration (minutes) and number of parallel units;
  - that failure days are drawn at random per exposure event (ADR-0001);
  - the failure LRV: a failure event stops one parallel unit and the others keep working, so a step with one unit loses its LRV during the failure, and a step with N units keeps at most log₁₀ N (for example 0.3 for two units) (D7);
  - the daily LRV under the mixed-water assumption: the water used on a failure day is a mixture of water treated during the failure and in normal operation, in proportion to the failure duration;
  - that best-case and worst-case use the same rule and differ only in the LRV a step starts from (its maximum or minimum LRV), so the failure duration affects both cases (D6);
  - combined failures: the failing steps' daily LRVs add up, as if each failure happened at a random time of day;
  - that a failure removes only the positive LRVs of a step (D4).

  The limitations question gets one line: units of a step that fail together, for example through a shared power supply, are not modelled; such a step is entered with one unit.
- **Guided tour:** step 4 (Treatment) gets one or two sentences on the three failure fields.

The text uses the glossary terms from `CONTEXT.md`. It is a draft written by Claude and must be reviewed by a domain expert before the release. The pull request says so.

Delivered on a new branch `c4-failure-explanations` based on `c3-failure-inputs-in-export` (so the C4 tickets and the export are there), together with #33 as the C4 pull request (a draft into `main` only so that it deploys to dev; not merged before the release, D5).

Source: Change C4 in `docs/failure_roadmap.md` (Small, no Spec), `CONTEXT.md` (Treatment failure, Failure day, Failure frequency, Failure duration, Parallel units, Failure LRV, Mixed-water assumption, Daily LRV, Combined failure), ADR-0001, ADR-0002, roadmap decisions D4, D6 and D7, the worked example `docs/failure-daily-lrv-example.md`, and the C2 Spec. GitHub issue #32.

**Blocked by:** None (can start immediately)

**Status:** done (the PR criterion is checked when the C4 pull request is opened)

- [x] The FAQ has a question on treatment failure covering all points above, consistent with `CONTEXT.md` and the implemented calculation.
- [x] The FAQ's limitations mention that units of a step failing together are not modelled and that such a step is entered with one unit.
- [x] Step 4 of the configurator's guided tour mentions failure frequency, failure duration and the number of parallel units, with their units.
- [x] Nothing in the FAQ or the tour says that worst-case ignores the failure duration or describes overlap rules for combined failures.
- [x] Deferred UI wording (such as "tolerable risk level") and explanations of unrelated parts of the model are left as they are.
- [ ] The pull request marks the text as a draft for domain expert review.
