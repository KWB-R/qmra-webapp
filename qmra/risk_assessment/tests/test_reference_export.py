"""the export package changes only on purpose (quality goal Export stability)"""
import io
import os
import re
import shutil
from pathlib import Path
from zipfile import ZipFile

from assertpy import assert_that
from django.test import TestCase
from django.urls import reverse

from qmra.risk_assessment.models import RiskAssessment, Inflow, Treatment
from qmra.user.models import User

REFERENCE = Path(__file__).parent / "reference_export"
FILE_LIST = REFERENCE / "files.txt"
PACKAGE = REFERENCE / "package"
# the plots are only checked for presence: their rendering can differ between machines
PLOTS = ["results-plots/infection-probability.png", "results-plots/dalys-pppy.png"]
UPDATE_REFERENCE = os.getenv("UPDATE_REFERENCE_EXPORT") == "1"


def is_compared(name: str) -> bool:
    """Whether a ZIP entry is compared by content: not a folder and not a plot."""
    return not name.endswith("/") and name not in PLOTS


NUMBER = re.compile(r"-?\d+(?:\.\d+)?(?:e[-+]?\d+)?")
# Tiny best-case probabilities are computed as 1 - exp(-k * dose), where most digits cancel, so machines with other
# processors or math libraries differ by up to about 1e-5 relative (seen between CI and a developer machine).
RELATIVE_TOLERANCE = 1e-3


def masked(name: str, content: bytes) -> str:
    """The content of an exported file as it is compared; the plots embedded in the report are masked."""
    text = content.decode("utf-8")
    if name.endswith(".html"):
        text, plots = re.subn(r"base64,\s*[A-Za-z0-9+/=]+", "base64, <plot>", text)
        assert_that(plots).described_as(f"plots masked in {name}").is_equal_to(len(PLOTS))
    return text


def assert_same_content(name: str, actual: str, expected: str):
    """The text of a file identical, and each of its numbers within the relative tolerance."""
    assert_that(NUMBER.sub("#", actual)).described_as(name).is_equal_to(NUMBER.sub("#", expected))
    for value, reference in zip(NUMBER.findall(actual), NUMBER.findall(expected)):
        assert_that(float(value)).described_as(f"{name}: {value} instead of {reference}").is_close_to(
            float(reference), abs(float(reference)) * RELATIVE_TOLERANCE)


class TestReferenceExport(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("reference-user", "reference-user@test.com", "password")
        self.client.force_login(self.user)
        self.assessment = RiskAssessment.objects.create(
            user=self.user, name="Reference assessment", description="Benchmark for the export package",
            source_name="groundwater", exposure_name="drinking water", events_per_year=365, volume_per_event=1)
        # fixed values rather than bundled data, so a data release doesn't change the reference
        for pathogen, (low, high) in {"Rotavirus": (0.01, 0.1), "Campylobacter jejuni": (0.1, 1),
                                      "Cryptosporidium parvum": (0.01, 0.1)}.items():
            Inflow.objects.create(risk_assessment=self.assessment, pathogen=pathogen, min=low, max=high)
        steps = [
            dict(name="Slow sand filtration", bacteria_min=2, bacteria_max=6, viruses_min=0.25, viruses_max=4,
                 protozoa_min=0.3, protozoa_max=5),
            dict(name="UV disinfection 20 mJ/cm2, drinking", bacteria_min=4.6, bacteria_max=6, viruses_min=1,
                 viruses_max=3, protozoa_min=2.5, protozoa_max=3, failure_frequency=10, failure_duration=60),
        ]
        for index, step in enumerate(steps):
            Treatment.objects.create(risk_assessment=self.assessment, train_index=index, **step)

    def export(self) -> dict[str, bytes]:
        response = self.client.get(reverse("assessment-export", args=[self.assessment.id]))
        assert_that(response.status_code).is_equal_to(200)
        with ZipFile(io.BytesIO(response.content)) as archive:
            return {name: archive.read(name) for name in archive.namelist()}

    def update_reference(self, export: dict[str, bytes]):
        shutil.rmtree(PACKAGE, ignore_errors=True)
        FILE_LIST.parent.mkdir(parents=True, exist_ok=True)
        FILE_LIST.write_text("".join(f"{name}\n" for name in sorted(export)), encoding="utf-8")
        for name, content in export.items():
            if is_compared(name):
                path = PACKAGE / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(masked(name, content), encoding="utf-8")

    def test_export_package_matches_the_reference(self):
        export = self.export()
        if UPDATE_REFERENCE:
            self.update_reference(export)
            self.skipTest("reference export updated; review the changes before committing them")

        assert_that(str(FILE_LIST)).described_as("no reference export stored yet").exists()
        assert_that(sorted(export)).described_as("files of the export package").is_equal_to(
            FILE_LIST.read_text(encoding="utf-8").splitlines())
        for name, content in export.items():
            if name in PLOTS:
                assert_that(content).described_as(name).is_not_empty()
            elif is_compared(name):
                assert_that(str(PACKAGE / name)).described_as(f"reference of {name}").exists()
                assert_same_content(name, masked(name, content), (PACKAGE / name).read_text(encoding="utf-8"))
