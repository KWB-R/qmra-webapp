# 06: Personal treatment steps store failure inputs and the configurator copies them in

**What to build:** A registered user can store a failure frequency and a failure duration on a personal treatment step, with the same rules as in the configurator. When they add the step to an assessment, its failure values are copied in together with its LRVs. The copy can then be changed in that one assessment without changing the personal treatment step.

Today the personal treatment step form sends back an empty error for invalid input, so the user sees nothing. With this Ticket it shows the messages, the same way it already does for a duplicate name.

Delivered on branch `c1-failure-inputs` and closes the C1 pull request. The pull request is tested on the dev environment and not merged before the release (D5).

Source: Spec C1 Failure inputs (`docs/specs/c1-failure-inputs.md`). The Spec issue does not exist yet. GitHub issue #23.

**Blocked by:** 04 (#21), 05 (#22)

**Status:** in-progress

- [x] A schema migration adds failure frequency and failure duration to personal treatment steps. Existing personal treatment steps get failure frequency 0 and failure duration 30.
- [x] The personal treatment step form shows both fields with their units and applies the same shared rule as the configurator: the ranges, whole minutes, D4 and minimum ≤ maximum LRV. Invalid input is rejected and the message is shown in the form.
- [x] A personal treatment step saved with failure inputs appears with them in its owner's list of personal treatment steps. Another user's list does not contain it.
- [x] Adding a personal treatment step to an assessment copies its failure frequency and failure duration into the new step. Bundled steps still start at 0 and 30.
- [x] Changing the copied values in an assessment and saving leaves the personal treatment step unchanged.
- [x] HTTP-level tests cover the form rules, old personal treatment steps reading back 0 and 30, and owner-only visibility. The existing test suite passes unchanged.
- [ ] Manual check on the dev environment, announced to the team first:
  - Create a personal treatment step with failure inputs and add it to an assessment.
  - See the copied values, change them, save and reopen.
  - Confirm that the personal treatment step itself is unchanged.
