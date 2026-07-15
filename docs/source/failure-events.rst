Integration of Failure Events into the QMRA Framework
======================================================

Summary
-------

This feature adds two new treatment-level inputs to the UI and to the risk
calculation pipeline so that treatment failure events can be represented in the
QMRA model.

The current treatment table already stores minimum and maximum log-removal
values for bacteria, viruses, and protozoa. The new feature extends each
treatment with two additional columns:

* ``failure_duration_minutes``: average duration of a failure event in minutes.
* ``failure_frequency_days_per_year``: number of failure-event days per year.

Default values
--------------

To keep existing assessments stable, the new fields should default to:

* failure duration: ``30`` minutes
* failure frequency: ``0`` days per year

These defaults mean that existing risk assessments continue to behave exactly
as they do today unless the user explicitly enters failure-event data.

Expected user-facing behavior
-----------------------------

Each treatment row in the configurator should show the two new columns alongside
the existing minimum and maximum LRV inputs.

Validation expectations:

* failure duration must be an integer between ``1`` and ``1440`` when used
  explicitly
* failure frequency must be a numeric value between ``0`` and ``365``
* default values should be prefilled in the UI

Storage assumptions:

* both values are stored directly on each ``Treatment`` record
* failure duration is stored as an integer field
* failure frequency is stored as a floating-point field to match the requested
  UI range

Calculation behavior
--------------------

The risk calculation needs to distinguish between:

* normal operation days
* days affected by a failure event

The existing LRV minimum and maximum values remain the inputs for treatment
performance. The new failure-event values are used to adjust the daily infection
risk when a treatment failure is active.

The failure-event logic should preserve backward compatibility:

* if ``failure_frequency_days_per_year`` is ``0``, the current calculation path
  is used
* if ``failure_frequency_days_per_year`` is greater than ``0``, the assessment
  must calculate a failure-day risk in addition to the normal-day risk

The implementation should treat the duration as the active fraction of the day
affected by failure, using ``failure_duration_minutes / 1440`` as the time
share for the failure window.

Suggested formulas
------------------

The current model uses the annual infection risk:

.. math::

   P_{inf,year} = 1 - \prod_{d=1}^{365} (1 - p_{inf,day,d})

and the current daily infection probability:

.. math::

   p_{inf,day} = 1 - e^{-\frac{c_{in} \cdot V}{10^{LRV}}}

For failure events, the daily risk should be split into a normal part and a
failure part.

Normal-day risk:

.. math::

   p_{inf,day,normal} = 1 - e^{-\frac{r \cdot c_{in} \cdot V}{10^{LRV_{normal}}}}

Failure-day risk:

.. math::

   p_{inf,day,failure} = 1 - e^{-\frac{r \cdot Vc_{in} \cdot V}{10^{LRV_{failure}}}}

Suggested mixed daily LRV (only needed for best-case calculation):

.. math::

   LRV_{failure,mix} = -log(\frac{x_{fail}}{10^{LRV_{failure,max}}}+\frac{1-x_{fail}} {10^{LRV_{max}}})

where:

############# Equations need to be checked:
.. math::

   x_{fail} = \frac{failure\_duration\_minutes}{1440}

If the calculation needs to work on a per-year basis with explicit failure
events, the annual infection risk can be written as:

.. math::

   P_{inf,year} = 1 - (1 - p_{inf,day,normal})^{365-n_{fail}} \cdot (1 - p_{inf,day,failure})^{n_{fail}}

where:

.. math::

   n_{fail} = failure\_frequency\_days\_per\_year

This is the smallest change to the current model if the code keeps the same
annual-risk structure and only swaps in a failure-adjusted daily probability.
####################

Treatment LRV adjustment
------------------------

When a failure event occurs in one treatment step, the treatment chain LRV for
that step should be reduced by the failing step's LRV contribution. A suggested
representation is:

.. math::

   LRV_{failure} = LRV_{total} - LRV_{treatment}

For a chain that mixes normal and failing operation during the same day, a
weighted LRV can be expressed as:

.. math::

   LRV_{mix} = -\log_{10}\left(\frac{x_{fail}}{10^{LRV_{failure}}} + \frac{1-x_{fail}}{10^{LRV_{normal}}}\right)

This formula describes how the current treatment LRV is blended during failure
windows. It changes the current calculation only if the implementation chooses
to model mixed operation within a day; otherwise the code can keep the current
annual formula and only switch daily probabilities for failure days.

Current formula impact
----------------------

The current annual-risk formula itself does not have to be removed. The planned
change is:

* keep the current annual aggregation structure
* add a failure-aware branch for daily risk
* use the same annual product formula, but with ``p_{inf,day,mix}`` when
  failure parameters are present

In other words, the shape of the model stays the same, but the daily probability
input changes from a single value to a failure-aware mixture.

Implementation scope
--------------------

The change is expected to touch the following areas:

* ``qmra/risk_assessment/models.py``
  * add the two new treatment fields
  * define defaults at the model level if appropriate
* ``qmra/risk_assessment/forms.py``
  * expose the two fields in ``TreatmentForm``
  * validate ranges and defaults
  * keep the formset behavior aligned with the table layout
* ``qmra/risk_assessment/templates/treatments-form-fieldset.html``
  * add the two new columns to the treatment table
* ``qmra/risk_assessment/templates/treatments-form-js.html``
  * ensure dynamically added treatment rows include the new inputs
* ``qmra/risk_assessment/risk.py``
  * update the annual-risk calculation so failure days are accounted for
  * decide whether the failure logic is implemented as a mixed daily
    probability or as a separate failure branch per day
  * keep the existing result shape stable if possible
* ``qmra/risk_assessment/tests/``
  * add coverage for default values
  * add coverage for validation
  * add regression tests for unchanged results when failure frequency is ``0``

Suggested implementation plan
-----------------------------

1. Add the new treatment fields to the data model and create the migration.
2. Update the treatment form, formset, and templates so the UI shows the new
   columns and pre-populates the defaults.
3. Extend the risk calculation to use the failure-event parameters.
4. Add tests for validation, default values, and backward compatibility.
5. Update any export or plot logic only if the result structure changes.

Implementation decisions
------------------------

* The new fields are per-treatment inputs, not shared globally.
* The UI should show the defaults on every blank treatment row so users see the
  expected starting values immediately.
* The initial release should keep the result presentation unchanged unless the
  calculation itself requires a new summary field.
