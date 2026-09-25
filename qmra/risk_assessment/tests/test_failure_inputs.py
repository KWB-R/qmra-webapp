"""failure inputs of treatment steps, tested over HTTP like a browser uses the configurator"""
import io
from html.parser import HTMLParser
from zipfile import ZipFile

from assertpy import assert_that
from django.test import TestCase
from django.urls import reverse

from qmra.risk_assessment.models import RiskAssessment, Inflow, Treatment
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


LRVS = dict(bacteria_min=1, bacteria_max=2, viruses_min=1, viruses_max=2, protozoa_min=1, protozoa_max=2)


class TestFailureInputs(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("test-user", "test-user@test.com", "password")
        self.client.force_login(self.user)

    def new_configurator(self) -> dict:
        data = configurator_data(self.client.get(reverse("assessment")))
        for i in range(3):
            data[f"inflow-{i}-min"] = "10"
            data[f"inflow-{i}-max"] = "100"
        data["ra-source_name"] = "groundwater"
        data["ra-exposure_name"] = "drinking water"
        data["ra-events_per_year"] = "365"
        data["ra-volume_per_event"] = "1"
        return data

    def post_configurator(self, data: dict, assessment: RiskAssessment = None):
        url = reverse("assessment") if assessment is None else reverse("assessment", args=[assessment.id])
        return self.client.post(url, data)

    def save_new(self, data: dict) -> RiskAssessment:
        response = self.post_configurator(data)
        assert_that(response.status_code).is_equal_to(302)
        return RiskAssessment.objects.get(user=self.user)

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
        data = self.new_configurator()
        add_step(data, "Primary treatment", **LRVS)

        assessment = self.save_new(data)

        assert_that(failure_inputs_per_step(self.reopen(assessment))).is_equal_to([
            dict(name="Primary treatment", failure_frequency=0, failure_duration=30)
        ])

    def test_failure_inputs_survive_save_and_reopen_per_step(self):
        data = self.new_configurator()
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
        data = self.new_configurator()
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
                data = self.new_configurator()
                add_step(data, "Primary treatment", **LRVS,
                         failure_frequency=frequency, failure_duration=duration)

                response = self.post_configurator(data)

                assert_that(response.status_code).is_equal_to(200)
                assert_that(response.content.decode()).contains(message)
                assert_that(RiskAssessment.objects.filter(user=self.user).count()).is_equal_to(0)

    def test_range_bounds_are_accepted(self):
        for frequency, duration in [("0", "1"), ("365", "1440"), ("0.5", "30")]:
            with self.subTest(frequency=frequency, duration=duration):
                data = self.new_configurator()
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

    def test_result_and_export_do_not_change_with_failure_inputs(self):
        data = self.new_configurator()
        add_step(data, "Primary treatment", **LRVS)
        add_step(data, "Slow sand filtration", **LRVS)
        assessment = self.save_new(data)
        results_before = self.results(assessment)
        export_before = self.export(assessment)

        data = self.reopen(assessment)
        data["treatments-0-failure_frequency"] = "20"
        data["treatments-0-failure_duration"] = "120"
        data["treatments-1-failure_frequency"] = "365"
        self.post_configurator(data, assessment)

        assert_that(failure_inputs_per_step(self.reopen(assessment))[0]["failure_frequency"]).is_equal_to(20)
        assert_that(self.results(assessment)).is_equal_to(results_before)
        assert_that(self.export(assessment)).is_equal_to(export_before)
