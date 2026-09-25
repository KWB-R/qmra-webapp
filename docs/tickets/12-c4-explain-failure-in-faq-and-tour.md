# 12: Explain treatment failure in the FAQ and the guided tour

**What to build:** Users of the application learn what the failure inputs mean and how the result uses them, without reading the method documents.

- **FAQ:** a new question on treatment failure explains:
  - failure frequency (failure days per year) and failure duration (minutes);
  - that failure days are drawn at random per exposure event (ADR-0001);
  - that a failure removes only the positive LRVs of a step (D4);
  - why worst-case ignores the failure duration;
  - the mixed-water assumption in best-case;
  - combined failures: no overlap within a day, two steps overlapping by the minutes beyond a day, and three or more steps longer than a day in total counting like worst-case, counting only steps that lose LRV for the pathogen group.

  The limitations question gets one line: partial loss of removal isn't modelled.
- **Guided tour:** step 4 (Treatment) gets one or two sentences on the two failure fields.

The text uses the glossary terms from `CONTEXT.md`. It is a draft written by Claude and must be reviewed by a domain expert before the release. The pull request says so.

Delivered on a new branch based on `c2-failure-calculation`, together with #33 as the C4 pull request (a draft into `main` only so that it deploys to dev; not merged before the release, D5).

Source: Change C4 in `docs/failure_roadmap.md` (Small, no Spec), `CONTEXT.md` (Treatment failure, Failure day, Failure frequency, Failure duration, Mixed-water assumption, Combined failure), ADR-0001, decisions 1–8 in `docs/QMRA_Failure_Approach.md`, the C2 Spec, and the decisions of 2026-09-25. GitHub issue #32.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] The FAQ has a question on treatment failure covering all points above, consistent with `CONTEXT.md` and the implemented calculation.
- [ ] The FAQ's limitations mention that partial loss of removal isn't modelled.
- [ ] Step 4 of the configurator's guided tour mentions failure frequency and failure duration with their units.
- [ ] Deferred UI wording (such as "tolerable risk level") and explanations of unrelated parts of the model are left as they are.
- [ ] The pull request marks the text as a draft for domain expert review.
