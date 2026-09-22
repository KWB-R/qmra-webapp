# Domain model: open questions

Status: open. Raised on 2026-09-22 while deriving `CONTEXT.md` from the original
`docs/glossary.md` and cross-checking both against the code. `CONTEXT.md` has since
replaced that glossary, which was removed; "the glossary" below refers to `CONTEXT.md`. Resolve each item, update `CONTEXT.md`, then
remove it from this list.

## Conflicts between glossary and code

1. **"Inflow" has no glossary entry, but code and exports use it.**
   The glossary describes source water as "represented by minimum and maximum pathogen
   concentrations". In the code a source water is only a name and description; the
   per-pathogen concentration range is a separate object called an inflow, and it is
   exported to users as `inflows.csv`. `CONTEXT.md` now defines *Inflow* as the canonical
   term and narrows *Source water* to the named type.
   **Question:** keep "inflow", or choose another word for the per-pathogen range?

2. **"Scenario" is used for three different things.**
   - Glossary: one combination of source-water, exposure and treatment assumptions.
   - Saved-assessments page: "maximum risk scenario" / "minimum risk scenario" for the
     minimum-LRV and maximum-LRV cases.
   - Guided tour: "custom exposure scenario" for an exposure.
   `CONTEXT.md` lists the last two under *Avoid*.
   **Question:** fix the UI wording in the docs PR, on a separate branch, or record only?

3. **"Tolerable risk level" appears on the result plots.**
   The glossary prefers "health-based reference level". The plot label is the one place
   users see the competing term.
   **Question:** same as 2.

4. **Assessment and scenario are one entity in code.**
   A saved assessment holds exactly one source water, one exposure and one treatment
   train; there is no scenario object. `CONTEXT.md` keeps *Scenario* and states that an
   assessment contains exactly one, so the term is ready for future comparison work.
   **Question:** agree to keep the distinction in language only?

## Terms added to CONTEXT.md that the glossary lacks

- **Pathogen group** (bacteria, viruses, protozoa). LRVs are defined per group and the
  engine maps each reference pathogen to its group.
- **Reference**: a literature citation attached to bundled data. The code sometimes calls
  this a "source", which collides with source water.
- **Reference-level exceedance**: the three-way verdict per pathogen (exceeds in both LRV
  cases, only in the minimum-LRV case, or neither). The code calls it a risk category
  with values max / min / none. It was unnamed anywhere.

**Question:** confirm these three terms and their names.

## Scenarios to stress-test the model

1. A registered user selects the bundled "groundwater" source water and then edits the
   Rotavirus concentration by hand. Is the assessment's source water still "groundwater",
   or is it now a site-specific input with no name? The code keeps the name and the edited
   numbers, so the name no longer describes the data.
2. The guided tour allows a negative LRV to simulate recontamination. Is a recontamination
   step a treatment step, or a different concept that shares the form?
3. A treatment step with a maximum LRV above 6 triggers a warning. Is 6 a domain rule
   worth naming (an LRV plausibility limit), or only a UI nicety?

## ADR candidates

None so far. "An assessment holds exactly one scenario" is neither hard to reverse nor
surprising, so it does not need an ADR.
