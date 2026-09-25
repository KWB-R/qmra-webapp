"""failure inputs of treatment steps, tested over HTTP like a browser uses the configurator"""
import io
import re
from html.parser import HTMLParser
from zipfile import ZipFile

import pandas as pd
from assertpy import assert_that
from django.test import TestCase
from django.urls import reverse

from qmra.risk_assessment.models import RiskAssessment, Inflow, Treatment
from qmra.risk_assessment.user_models import UserTreatment
from qmra.user.models import User


class ConfiguratorFormParser(HTMLParser):
    """Collects what a browser would submit from the configurator form."""

    def __init__(self):
        super().__init__()
        self.data = {}
        self.in_configurator = False
        self.select_name = None
        self.first_option = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "form":
            self.in_configurator = attrs.get("id") == "configurator"
        if not self.in_configurator:
            return
        if tag == "input" and attrs.get("name"):
            if attrs.get("type") in ("submit", "button"):
                return
            if attrs.get("type") == "checkbox" and "checked" not in attrs:
                return
            self.data[attrs["name"]] = attrs.get("value", "")
        elif tag == "select":
            self.select_name = attrs.get("name")
            self.first_option = None
        elif tag == "option" and self.select_name:
            if self.first_option is None:
                self.first_option = attrs.get("value", "")
                self.data.setdefault(self.select_name, self.first_option)
            if "selected" in attrs:
                self.data[self.select_name] = attrs.get("value", "")

    def handle_endtag(self, tag):
        if tag == "form":
            self.in_configurator = False
        elif tag == "select":
            self.select_name = None


def configurator_data(response) -> dict:
    parser = ConfiguratorFormParser()
    parser.feed(response.content.decode())
    return parser.data


def field_errors(response, name: str) -> list[str]:
    """The error messages the configurator shows below the input with this name."""
    return re.findall(rf'<span id="error_\d+_id_{re.escape(name)}"><strong>(.*?)</strong></span>',
                      response.content.decode())


def add_step(data: dict, name: str, **values):
    """Add a treatment step card the way the configurator's script does: copy the empty form."""
    n = int(data["treatments-TOTAL_FORMS"])
    for key, value in list(data.items()):
        if key.startswith("treatments-__prefix__-") and not key.endswith("-DELETE"):
            data[key.replace("__prefix__", str(n))] = value
    data[f"treatments-{n}-name"] = name
    for field, value in values.items():
        data[f"treatments-{n}-{field}"] = value
    data["treatments-TOTAL_FORMS"] = str(n + 1)


def failure_inputs_per_step(data: dict) -> list[dict]:
    """The treatment step cards of a configurator, in order, with their failure inputs."""
    return [
        dict(name=data[f"treatments-{i}-name"],
             failure_frequency=float(data[f"treatments-{i}-failure_frequency"]),
             failure_duration=int(data[f"treatments-{i}-failure_duration"]))
        for i in range(int(data["treatments-TOTAL_FORMS"]))
    ]


def new_configurator(client) -> dict:
    """A new configurator with groundwater, drinking water and no treatment steps yet."""
    data = configurator_data(client.get(reverse("assessment")))
    for i in range(3):
        data[f"inflow-{i}-min"] = "10"
        data[f"inflow-{i}-max"] = "100"
    data["ra-source_name"] = "groundwater"
    data["ra-exposure_name"] = "drinking water"
    data["ra-events_per_year"] = "365"
    data["ra-volume_per_event"] = "1"
    return data


TREATMENTS_CSV = "exposure-assessment/treatments.csv"


def layout(csv: bytes) -> list[str]:
    """The lines of an exported table with every number replaced, so only its rows and columns remain."""
    return [re.sub(r"-?\d+(\.\d+)?(e[-+]?\d+)?", "#", line) for line in csv.decode().splitlines()]


# high enough that failures change the results visibly instead of leaving them at a risk of 1
HIGH_LRVS = dict(bacteria_min=3, bacteria_max=4, viruses_min=3, viruses_max=4, protozoa_min=3, protozoa_max=4)
LRVS = dict(bacteria_min=1, bacteria_max=2, viruses_min=1, viruses_max=2, protozoa_min=1, protozoa_max=2)


class LoggedInTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("test-user", "test-user@test.com", "password")
        self.client.force_login(self.user)

    def save_new(self, data: dict) -> RiskAssessment:
        response = self.client.post(reverse("assessment"), data)
        assert_that(response.status_code).is_equal_to(302)
        return RiskAssessment.objects.get(user=self.user)


class TestFailureInputs(LoggedInTestCase):

    def post_configurator(self, data: dict, assessment: RiskAssessment = None):
        url = reverse("assessment") if assessment is None else reverse("assessment", args=[assessment.id])
        return self.client.post(url, data)

    def reopen(self, assessment: RiskAssessment) -> dict:
        return configurator_data(self.client.get(reverse("assessment", args=[assessment.id])))

    def results(self, assessment: RiskAssessment) -> dict:
        return {r.pathogen: r.as_dict() for r in RiskAssessment.objects.get(id=assessment.id).results.all()}

    def export(self, assessment: RiskAssessment) -> dict:
        response = self.client.get(reverse("assessment-export", args=[assessment.id]))
        with ZipFile(io.BytesIO(response.content)) as archive:
            return {name: archive.read(name) for name in archive.namelist()}

    def test_new_step_card_shows_failure_fields_with_units_and_defaults(self):
        response = self.client.get(reverse("assessment"))

        assert_that(response.content.decode()).contains(
            "Failure frequency (days per year)", "Failure duration (minutes)")
        data = configurator_data(response)
        assert_that(float(data["treatments-__prefix__-failure_frequency"])).is_equal_to(0)
        assert_that(int(data["treatments-__prefix__-failure_duration"])).is_equal_to(30)

    def test_bundled_step_starts_at_defaults(self):
        data = new_configurator(self.client)
        add_step(data, "Primary treatment", **LRVS)

        assessment = self.save_new(data)

        assert_that(failure_inputs_per_step(self.reopen(assessment))).is_equal_to([
            dict(name="Primary treatment", failure_frequency=0, failure_duration=30)
        ])

    def test_failure_inputs_survive_save_and_reopen_per_step(self):
        data = new_configurator(self.client)
        add_step(data, "Primary treatment", **LRVS, failure_frequency="0.5", failure_duration="15")
        add_step(data, "Primary treatment", **LRVS, failure_frequency="12", failure_duration="600")
        add_step(data, "Slow sand filtration", **LRVS, failure_frequency="365", failure_duration="1440")

        assessment = self.save_new(data)

        assert_that(failure_inputs_per_step(self.reopen(assessment))).is_equal_to([
            dict(name="Primary treatment", failure_frequency=0.5, failure_duration=15),
            dict(name="Primary treatment", failure_frequency=12, failure_duration=600),
            dict(name="Slow sand filtration", failure_frequency=365, failure_duration=1440),
        ])

    def test_editing_stores_new_values_and_values_stay_with_their_step(self):
        data = new_configurator(self.client)
        add_step(data, "Primary treatment", **LRVS, failure_frequency="1", failure_duration="10")
        add_step(data, "Slow sand filtration", **LRVS, failure_frequency="2", failure_duration="20")
        add_step(data, "Primary treatment", **LRVS, failure_frequency="3", failure_duration="30")
        assessment = self.save_new(data)

        data = self.reopen(assessment)
        data["treatments-0-DELETE"] = "on"
        data["treatments-2-failure_frequency"] = "4.5"
        data["treatments-2-failure_duration"] = "45"
        response = self.post_configurator(data, assessment)

        assert_that(response.status_code).is_equal_to(302)
        assert_that(failure_inputs_per_step(self.reopen(assessment))).is_equal_to([
            dict(name="Slow sand filtration", failure_frequency=2, failure_duration=20),
            dict(name="Primary treatment", failure_frequency=4.5, failure_duration=45),
        ])

    def test_out_of_range_or_fractional_values_are_rejected_with_a_message(self):
        cases = [
            ("-1", "30", "failure frequency must be between 0 and 365 days per year"),
            ("365.5", "30", "failure frequency must be between 0 and 365 days per year"),
            ("0", "0", "failure duration must be between 1 and 1440 minutes"),
            ("0", "1441", "failure duration must be between 1 and 1440 minutes"),
            ("1", "2.5", "Enter a whole number."),
            ("1", "", "This field is required."),
            ("", "30", "This field is required."),
        ]
        for frequency, duration, message in cases:
            with self.subTest(frequency=frequency, duration=duration):
                data = new_configurator(self.client)
                add_step(data, "Primary treatment", **LRVS,
                         failure_frequency=frequency, failure_duration=duration)

                response = self.post_configurator(data)

                assert_that(response.status_code).is_equal_to(200)
                assert_that(response.content.decode()).contains(message)
                assert_that(RiskAssessment.objects.filter(user=self.user).count()).is_equal_to(0)

    def test_range_bounds_are_accepted(self):
        for frequency, duration in [("0", "1"), ("365", "1440"), ("0.5", "30")]:
            with self.subTest(frequency=frequency, duration=duration):
                data = new_configurator(self.client)
                add_step(data, "Primary treatment", **LRVS,
                         failure_frequency=frequency, failure_duration=duration)

                response = self.post_configurator(data)

                assert_that(response.status_code).is_equal_to(302)

    def test_assessment_from_before_failure_inputs_reopens_with_defaults(self):
        assessment = RiskAssessment.objects.create(user=self.user, events_per_year=365, volume_per_event=1)
        for pathogen in ["Rotavirus", "Campylobacter jejuni", "Cryptosporidium parvum"]:
            Inflow.objects.create(risk_assessment=assessment, pathogen=pathogen, min=10, max=100)
        Treatment.objects.create(risk_assessment=assessment, name="Primary treatment", **LRVS)

        assert_that(failure_inputs_per_step(self.reopen(assessment))).is_equal_to([
            dict(name="Primary treatment", failure_frequency=0, failure_duration=30)
        ])

    @staticmethod
    def exported_failure_inputs(export: dict) -> list[tuple]:
        """(treatment, pathogen group, failure frequency, failure duration) of each row of the exported treatment table."""
        table = pd.read_csv(io.BytesIO(export[TREATMENTS_CSV]))
        return list(table[["Treatment", "Pathogen group", "Failure frequency (days per year)",
                           "Failure duration (minutes)"]].itertuples(index=False, name=None))

    def saved_assessment_with_two_steps(self) -> RiskAssessment:
        data = new_configurator(self.client)
        add_step(data, "Primary treatment", **HIGH_LRVS)
        add_step(data, "Slow sand filtration", **HIGH_LRVS)
        return self.save_new(data)

    def test_failure_frequency_0_changes_neither_results_nor_export_beyond_the_durations(self):
        assessment = self.saved_assessment_with_two_steps()
        results_before = self.results(assessment)
        export_before = self.export(assessment)

        data = self.reopen(assessment)
        data["treatments-0-failure_duration"] = "120"
        data["treatments-1-failure_duration"] = "1440"
        self.post_configurator(data, assessment)

        assert_that(failure_inputs_per_step(self.reopen(assessment))[0]["failure_duration"]).is_equal_to(120)
        assert_that(self.results(assessment)).is_equal_to(results_before)
        # the export records the new durations in the treatment table; everything else stays identical
        export_after = self.export(assessment)
        durations = {duration for *_, duration in self.exported_failure_inputs(export_after)}
        export_after.pop(TREATMENTS_CSV)
        export_before.pop(TREATMENTS_CSV)
        assert_that(export_after).is_equal_to(export_before)
        assert_that(durations).is_equal_to({120, 1440})

    def test_export_records_the_failure_inputs_of_each_step(self):
        data = new_configurator(self.client)
        add_step(data, "Primary treatment", **HIGH_LRVS, failure_frequency="12.5", failure_duration="90")
        add_step(data, "Slow sand filtration", **HIGH_LRVS)
        assessment = self.save_new(data)

        groups = ["Viruses", "Bacteria", "Protozoa"]
        assert_that(self.exported_failure_inputs(self.export(assessment))).is_equal_to(
            [("Primary treatment", group, 12.5, 90) for group in groups]
            + [("Slow sand filtration", group, 0, 30) for group in groups])

    def test_export_keeps_its_files_and_columns_with_failures(self):
        assessment = self.saved_assessment_with_two_steps()
        results_before = self.results(assessment)
        export_before = self.export(assessment)

        data = self.reopen(assessment)
        data["treatments-0-failure_frequency"] = "20"
        data["treatments-1-failure_frequency"] = "365"
        self.post_configurator(data, assessment)

        assert_that(self.results(assessment)).is_not_equal_to(results_before)
        export_after = self.export(assessment)
        assert_that(sorted(export_after)).is_equal_to(sorted(export_before))
        for name in export_before:
            if name.endswith(".csv"):
                assert_that(layout(export_after[name])).described_as(name).is_equal_to(layout(export_before[name]))


NO_LRVS = dict(bacteria_min="", bacteria_max="", viruses_min="", viruses_max="", protozoa_min="", protozoa_max="")
D4_REJECTED = {
    "empty LRVs": NO_LRVS,
    "zero LRVs": dict(NO_LRVS, bacteria_min=0, bacteria_max=0, viruses_min=0, viruses_max=0),
    "recontamination": dict(bacteria_min=-1, bacteria_max=-0.5, viruses_min=-1, viruses_max=-0.5,
                            protozoa_min=-1, protozoa_max=-0.5),
}
D4_ACCEPTED = {
    "one positive maximum": dict(NO_LRVS, protozoa_min=0, protozoa_max=2),
    "regrowth in one group": dict(bacteria_min=-1, bacteria_max=-0.5, viruses_min=1, viruses_max=2,
                                  protozoa_min=1, protozoa_max=2),
}
D4_MESSAGE = "failure frequency must be 0 for a treatment step without a positive LRV"


class TestFailureOnlyWithPositiveLrv(LoggedInTestCase):

    def save_with_step(self, lrvs: dict, failure_frequency: str):
        data = new_configurator(self.client)
        add_step(data, "Primary treatment", **lrvs, failure_frequency=failure_frequency, failure_duration="30")
        return self.client.post(reverse("assessment"), data)

    def test_step_without_positive_lrv_cannot_fail(self):
        for case, lrvs in D4_REJECTED.items():
            with self.subTest(case):
                response = self.save_with_step(lrvs, failure_frequency="1")

                assert_that(response.status_code).is_equal_to(200)
                assert_that(field_errors(response, "treatments-0-failure_frequency")).is_equal_to([D4_MESSAGE])
                assert_that(RiskAssessment.objects.filter(user=self.user).count()).is_equal_to(0)

    def test_step_without_positive_lrv_keeps_failure_frequency_0(self):
        for case, lrvs in D4_REJECTED.items():
            with self.subTest(case):
                response = self.save_with_step(lrvs, failure_frequency="0")

                assert_that(response.status_code).is_equal_to(302)

    def test_step_with_one_positive_lrv_can_fail(self):
        for case, lrvs in D4_ACCEPTED.items():
            with self.subTest(case):
                response = self.save_with_step(lrvs, failure_frequency="1")

                assert_that(response.status_code).is_equal_to(302)


class TestGuestFailureInputs(TestCase):

    def guest_result(self, **step_values):
        data = new_configurator(self.client)
        add_step(data, "Primary treatment", **{**LRVS, **step_values})
        return self.client.post(reverse("assessment-result"), data)

    def test_guest_sees_failure_fields(self):
        response = self.client.get(reverse("assessment"))

        assert_that(response.content.decode()).contains(
            "Failure frequency (days per year)", "Failure duration (minutes)")

    def test_guest_result_with_failure_inputs_is_shown_and_not_stored(self):
        response = self.guest_result(failure_frequency="12", failure_duration="60")

        assert_that(response.status_code).is_equal_to(200)
        assert_that(RiskAssessment.objects.count()).is_equal_to(0)
        assert_that(Treatment.objects.count()).is_equal_to(0)

    def test_guest_result_sends_back_messages_of_invalid_inputs(self):
        cases = [
            (dict(failure_frequency="366"), "treatments-0-failure_frequency",
             "failure frequency must be between 0 and 365 days per year"),
            (dict(failure_duration="2.5"), "treatments-0-failure_duration", "Enter a whole number."),
            (dict(bacteria_min="3", bacteria_max="1"), "treatments-0-bacteria_min", "min. must be less than max"),
        ]
        for step_values, field, message in cases:
            with self.subTest(field=field, message=message):
                response = self.guest_result(**step_values)

                assert_that(response.status_code).is_equal_to(422)
                assert_that(response.json()["errors"]).contains_entry({field: [message]})
                assert_that(RiskAssessment.objects.count()).is_equal_to(0)

    def test_guest_result_rejects_failing_step_without_positive_lrv(self):
        for case, lrvs in D4_REJECTED.items():
            with self.subTest(case):
                response = self.guest_result(**lrvs, failure_frequency="1")

                assert_that(response.status_code).is_equal_to(422)
                assert_that(response.json()["errors"]).contains_entry(
                    {"treatments-0-failure_frequency": [D4_MESSAGE]})

    def test_guest_result_accepts_step_without_positive_lrv_and_failure_frequency_0(self):
        for case, lrvs in D4_REJECTED.items():
            with self.subTest(case):
                response = self.guest_result(**lrvs, failure_frequency="0")

                assert_that(response.status_code).is_equal_to(200)

    def test_guest_result_accepts_failing_step_with_one_positive_lrv(self):
        for case, lrvs in D4_ACCEPTED.items():
            with self.subTest(case):
                response = self.guest_result(**lrvs, failure_frequency="1")

                assert_that(response.status_code).is_equal_to(200)


def personal_step_form(response) -> str:
    """The HTML of the personal treatment step form on the configurator page."""
    html = response.content.decode()
    start = html.index('id="user-treatment-form"')
    return html[start:html.index("</form>", start)]


class TestPersonalTreatmentStepFailureInputs(LoggedInTestCase):

    def create_personal_step(self, name="Plant UV", **values):
        data = dict(name=name, **LRVS, failure_frequency="0", failure_duration="30")
        data.update(values)
        return self.client.post(reverse("treatment"), data, HTTP_REFERER=reverse("assessment"))

    def personal_steps(self, client=None) -> dict:
        return (client or self.client).get(reverse("treatments")).json()

    def failure_inputs(self, name: str) -> tuple:
        step = self.personal_steps()[name]
        return step["failure_frequency"], step["failure_duration"]

    def test_form_shows_failure_fields_with_units_and_defaults(self):
        form = personal_step_form(self.client.get(reverse("assessment")))

        assert_that(form).contains("Failure frequency (days per year)", "Failure duration (minutes)")
        assert_that(form).matches(r'name="failure_frequency" value="0"')
        assert_that(form).matches(r'name="failure_duration" value="30"')

    def test_failure_inputs_appear_in_the_owners_list(self):
        response = self.create_personal_step(failure_frequency="2.5", failure_duration="90")

        assert_that(response.status_code).is_equal_to(302)
        assert_that(self.failure_inputs("Plant UV")).is_equal_to((2.5, 90))

    def test_other_users_do_not_see_the_personal_step(self):
        self.create_personal_step(failure_frequency="2.5", failure_duration="90")
        other = User.objects.create_user("other-user", "other-user@test.com", "password")
        other_client = self.client_class()
        other_client.force_login(other)

        assert_that(self.personal_steps(other_client)).does_not_contain_key("Plant UV")

    def test_invalid_values_are_rejected_with_a_message(self):
        cases = [
            (dict(failure_frequency="366"), "failure frequency must be between 0 and 365 days per year"),
            (dict(failure_duration="0"), "failure duration must be between 1 and 1440 minutes"),
            (dict(failure_duration="2.5"), "Enter a whole number."),
            (dict(failure_duration=""), "This field is required."),
            (dict(NO_LRVS, failure_frequency="1"), D4_MESSAGE),
            (dict(bacteria_min="3", bacteria_max="1"), "min. must be less than max"),
        ]
        for values, message in cases:
            with self.subTest(message=message, values=values):
                response = self.create_personal_step(**values)

                assert_that(response.status_code).is_equal_to(422)
                assert_that(response.content.decode()).contains(message)
                assert_that(self.personal_steps()).is_empty()

    def test_valid_values_including_d4_cases_are_accepted(self):
        cases = {
            "bounds low": dict(failure_frequency="0", failure_duration="1"),
            "bounds high": dict(failure_frequency="365", failure_duration="1440"),
            "no positive LRV, frequency 0": dict(NO_LRVS, failure_frequency="0"),
            **{case: dict(lrvs, failure_frequency="1") for case, lrvs in D4_ACCEPTED.items()},
        }
        for case, values in cases.items():
            with self.subTest(case):
                response = self.create_personal_step(name=case, **values)

                assert_that(response.status_code).is_equal_to(302)
                assert_that(self.personal_steps()).contains_key(case)

    def test_personal_step_from_before_failure_inputs_offers_defaults(self):
        UserTreatment.objects.create(user=self.user, name="Old step", **LRVS)

        assert_that(self.failure_inputs("Old step")).is_equal_to((0, 30))

    def test_changing_the_copy_in_an_assessment_leaves_the_personal_step_unchanged(self):
        self.create_personal_step(failure_frequency="2.5", failure_duration="90")
        data = new_configurator(self.client)
        add_step(data, "Plant UV", **LRVS, failure_frequency="10", failure_duration="15")

        assessment = self.save_new(data)

        assert_that(failure_inputs_per_step(configurator_data(
            self.client.get(reverse("assessment", args=[assessment.id]))))).is_equal_to([
                dict(name="Plant UV", failure_frequency=10, failure_duration=15)])
        assert_that(self.failure_inputs("Plant UV")).is_equal_to((2.5, 90))
