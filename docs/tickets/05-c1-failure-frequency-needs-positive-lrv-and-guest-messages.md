# 05: Failure frequency only on steps with a positive LRV (D4), with messages for guests too

**What to build:** A treatment step can only have a failure frequency above 0 if at least one of its LRVs is positive, because a failure removes only positive LRVs (D4). The configurator checks this when the assessment is run or saved, and the error appears on the failure frequency field.

Guests can use the failure fields too, and the same rules apply to them. Today, when a guest runs an assessment with invalid input, the guest result sends back an empty error and nothing appears on the page. With this Ticket, the guest result sends back the error messages and the configurator shows them on the affected treatment step, as it does for registered users. This also makes the existing LRV errors, such as minimum above maximum, visible to guests.

Delivered on branch `c1-failure-inputs` as part of the single C1 pull request.

Source: Spec C1 Failure inputs (`docs/specs/c1-failure-inputs.md`), roadmap decision D4. The Spec issue does not exist yet. GitHub issue #22.

**Blocked by:** 04 (#21)

**Status:** in-progress

- [x] A failure frequency above 0 is rejected, with a message on the failure frequency field, if none of the step's six LRVs (minimum and maximum for bacteria, viruses and protozoa) is above 0. An empty LRV counts as 0.
- [x] A step whose only positive LRV is one maximum (for example protozoa 0–2) accepts a failure frequency above 0.
- [x] A step with only negative LRVs (recontamination) or only empty LRVs keeps failure frequency 0. A higher value is rejected.
- [x] A guest sees the failure fields, can run an assessment with valid failure inputs, and nothing is stored.
- [x] When a guest's input is invalid, whether a failure input or an LRV, the guest result sends back the error messages and the configurator shows them on the affected step. The rules are the same as for registered users.
- [x] HTTP-level tests cover the D4 cases on the saved configurator and on the guest result, and cover rejection with a message on the guest result. The existing test suite passes unchanged.
