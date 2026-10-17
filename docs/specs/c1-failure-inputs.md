# Spec C1: Failure inputs

Status: draft, 2026-09-24, revised 2026-10-16 for D7 (number of parallel units). Change C1
in `docs/failure_roadmap.md` (Large). Spec issue: #___
Sources: `docs/vision.md` (MVP item 1 and 2), `CONTEXT.md`, ADR-0001, ADR-0002, roadmap
decisions D4, D5 and D7.

The first version (failure frequency and failure duration) is built and was tested on the
dev environment (tickets 04–06). This revision adds the third failure input, the number of
parallel units, and keeps everything else. Requirements that are new in this revision are
marked *(D7)*.

## Problem Statement

A utility operator or engineer who wants to know how failures of their treatment steps
affect the yearly risk has nowhere to say how often a step fails, for how long, and how much
of the step stops when it fails. The assessment configurator only knew LRVs, and a personal
treatment step only stored a name and LRVs. Before the calculation can include treatment
failures (C2), users need a place to enter a failure frequency, a failure duration and a
number of parallel units for each treatment step, and the application needs to keep those
values with the scenario.

In most plants the LRV of a step does not drop to 0 during a failure: a step often has
several parallel units, and a failure event stops only one of them (D7, ADR-0002). Without
the number of parallel units, every failure would be counted as a complete loss of the
step's positive LRVs.

## Solution

Every treatment step in the assessment configurator has three failure fields next to its
LRVs: **failure frequency** (failure days per year), **failure duration** (minutes) and
**number of parallel units** *(D7)*. They start at 0 days per year, 30 minutes and 1 unit,
so a step does not fail unless the user says so, and a step with one unit loses all its
positive LRVs when it fails, as before. The application checks the values when the
assessment is run or saved and explains what is wrong. A step can only have a failure
frequency above 0 if at least one of its LRVs is positive, since a failure removes only
positive LRVs (D4).

Registered users can also store the three values on a personal treatment step. When they
add that step to an assessment, its failure inputs are copied in like its LRVs. Saved
assessments keep the values, and reopening or editing an assessment shows them again.
Assessments and personal treatment steps saved before a failure input existed read back its
default: failure frequency 0, failure duration 30 and 1 parallel unit, so nothing about
them changes.

In this Change the values do not yet affect the result. The calculation follows in C2, and
nothing reaches production before C1–C5 are released together (D5).

## User Stories

1. As a utility operator, I want to enter a failure frequency for each treatment step in my
   assessment, so that the assessment reflects how often each step fails at my plant.
2. As a utility operator, I want to enter a failure duration for each treatment step, so
   that the assessment reflects how long a typical failure event lasts.
3. As a utility operator, I want to enter the number of parallel units of each treatment
   step, so that a failure of one unit is not counted as a failure of the whole step.
   *(D7)*
4. As a user, I want the failure frequency to be given in failure days per year, so that I
   can use the numbers from my plant's operating records directly.
5. As a user, I want the failure duration to be given in minutes, so that short failure
   events can be expressed without fractions.
6. As a user, I want the number of parallel units to be a plain count of units, so that I
   can take it from the plant layout. *(D7)*
7. As a user, I want the unit or meaning of each failure field shown in its label, so that I
   do not enter hours instead of minutes, events instead of days, or a percentage instead of
   a count of units.
8. As a user, I want every treatment step to start with failure frequency 0, so that an
   assessment without failure information behaves as before.
9. As a user, I want every treatment step to start with failure duration 30 minutes, so
   that I only change the duration when I know a better value.
10. As a user, I want every treatment step to start with 1 parallel unit, so that a step I do
    not describe further loses all its positive LRVs during a failure, as before. *(D7)*
11. As a user, I want to enter a fractional failure frequency such as 0.5 days per year, so
    that I can describe a step that fails once every two years.
12. As a user, I want a failure frequency below 0 or above 365 to be rejected with a clear
    message, so that I notice a typing mistake.
13. As a user, I want a failure duration below 1 or above 1440 minutes, or a non-whole
    number of minutes, to be rejected with a clear message, so that I notice a typing
    mistake or a wrong unit.
14. As a user, I want a number of parallel units below 1, or one that is not a whole number,
    to be rejected with a clear message, so that I notice a typing mistake. *(D7)*
15. As a user of a large plant, I want to enter any number of parallel units, however large,
    so that the application does not stop me from describing my plant. *(D7)*
16. As a user, I want to be told when I give a failure frequency above 0 to a step that has
    no positive LRV, so that I understand that such a step cannot fail.
17. As a user modelling recontamination with a negative LRV, I want that step to keep
    failure frequency 0, so that recontamination is never treated as a failing step.
18. As a user, I want a step with a positive LRV for one pathogen group and a zero or
    negative LRV for another to accept failure inputs, so that steps like chlorination
    (protozoa minimum 0) or a storage tank with regrowth can fail.
19. As a user, I want the number of parallel units shown for every treatment step, next to
    failure frequency and failure duration, so that I see all failure inputs of a step
    together and the form does not change shape while I type. *(D7)*
20. As a user describing a non-technical measure such as a hygiene practice, I want the same
    three failure fields, so that I can leave the number of units at 1 and the measure is
    lost completely during a failure. *(D7)*
21. As a user whose units fail together, for example through a shared power supply, I want
    to enter 1 unit, so that such a failure is counted as a loss of the whole step. *(D7)*
22. As a user, I want the failure fields to appear in the same card as the step's LRVs, so
    that I see all values of a step together.
23. As a user, I want the failure values of each step to stay with that step when I reorder
    or remove other steps, so that values do not move to the wrong step.
24. As a user adding the same bundled step twice, I want to give each copy its own failure
    values, so that I can describe two separate installations of the same technology.
25. As a guest, I want to enter all three failure inputs and run an assessment, so that I
    can try the feature without an account.
26. As a guest, I want invalid failure inputs to be rejected in the same way as for
    registered users, so that the rules do not depend on having an account.
27. As a registered user, I want the failure values of each step saved with my assessment,
    so that I do not have to enter them again.
28. As a registered user, I want to see the saved failure values when I reopen an
    assessment, so that I can check what the assessment is based on.
29. As a registered user, I want to change failure values when I edit an assessment and
    have the new values saved, so that I can correct or update them.
30. As a registered user, I want assessments I saved before a failure input existed to
    reopen with its default (failure frequency 0, failure duration 30, 1 parallel unit), so
    that their results do not change.
31. As a registered user, I want to store all three failure inputs on a personal treatment
    step, so that my plant's failure record is reused in every assessment that uses the
    step.
32. As a registered user, I want the same checks on a personal treatment step as in the
    configurator, so that a personal step never carries values an assessment would reject.
33. As a registered user, I want a personal treatment step's failure values, including its
    number of parallel units, copied into the assessment when I add the step, so that I do
    not type them again.
34. As a registered user, I want to change the copied failure values in one assessment
    without changing the personal treatment step, so that I can try other values in one
    scenario.
35. As a registered user, I want personal treatment steps I created before a failure input
    existed to offer its default, so that they keep working.
36. As a registered user, I want my personal treatment steps and their failure values to be
    visible only to me, so that my plant's failure record stays private.
37. As a user comparing scenarios, I want two saved assessments to differ only in their
    failure inputs, for example only in the number of parallel units of one step, so that I
    can later compare the effect of that input.
38. As a user, I want bundled treatment steps to come without failure values, so that I am
    not given literature failure data the application does not have.
39. As a developer of C2, I want the failure frequency, failure duration and number of
    parallel units of every step in an assessment to be available where the calculation
    reads the treatment train, so that C2 only has to change the calculation.
40. As a developer of C3, I want the stored failure values to be readable from a saved
    assessment, so that C3 can add them to the export package.

## Implementation Decisions

- **Three attributes on two kinds of treatment step.** The treatment step of an assessment
  and the personal treatment step each carry *failure frequency* (a decimal number of
  failure days per year), *failure duration* (a whole number of minutes) and *number of
  parallel units* (a whole number) *(D7)*. All three are required, with defaults 0, 30 and
  1. Failure frequency and failure duration exist since tickets 04–06. A new schema
  migration adds the number of parallel units to both kinds of step, and existing rows
  receive 1.
- **Bundled treatment steps are unchanged.** They carry no failure data (failure inputs are
  user input only). A bundled step added to an assessment starts at the defaults.
- **One validation rule, used by both forms.** The treatment step form of the configurator
  and the personal treatment step form apply the same shared rule, which already checks
  minimum ≤ maximum LRV and the first two failure inputs. It is extended, not duplicated:
  - failure frequency from 0 to 365 inclusive, decimals allowed;
  - failure duration a whole number from 1 to 1440 inclusive;
  - number of parallel units a whole number of 1 or more, with no upper limit *(D7)*;
  - failure frequency above 0 only if at least one of the step's six LRVs (minimum and
    maximum for bacteria, viruses and protozoa) is above 0; an empty LRV counts as 0 (D4).
    The error is attached to the failure frequency field.
  The ranges are checked even when the frequency is 0, so stored values are always valid.
  The messages follow the existing pattern and name the field and its range, for example
  "number of parallel units must be a whole number of 1 or more".
- **Configurator.** Each treatment step card shows the three failure fields below its LRV
  rows, labelled "Failure frequency (days per year)", "Failure duration (minutes)" and
  "Number of parallel units". The fields are always shown, also when the failure frequency
  is 0; the D4 rule is enforced by validation, since the user can change LRVs after
  entering a frequency. Guests see and use the same fields. The labels say nothing more;
  what a parallel unit is, that the failure duration affects both best-case and
  worst-case, and that units failing together are entered as 1 unit are explained in C4.
- **Saving and reopening.** The treatment step formset saves the three values with each
  step, and reopening an assessment fills them in again. Each value belongs to its step,
  not to a position in the train.
- **Personal treatment steps.** The personal treatment step form gets the number of
  parallel units next to the two existing failure fields. The list of personal treatment
  steps that the configurator loads includes all three values, and the configurator copies
  them into a newly added step together with its LRVs. The copy is independent: editing it
  in an assessment leaves the personal treatment step unchanged.
- **Guest path.** The guest result submits the same treatment step formset. Failure values
  are validated there too and are not stored.
- **No effect on results.** The calculation, the result page and the export package are not
  changed in C1. The values are stored so that C2 and C3 can use them; C2 reads the number
  of parallel units to calculate the failure LRV (ADR-0002).
- **Delivery.** The number of parallel units is added in new tickets on the existing C1 pull
  request (roadmap decision "Rework of C1–C3"). C1 stays an open pull request and is tested
  on the dev environment again; it is not merged into `main` before the release (D5). C2
  and C3 build on it.

## Testing Decisions

- **What a good test is.** A test drives the application from the outside the way a browser
  does and checks what a user or a later request can observe: the response, the saved
  assessment, the reopened form, the list of personal treatment steps. It does not check
  how validation is organised internally.
- **One seam: HTTP through the Django test client.** Tests post the configurator form (save
  and guest result) and the personal treatment step form, then read the saved assessment,
  the reopened configurator or the personal treatment step list. This covers form
  validation, saving, reopening and ownership without a separate form-level seam. The
  number of parallel units is tested at the same seam as the other two failure inputs.
- **Behaviour covered at that seam** (cases new in this revision marked *(D7)*):
  - a new step card, the guest form and the personal treatment step form show all three
    failure fields with their labels and defaults 0, 30 and 1 *(D7: the third field)*;
  - saving an assessment with failure inputs and reopening it returns the same values,
    including the number of parallel units; editing and saving again stores the new values,
    per step *(D7)*;
  - out-of-range frequency or duration, a non-whole duration, and a frequency above 0 on a
    step without a positive LRV are rejected with a message, on the saved configurator, on
    the guest result and on the personal treatment step form;
  - a number of parallel units of 0, a negative number or a fraction such as 1.5 is rejected
    with a message on all three forms; 1, 2 and a large value such as 1000 are accepted
    *(D7)*;
  - a step whose only positive LRV is one maximum (for example protozoa 0–2) accepts a
    frequency above 0; a step with only negative or empty LRVs does not;
  - a guest result with valid failure inputs is accepted;
  - a personal treatment step saved with failure inputs appears with all three in its
    owner's list; another user's list does not contain it *(D7: the third value)*;
  - an assessment and a personal treatment step created without the number of parallel
    units (as before its migration) come back with 1 *(D7)*, and without any failure values
    with frequency 0, duration 30 and 1 unit;
  - the result and the export package of an assessment are identical with and without
    failure inputs, including a number of parallel units above 1 (C1 does not change the
    calculation) *(D7)*.
- **Prior art.** The C1 HTTP tests in the risk-assessment test package (failure inputs on
  the configurator, guest result and personal treatment steps, with a logged-in test user
  and a parser for the configurator form) are extended with the cases above. The form tests
  in the same package show the minimum ≤ maximum LRV cases; the calculation regression test
  shows how fixed results are compared.
- **Manual check on the dev environment.** Copying a personal treatment step's failure
  values into the configurator happens in the browser and is not covered by the HTTP seam.
  Before C1 is done again, a tester on the dev environment creates a personal treatment step
  with all three failure inputs (including a number of parallel units above 1), adds it to
  an assessment, sees the copied values, changes them, saves, reopens, and confirms the
  personal treatment step itself is unchanged.
- The existing test suite passes unchanged.

## Acceptance criteria

1. Each treatment step in the configurator, for guests and registered users, shows failure
   frequency, failure duration and number of parallel units with their labels, starting at
   0, 30 and 1.
2. The validation rules above reject invalid values with a message on the configurator,
   the guest result and the personal treatment step form, and accept every valid
   combination, including the D4 cases and any whole number of parallel units of 1 or more.
3. All three failure values survive save, reopen and edit of an assessment, per step.
4. Personal treatment steps store all three failure values, the configurator copies them
   into an added step, and the copy can be changed independently (manual check on the dev
   environment).
5. Assessments and personal treatment steps that existed before a failure input read back
   its default: failure frequency 0, failure duration 30, 1 parallel unit.
6. Results and export packages are the same as before C1 for every assessment, whatever its
   failure inputs.
7. All HTTP-level tests listed above pass, and the existing suite passes unchanged.

Quality goals from `docs/vision.md`, one criterion each:

| Quality goal | Criterion in C1 |
|---|---|
| Input validity | Every failure input shows its unit or meaning in its label; a value outside 0–365 days per year or 1–1440 whole minutes, a number of parallel units that is not a whole number of 1 or more, or a frequency above 0 on a step without a positive LRV is rejected with a message (criteria 1–2). |
| Reproducibility | Reopening a saved assessment returns exactly the stored failure values, and assessments from before C1 or before the number of parallel units keep their results, since they read back the defaults (criteria 3, 5, 6). |
| Export stability | The export package of any assessment is unchanged by C1 (criterion 6); adding failure values to it is C3's job. |
| Privacy of registered-user data | A personal treatment step and its failure values appear only in its owner's list; a test requests the list as another user and finds nothing of it (criterion 7). |

The number of parallel units has a lower bound but no upper bound (D7), although the Input
validity goal asks for a plausible range. That is intended: a mistyped large value can only
raise the failure LRV towards log10 of the number of units, at most to the step's normal
LRV (ADR-0002), so it cannot produce an implausible result. ADR-0002 is not reopened.

Not relevant to C1: *Scientific correctness* (the calculation is untouched; C2 and C5) and
*Traceability* (showing failure inputs in the export package is C3).

## Out of Scope

- Any effect of failure inputs on the calculation, the result page or the reference-level
  exceedance, including the failure LRV and the daily LRV (C2, ADR-0002).
- Failure inputs in the export package (C3). The HTML report shows no inputs and does not
  get failure inputs either (decided 2026-09-25).
- Explanations beyond field labels and units: what a parallel unit is, that the failure
  duration affects both cases, that units failing together are entered as 1 unit, and the
  rest of the FAQ, guided tour and Sphinx documentation (C4).
- Benchmark scenarios (C5).
- Failure data for bundled treatment steps, including a number of parallel units.
- Units of one step that fail together; such a step is entered with 1 unit (D7).
- A failure frequency per unit; it stays per step (D7).
- Marking treatment steps as non-technical measures; every step that accepts failure
  inputs gets the same three fields (D7).
- Hiding the failure fields in production; D5 keeps C1 out of `main` instead.
- A browser test setup; the one browser-only behaviour is checked manually.
- The naming follow-ups in `docs/domain-model-open-questions.md` and the deferred UI
  wording.

## Further Notes

- Until C2 is reworked, the number of parallel units has no effect on results, and C2's
  current code still uses the rules ADR-0002 replaces. That is acceptable only because of
  D5: C1–C3 stay out of `main` and production until the release.
- The default failure duration stays 30 minutes (roadmap, "Rework of C1–C3"). Since
  ADR-0002 it affects worst-case too; C4 explains this, the configurator label does not.
- Saving a personal treatment step still checks the name for uniqueness against the user's
  personal *exposures*, not their personal treatment steps. That is an existing bug outside
  this Change; it is noted here so it is not mistaken for C1 behaviour.
- The open roadmap decisions D1–D3 do not affect C1.
