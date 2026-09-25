# 04: Failure inputs on a treatment step in the configurator: enter, check ranges, save, reopen, edit

**What to build:** Every treatment step in the assessment configurator gets two more fields: **failure frequency** (failure days per year) and **failure duration** (minutes). Registered users can save an assessment with these values, and when they reopen or edit it they see the same values again. The values do not change the result yet; the calculation follows in C2.

Tidy-up comes first. The configurator's treatment step form and the personal treatment step form both contain the same minimum ≤ maximum LRV check. It becomes one shared rule that both forms use, and the failure rules are added to it later. This Ticket also adds the first HTTP-level tests. They use Django's test client and a logged-in test user, and they check what a browser or a later request can see.

Delivered on branch `c1-failure-inputs` as part of the single C1 pull request. The pull request stays open until the release (D5).

Source: Spec C1 Failure inputs (`docs/specs/c1-failure-inputs.md`), Change C1 in `docs/failure_roadmap.md`. The Spec issue does not exist yet. GitHub issue #21.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] The minimum ≤ maximum LRV check is defined once and used by both treatment step forms. Nothing changes that a user can notice, and the existing test suite passes unchanged.
- [ ] A schema migration adds failure frequency (a decimal number) and failure duration (a whole number) to the treatment steps of an assessment. Existing rows get failure frequency 0 and failure duration 30.
- [ ] Each treatment step card in the configurator shows both fields below its LRV rows, labelled "Failure frequency (days per year)" and "Failure duration (minutes)". New steps start at 0 and 30, bundled steps included.
- [ ] Failure frequency outside 0–365, and failure duration outside 1–1440 or not a whole number, are rejected with a message on the saved configurator. The duration range is checked even when the frequency is 0.
- [ ] A fractional failure frequency such as 0.5 is accepted.
- [ ] Saving an assessment and reopening it gives back the same failure values for each step. Editing them and saving again stores the new values.
- [ ] Each value stays with its own step when other steps are removed. Two copies of the same bundled step can have different values.
- [ ] An assessment created without failure values, as before the migration, reopens with failure frequency 0 and failure duration 30.
- [ ] An assessment's result and export package are the same with and without failure inputs.
- [ ] All of the above is covered by HTTP-level tests through Django's test client, and the existing test suite passes unchanged.
