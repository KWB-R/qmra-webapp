from django.test import TestCase
from assertpy import assert_that

from qmra.risk_assessment.forms import RiskAssessmentForm, InflowForm, InflowFormSet, TreatmentForm, TreatmentFormSet


class TestRiskAssessmentForm(TestCase):
    def test_gt_zero_constraints(self):
        given_form = RiskAssessmentForm(
            data=dict(events_per_year=0, volume_per_event=1)
        )
        given_form.full_clean()
        assert_that(len(given_form.errors)).is_greater_than(0)
        assert_that(given_form.errors).contains_key("events_per_year")

        given_form = RiskAssessmentForm(
            data=dict(events_per_year=1, volume_per_event=0)
        )
        given_form.full_clean()
        assert_that(len(given_form.errors)).is_greater_than(0)
        assert_that(given_form.errors).contains_key("volume_per_event")


class TestInflowForm(TestCase):
    def test_that_pathogen_can_not_be_blank(self):
        given_form = InflowForm(
            data=dict(min=0, max=10, pathogen="")
        )
        given_form.full_clean()
        assert_that(len(given_form.errors)).is_equal_to(1)
        assert_that(given_form.errors).contains_key("pathogen")

    def test_non_negative_constraints(self):
        given_form = InflowForm(
            data=dict(min=-1, max=1), initial=dict(pathogen="Rotavirus")
        )
        given_form.full_clean()
        assert_that(len(given_form.errors)).is_equal_to(1)
        assert_that(given_form.errors).contains_key("min")

        given_form = InflowForm(
            data=dict(min=0, max=-1), initial=dict(pathogen="Rotavirus")
        )
        given_form.full_clean()
        assert_that(len(given_form.errors)).is_equal_to(2)
        assert_that(given_form.errors).contains_key("min")
        assert_that(given_form.errors).contains_key("max")

    def test_that_form_is_valid_when_min_max_eq(self):
        given_form = InflowForm(
            data=dict(min=0, max=0), initial=dict(pathogen="Rotavirus")
        )
        given_form.full_clean()
        assert_that(len(given_form.errors)).is_equal_to(0)

    def test_that_min_needs_to_be_lower_than_max(self):
        given_form = InflowForm(
            data=dict(min=10, max=1), initial=dict(pathogen="Rotavirus")
        )
        given_form.full_clean()
        assert_that(len(given_form.errors)).is_equal_to(2)
        assert_that(given_form.errors).contains_key("min")
        assert_that(given_form.errors).contains_key("max")


class TestInflowFormset(TestCase):
    @classmethod
    def make_formset_data(cls, forms):
        data = {
            "form-INITIAL_FORMS": "0",
            "form-TOTAL_FORMS": str(len(forms)),
            "form-MAX_NUM_FORMS": "1000",
        }
        for i, f in enumerate(forms):
            d = {f"inflow-{i}-{k}": v for k, v in f.items()}
            data = {**data, **d}
        return data


class TestTreatmentForm(TestCase):
    def test_that_negative_are_allowed(self):
        data = dict(
            name="Primary treatment",
            bacteria_min=-2,
            bacteria_max=-1,
            viruses_min=-2,
            viruses_max=-1,
            protozoa_min=-2,
            protozoa_max=-1
        )
        given_form = TreatmentForm(data=data)
        given_form.full_clean()
        print(given_form.errors)
        assert_that(len(given_form.errors)).is_equal_to(0)

    def test_that_min_needs_to_be_less_than_max(self):
        default_data = dict(
            name="Primary treatment",
            bacteria_min=0,
            bacteria_max=0,
            viruses_min=0,
            viruses_max=0,
            protozoa_min=0,
            protozoa_max=0
        )
        for prfx in ["bacteria", "viruses", "protozoa"]:
            mn = prfx + "_min"
            mx = prfx + "_max"
            data = {**default_data, mn: 2, mx: 1}
            given_form = TreatmentForm(data=data)
            given_form.full_clean()
            assert_that(len(given_form.errors)).is_equal_to(1)
            assert_that(given_form.errors).contains_key(mn)
