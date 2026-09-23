# 02: Establish the current product vision and glossary

**What to build:** A short document, `docs/vision.md`, that describes the QMRA web app as it is today. It explains why the tool exists, who uses it, the main things users do with it, and which functions are available now. It describes the current product, not future plans. The purpose is to give the AI agents a reliable description of the existing product. We do not need to answer every open question at this stage. Open questions, contradictions and unfinished behaviour are listed in a short section at the end of the document.

Next to the vision, a glossary: a short list of the key terms of the QMRA app with one clear meaning each, so that the vision and all future work use the same words.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] Malte wrote the first version of the vision.
- [x] Nico aligned the vision with the current code in the GitHub repository KWB-R/qmra-webapp.
- [x] Open questions and contradictions are listed at the end of the vision instead of being resolved now.
- [x] Nico created the glossary.
- [x] The glossary was moved into the file `CONTEXT.md` in the root folder of the repository. This is the place where our framework expects the project vocabulary. Each concept has one agreed term and a list of words to avoid.
- [x] The vision and the glossary were compared with the code. Where they disagreed, the points were written down in `docs/domain-model-open-questions.md` and settled on 23 September 2026. The code changes that follow from them are listed there as later work.
- [x] A review comment on the vision was addressed: the app already has a plot that compares the infection risk of several saved assessments, and the vision now describes it as an existing function.
- [x] Everything is published in pull request #17 (branch `docs-vision-architecture-glossary`).

Follow-up work, not part of this ticket:

- Merge pull request #17.
- Later code changes recorded in `docs/domain-model-open-questions.md`: rename "inflow" to "inflow concentration" in the code and the export file, and mark a bundled source water as "site-specific" once a user edits its values.
