# 02: Establish the current product vision and glossary

**What to build:** A `docs/vision.md` that describes the current QMRA product as it is: why the tool exists, who uses it, the main user workflows and the functionality available today. It describes the existing product, not its future direction, so that agents have a reliable description to work from. Open questions, inconsistencies and incomplete behaviour are recorded in a short section at the end rather than resolved now. Alongside it, a concise shared glossary that defines the key terms so the vision and all future work use consistent language.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] Malte wrote the first version of the vision
- [x] Nico aligned the vision with the current legacy code in KWB-R/qmra-webapp
- [x] Open questions and inconsistencies are listed at the end of the vision instead of being resolved
- [x] Nico created the glossary
- [x] Glossary folded into `CONTEXT.md` at the repo root, the framework's place for the project vocabulary, with one canonical term per concept and an avoid-list
- [x] Glossary and vision cross-checked against the code; conflicts recorded in `docs/domain-model-open-questions.md` for a later session
- [x] Review comment on the vision addressed: the existing saved-assessment comparison plot is documented as current functionality
- [x] Everything published in PR #17 (branch `docs-vision-architecture-glossary`)

Follow-ups, not part of this ticket:

- Resolve the items in `docs/domain-model-open-questions.md` (inflow naming, "scenario" overloading in the UI, "tolerable risk level" plot label)
- Merge PR #17
