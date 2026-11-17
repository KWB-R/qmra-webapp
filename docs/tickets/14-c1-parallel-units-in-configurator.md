# 14: Number of parallel units on a treatment step in the configurator: enter, check, save, reopen, edit

**What to build:** Every treatment step in the assessment configurator gets a third failure input next to failure frequency and failure duration: the **number of parallel units**, starting at 1. Guests and registered users see and use it. Registered users can save an assessment with it, and when they reopen or edit the assessment they see the same value again, for each step. The value does not change the result yet; the failure LRV follows in C2 (ADR-0002).

The shared validation rule that both treatment step forms use is extended with the new input, not duplicated. A number of parallel units is a whole number of 1 or more, with no upper limit (D7).

Delivered on branch `c1-failure-inputs` as part of the C1 pull request (#28). The pull request is tested on the dev environment again and not merged before the release (D5).

Source: Spec C1 Failure inputs, revision for D7 (`docs/specs/c1-failure-inputs.md`), Change C1 in `docs/failure_roadmap.md`, roadmap decision D7, ADR-0002. The Spec issue does not exist yet. GitHub issue #36.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [x] A schema migration adds the number of parallel units to the treatment steps of assessments. Existing treatment steps get 1.
- [x] Each treatment step card in the configurator shows the field "Number of parallel units" below the LRV rows, next to failure frequency and failure duration, starting at 1. It is always shown, also when the failure frequency is 0. Guests see the same field.
- [x] A bundled treatment step added to an assessment starts at 1 parallel unit.
- [x] The shared rule rejects a number of parallel units of 0, a negative number or a fraction such as 1.5 with a message that names the field and its range, on the saved configurator and on the guest result. 1, 2 and a large value such as 1000 are accepted.
- [x] Saving an assessment and reopening it returns the same number of parallel units per step. Editing and saving again stores the new value, and values stay with their step when other steps are reordered or removed.
- [x] An assessment saved before this Ticket reopens with 1 parallel unit, failure frequency 0 and failure duration 30, and its result is unchanged.
- [x] The result and the export package of an assessment are identical with and without failure inputs, including a number of parallel units above 1.
- [x] HTTP-level tests through Django's test client cover the cases above, extending the existing C1 failure input tests. The existing test suite passes unchanged.

Quality goals (`docs/vision.md`): Input validity (label and checked range), Reproducibility (saved values and old assessments read back unchanged), Export stability (export package unchanged by C1).
