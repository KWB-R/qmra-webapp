# 15: Personal treatment steps store the number of parallel units and the configurator copies it in

**What to build:** A registered user can store a number of parallel units on a personal treatment step, next to its failure frequency and failure duration, with the same rule as in the configurator. When they add the step to an assessment, its number of parallel units is copied in together with its other failure inputs and its LRVs. The copy can then be changed in that one assessment without changing the personal treatment step.

Delivered on branch `c1-failure-inputs` and completes the D7 rework of the C1 pull request (#28). The pull request is tested on the dev environment again and not merged before the release (D5).

Source: Spec C1 Failure inputs, revision for D7 (`docs/specs/c1-failure-inputs.md`), roadmap decision D7, ADR-0002. The Spec issue does not exist yet. GitHub issue #37.

**Blocked by:** 14 (#36)

**Status:** ready-for-agent

- [x] A schema migration adds the number of parallel units to personal treatment steps. Existing personal treatment steps get 1.
- [x] The personal treatment step form shows "Number of parallel units", starting at 1, next to the two other failure fields, and applies the same shared rule as the configurator. Invalid input is rejected and the message is shown in the form.
- [x] A personal treatment step saved with a number of parallel units appears with it in its owner's list of personal treatment steps. Another user's list does not contain it.
- [x] Adding a personal treatment step to an assessment copies its number of parallel units into the new step, together with its failure frequency, failure duration and LRVs. Bundled steps still start at 1.
- [x] Changing the copied value in an assessment and saving leaves the personal treatment step unchanged.
- [x] HTTP-level tests cover the form rule, personal treatment steps from before this Ticket reading back 1, and owner-only visibility. The existing test suite passes unchanged.
- [x] Manual check on the dev environment, announced to the team first (2026-10-17, passed):
  - Create a personal treatment step with all three failure inputs, including a number of parallel units above 1, and add it to an assessment.
  - See the copied values, change them, save and reopen.
  - Confirm that the personal treatment step itself is unchanged.

Quality goals (`docs/vision.md`): Input validity (the same rule as the configurator), Privacy of registered-user data (the step and its failure inputs appear only in its owner's list).
