# 03: Rewrite the vision to the template and draft the failure roadmap

**What to build:** The vision document `docs/vision.md` follows the framework's vision template: Purpose, Users, Main workflows, Scope, Out of scope, MVP, Success criteria, Quality goals and Open questions with owners. The MVP is the next useful version of the app: treatment failure, including combined failures. Next to it, a roadmap `docs/failure_roadmap.md` lists the Changes that deliver this MVP, their size (Large with a Spec, or Small and built directly), their order, what can run in parallel, and the decisions that are still open and who owns them.

**Blocked by:** None (can start immediately)

**Status:** in-progress

Done on 24 September 2026 (branch `docs-vision-architecture-glossary`, pull request #17):

- [x] Vision restructured to the template. Technical details moved to `docs/architecture_baseline.md`.
- [x] Six quality goals written as goal, example situation and a check someone can run: scientific correctness, traceability, reproducibility, input validity, export stability, privacy of registered-user data.
- [x] MVP defined as treatment failure in four functionalities, following `docs/QMRA_Failure_Approach.md` and ADR-0001.
- [x] Open questions listed with owners, technical ones marked for Architecture.
- [x] Vision and architecture baseline use the glossary terms (best-case, worst-case, reference-level exceedance).
- [x] Failure roadmap drafted with four Changes (C1 failure inputs, C2 failure calculation, C3 export and report, C4 explanations), dependencies, sequence and four unresolved decisions.
- [x] Roadmap decisions revisited: C2 is built first and tested with internal checks; the comparison with an independent calculation became a fifth Change, C5 failure benchmark (Small), required before release. D4 settled: steps with at least one positive LRV accept failure inputs, and a failure removes only positive LRVs. Expected benchmark values come from an independent Monte Carlo script; domain experts sign off the C5 benchmark comparison before release. The vision's success criterion now covers results only.
- [x] ADR-0001 records why worst-case ignores the failure duration and that failure comparison covers infection risk only. It cites the vision's quality goals by their new names.
- [x] The vision template is copied into `docs/templates/`.

Still to do:

- [ ] Make the MVP list and the roadmap map one to one, as the template asks: today MVP items 1 and 2 both fall into C1, item 4 is split between C2 and C3, and C4 and C5 have no MVP item.
- [ ] Decide whether the roadmap file keeps the name `failure_roadmap.md` or becomes `docs/roadmap.md`, the name the framework's Roadmap stage expects.
- [ ] Fix the site-specific workflow in the vision: only registered users have personal definitions, guests do not.
- [ ] Replace "QMRA project team" in the ADR's Deciders line with names or roles.
- [ ] Create the Spec issues for C1 and C2 and fill in their numbers in the roadmap.
- [ ] Settle the three remaining open decisions in the roadmap: D1 benchmark tolerance, D2 who writes the independent benchmark script (ideally not the C2 author), D3 which one or two domain experts sign off the benchmark comparison. Owners: Wolfgang and Malte. None of them blocks the Specs of C1 and C2.
- [ ] Get pull request #17 reviewed and merged.
