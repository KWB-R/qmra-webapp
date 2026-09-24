# Domain model: open questions

Status: all items resolved or deferred (2026-09-23). Raised on 2026-09-22 while deriving `CONTEXT.md` from the original
`docs/glossary.md` and cross-checking both against the code. `CONTEXT.md` has since
replaced that glossary, which was removed; "the glossary" below refers to `CONTEXT.md`. Resolve each item, update `CONTEXT.md`, then
remove it from this list.

## Follow-ups from resolved items

- **Inflow / outflow concentration (resolved 2026-09-23).** The glossary now uses
  *Inflow concentration* and *Outflow concentration*. Decided target for the code, to be
  done in a later code change (this branch stays docs-only):
  - identifiers `inflow` / `outflow` become `inflow_concentration` /
    `outflow_concentration`;
  - the export file `inflows.csv` becomes `inflow_concentration.csv`.

  Configurator wording ("pathogen concentrations") is left as it is.

- **Site-specific source water (resolved 2026-09-23).** When a user enters or edits any
  inflow concentration of a bundled source water by hand, the assessment's source water
  becomes a site-specific source water. Naming rule for the code: it is named after the
  bundled source water with the prefix "site-specific" (e.g. selecting "groundwater" and
  editing the Rotavirus concentration gives "site-specific groundwater"). Inflow
  concentrations entered without selecting any source water are named plain
  "site-specific source water". Personal definitions already carry the user's own name
  and keep it when edited. The code does not do this yet: it keeps the plain source water
  name next to the edited values, so saved assessments and exports show "groundwater" for
  data that is not the bundled groundwater. To be changed in a later code change.

## Deferred: UI wording that conflicts with the glossary

Decided 2026-09-23: leave the UI as it is for now. The glossary keeps its terms and
lists the UI words under *Avoid*. Where users see them today:

- **"Tolerable risk level"** (glossary: *Health-based reference level*): result summary
  text (`assessment-result.html`, five times, attributed to the WHO), FAQ (`faqs.html`),
  result plots (`plots.py`, `views_v0.py`) and the saved-assessments plot
  (`risk-assessment-list.html`).
- **"Exposure scenario"** (glossary: *Exposure*): FAQ (`faqs.html`, five times), home and
  configurator guided tours, form help text (`views_v0.py`).
- **"Maximum / minimum risk scenario"** (glossary: *Worst-case* / *Best-case*): explanation text on the saved-assessments page (`risk-assessment-list.html`).

## Deferred: LRV above 6

Decided 2026-09-23: leave it for now; the origin of the rule is unclear. What the code
does: each treatment step's maximum LRV per pathogen group is checked against 6
(`models.py`, `above_max_lrv`). Above 6, the result page warns that "the WHO standards
do not allow LRVs above 6 in order to promote redundancy and robustness in treatment
trains" (`assessment-result.html`). Minimum LRVs and the train total are not checked,
and the calculation still uses the value above 6. Open: confirm the WHO source, decide
whether it is a domain rule worth naming (e.g. *single-step LRV limit*), and whether it
should warn or cap.

## ADR candidates

- **Written:** `docs/adr/0001-failure-days-drawn-per-exposure-event.md` (2026-09-23),
  the decision to draw failure days per exposure event inside the Monte Carlo simulation
  instead of following the source method's 365-day sequence.
- **Not needed:** "An assessment holds exactly one scenario" is neither hard to reverse
  nor surprising, so it does not need an ADR.
