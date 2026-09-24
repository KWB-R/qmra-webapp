# Spec C1: Failure inputs

Status: draft, 2026-09-24. Change C1 in `docs/failure_roadmap.md` (Large). Spec issue: #___
Sources: `docs/vision.md` (MVP item 1 and 2), `CONTEXT.md`, ADR-0001, roadmap decisions D4
and D5.

## Problem Statement

A utility operator or engineer who wants to know how failures of their treatment steps
affect the yearly risk has nowhere to say how often a step fails and for how long. The
assessment configurator only knows LRVs, and a personal treatment step only stores a name
and LRVs. Before the calculation can include treatment failures (C2), users need a place to
enter a failure frequency and a failure duration for each treatment step, and the
application needs to keep those values with the scenario.

## Solution

Every treatment step in the assessment configurator gets two more fields next to its LRVs:
**failure frequency** (failure days per year) and **failure duration** (minutes). They
start at 0 days per year and 30 minutes, so a step does not fail unless the user says so.
The application checks the values when the assessment is run or saved and explains what is
wrong. A step can only have a failure frequency above 0 if at least one of its LRVs is
positive, since a failure removes only positive LRVs (D4).

Registered users can also store both values on a personal treatment step. When they add
that step to an assessment, its failure frequency and failure duration are copied in like
its LRVs. Saved assessments keep the values, and reopening or editing an assessment shows
them again. Assessments saved before this change reopen with failure frequency 0 and
failure duration 30, so nothing about them changes.

In this Change the values do not yet affect the result. The calculation follows in C2, and
nothing reaches production before C1–C5 are released together (D5).

## User Stories

1. As a utility operator, I want to enter a failure frequency for each treatment step in my
   assessment, so that the assessment reflects how often each step fails at my plant.
2. As a utility operator, I want to enter a failure duration for each treatment step, so
   that the assessment reflects how long a typical failure event lasts.
3. As a user, I want the failure frequency to be given in failure days per year, so that I
   can use the numbers from my plant's operating records directly.
4. As a user, I want the failure duration to be given in minutes, so that short failure
   events can be expressed without fractions.
5. As a user, I want the unit of each failure field shown next to it, so that I do not
   enter hours instead of minutes or events instead of days.
6. As a user, I want every treatment step to start with failure frequency 0, so that an
   assessment without failure information behaves as before.
7. As a user, I want every treatment step to start with failure duration 30 minutes, so
   that I only change the duration when I know a better value.
8. As a user, I want to enter a fractional failure frequency such as 0.5 days per year, so
   that I can describe a step that fails once every two years.
9. As a user, I want a failure frequency below 0 or above 365 to be rejected with a clear
   message, so that I notice a typing mistake.
10. As a user, I want a failure duration below 1 or above 1440 minutes, or a non-whole
    number of minutes, to be rejected with a clear message, so that I notice a typing
    mistake or a wrong unit.
11. As a user, I want to be told when I give a failure frequency above 0 to a step that has
    no positive LRV, so that I understand that such a step cannot fail.
12. As a user modelling recontamination with a negative LRV, I want that step to keep
    failure frequency 0, so that recontamination is never treated as a failing step.
13. As a user, I want a step with a positive LRV for one pathogen group and a zero or
    negative LRV for another to accept failure inputs, so that steps like chlorination
    (protozoa minimum 0) or a storage tank with regrowth can fail.
14. As a user, I want the failure fields to appear in the same card as the step's LRVs, so
    that I see all values of a step together.
15. As a user, I want the failure values of each step to stay with that step when I
    reorder or remove other steps, so that values do not move to the wrong step.
16. As a user adding the same bundled step twice, I want to give each copy its own failure
    values, so that two parallel units can have different failure records.
17. As a guest, I want to enter failure inputs and run an assessment, so that I can try the
    feature without an account.
18. As a guest, I want invalid failure inputs to be rejected in the same way as for
    registered users, so that the rules do not depend on having an account.
19. As a registered user, I want the failure values of each step saved with my assessment,
    so that I do not have to enter them again.
20. As a registered user, I want to see the saved failure values when I reopen an
    assessment, so that I can check what the assessment is based on.
21. As a registered user, I want to change failure values when I edit an assessment and
    have the new values saved, so that I can correct or update them.
22. As a registered user, I want assessments I saved before this change to reopen with
    failure frequency 0 and failure duration 30, so that their results do not change.
23. As a registered user, I want to store a failure frequency and failure duration on a
    personal treatment step, so that my plant's failure record is reused in every
    assessment that uses the step.
24. As a registered user, I want the same checks on a personal treatment step as in the
    configurator, so that a personal step never carries values an assessment would reject.
25. As a registered user, I want a personal treatment step's failure values copied into the
    assessment when I add the step, so that I do not type them again.
26. As a registered user, I want to change the copied failure values in one assessment
    without changing the personal treatment step, so that I can try other values in one
    scenario.
27. As a registered user, I want personal treatment steps I created before this change to
    offer failure frequency 0 and failure duration 30, so that they keep working.
28. As a registered user, I want my personal treatment steps and their failure values to be
    visible only to me, so that my plant's failure record stays private.
29. As a user comparing scenarios, I want two saved assessments to differ only in their
    failure inputs, so that I can later compare the effect of different failure
    frequencies.
30. As a user, I want bundled treatment steps to come without failure values, so that I am
    not given literature failure data the application does not have.
31. As a developer of C2, I want the failure frequency and failure duration of every step in
    an assessment to be available where the calculation reads the treatment train, so that
    C2 only has to change the calculation.
32. As a developer of C3, I want the stored failure values to be readable from a saved
    assessment, so that C3 can add them to the export package and report.

## Implementation Decisions

- **Two new attributes on two kinds of treatment step.** The treatment step of an
  assessment and the personal treatment step each get *failure frequency* (a decimal
  number of failure days per year) and *failure duration* (a whole number of minutes).
  Both are required, with defaults 0 and 30. A schema migration adds them to both, and
  existing rows receive the defaults.
- **Bundled treatment steps are unchanged.** They carry no failure data (failure inputs are
  user input only). A bundled step added to an assessment starts at the defaults.
- **One validation rule, used by both forms.** The treatment step form of the configurator
  and the personal treatment step form apply the same rule, defined once:
  - failure frequency from 0 to 365 inclusive, decimals allowed;
  - failure duration a whole number from 1 to 1440 inclusive;
  - failure frequency above 0 only if at least one of the step's six LRVs (minimum and
    maximum for bacteria, viruses and protozoa) is above 0; an empty LRV counts as 0 (D4).
    The error is attached to the failure frequency field.
  The duration range is checked even when the frequency is 0, so stored values are always
  valid. The existing minimum ≤ maximum LRV check, which both forms currently duplicate,
  may move into the same shared rule.
- **Configurator.** Each treatment step card shows the two fields below its LRV rows,
  labelled with their units ("Failure frequency (days per year)", "Failure duration
  (minutes)"). The fields are always shown; the D4 rule is enforced by validation, since the
  user can change LRVs after entering a frequency. Guests see and use the same fields.
- **Saving and reopening.** The treatment step formset saves the two values with each step,
  and reopening an assessment fills them in again. Each value belongs to its step, not to a
  position in the train.
- **Personal treatment steps.** The personal treatment step form gets the two fields. The
  list of personal treatment steps that the configurator loads includes both values, and
  the configurator copies them into a newly added step together with its LRVs. The copy is
  independent: editing it in an assessment leaves the personal treatment step unchanged.
- **Guest path.** The guest result submits the same treatment step formset. Failure values
  are validated there too and are not stored.
- **No effect on results.** The calculation, the result page and the export package are not
  changed in C1. The values are stored so that C2 and C3 can use them.
- **Delivery.** C1 stays an open pull request and is tested on the dev environment; it is
  not merged into `main` before the release (D5). C2 and C3 build on it.

## Testing Decisions

- **What a good test is.** A test drives the application from the outside the way a browser
  does and checks what a user or a later request can observe: the response, the saved
  assessment, the reopened form, the list of personal treatment steps. It does not check
  how validation is organised internally.
- **One seam: HTTP through the Django test client.** Tests post the configurator form (save
  and guest result) and the personal treatment step form, then read the saved assessment,
  the reopened configurator or the personal treatment step list. This covers form
  validation, saving, reopening and ownership without a separate form-level seam.
- **Behaviour covered at that seam:**
  - saving an assessment with failure inputs and reopening it returns the same values;
    editing and saving again stores the new values;
  - out-of-range frequency or duration, a non-whole duration, and a frequency above 0 on a
    step without a positive LRV are rejected with a message, on the saved configurator, on
    the guest result and on the personal treatment step form;
  - a step whose only positive LRV is one maximum (for example protozoa 0–2) accepts a
    frequency above 0; a step with only negative or empty LRVs does not;
  - a guest result with valid failure inputs is accepted;
  - a personal treatment step saved with failure inputs appears with them in its owner's
    list; another user's list does not contain it;
  - an assessment and a personal treatment step created without failure values (as before
    the migration) come back with frequency 0 and duration 30;
  - the result of an assessment is identical with and without failure inputs (C1 does not
    change the calculation).
- **Prior art.** The form tests in the risk-assessment test module (min ≤ max, negative LRVs
  allowed) show the validation cases to extend; the calculation regression test shows how
  fixed results are compared. There are no HTTP-level tests yet; C1 adds the first ones,
  using Django's test client and a logged-in test user.
- **Manual check on the dev environment.** Copying a personal treatment step's failure
  values into the configurator happens in the browser and is not covered by the HTTP seam.
  Before C1 is done, a tester on the dev environment creates a personal treatment step with
  failure inputs, adds it to an assessment, sees the copied values, changes them, saves,
  reopens, and confirms the personal treatment step itself is unchanged.
- The existing test suite passes unchanged.

## Acceptance criteria

1. Each treatment step in the configurator, for guests and registered users, shows failure
   frequency and failure duration with their units, starting at 0 and 30.
2. The validation rules above reject invalid values with a message on the configurator,
   the guest result and the personal treatment step form, and accept every valid
   combination, including the D4 cases.
3. Failure values survive save, reopen and edit of an assessment, per step.
4. Personal treatment steps store failure values, the configurator copies them into an
   added step, and the copy can be changed independently (manual check on the dev
   environment).
5. Assessments and personal treatment steps that existed before C1 read back failure
   frequency 0 and failure duration 30.
6. Results and export packages are the same as before C1 for every assessment.
7. All HTTP-level tests listed above pass, and the existing suite passes unchanged.

Quality goals from `docs/vision.md`, one criterion each:

| Quality goal | Criterion in C1 |
|---|---|
| Input validity | Every failure input shows its unit, and a value outside 0–365 days per year or 1–1440 whole minutes, or a frequency above 0 on a step without a positive LRV, is rejected with a message (criteria 1–2). |
| Reproducibility | Reopening a saved assessment returns exactly the stored failure values, and assessments from before C1 keep their results, since they read back frequency 0 (criteria 3, 5, 6). |
| Export stability | The export package of any assessment is unchanged by C1 (criterion 6); adding failure values to it is C3's job. |
| Privacy of registered-user data | A personal treatment step and its failure values appear only in its owner's list; a test requests the list as another user and finds nothing of it (criterion 7). |

Not relevant to C1: *Scientific correctness* (the calculation is untouched; C2 and C5) and
*Traceability* (showing failure inputs in the export package and report is C3).

## Out of Scope

- Any effect of failure inputs on the calculation, the result page or the reference-level
  exceedance (C2).
- Failure inputs in the export package and the HTML report (C3).
- Explanations of failure frequency, failure duration and the two cases beyond field
  labels and units: FAQ, guided tour, Sphinx documentation (C4).
- Benchmark scenarios (C5).
- Failure data for bundled treatment steps.
- Partial loss of removal (not planned).
- Hiding the failure fields in production; D5 keeps C1 out of `main` instead.
- A browser test setup; the one browser-only behaviour is checked manually.
- The naming follow-ups in `docs/domain-model-open-questions.md` and the deferred UI
  wording.

## Further Notes

- Until C2 is done, failure inputs have no effect on results. That is acceptable only
  because of D5: C1 stays out of `main` and production until the release.
- While exploring: saving a personal treatment step checks the name for uniqueness against
  the user's personal *exposures*, not their personal treatment steps. That is an existing
  bug outside this Change; it is noted here so it is not mistaken for C1 behaviour.
- The open roadmap decisions D1–D3 do not affect C1.
