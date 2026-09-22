<!--
  PR description template. Copy it into the PR when you Ship.
  Each Change or Bug gets one PR, or one per PR group for a Large change split into groups. Open it as a Draft PR, and mark it ready for Review
  only once every box in the Definition of Done is ticked. The Author ticks the boxes;
  the Reviewer checks them.
  Never paste Real data into this description, including the Real-data check.
-->

## What changes

<!-- A few sentences in your own words on what this Change does and why. -->

## Spec and Tickets

<!-- Link the Spec and the Tickets. A Small change has no Spec, so link its entry in docs/roadmap.md; a Bug links its Summary in the Ticket tracker. -->

## Checks

- **Mock-data check** (Controlled server): <!-- what you ran and the result -->
- **Real-data check** (Workstation): <!-- result only, never the data; or "not needed" and why -->
- **Quality goals checked**: <!-- which Quality goals this Change touches and how each was checked; or "none" -->

<!-- You may review your own PR only when it changes docs or tests and no data logic. If you do, add this line: -->
<!-- **Self-review**: this Change touches only docs or tests and no data logic. -->

## Definition of Done

- [ ] Tests pass
- [ ] `code-review` findings are handled (fixed, or answered in this PR)
- [ ] Mock-data check done
- [ ] Real-data check done, or marked not needed above
- [ ] No secrets or Real data committed
- [ ] Glossary, ADRs and Vision document updated if this Change affects them
- [ ] Relevant Quality goals checked
- [ ] I can explain this Change in my own words
