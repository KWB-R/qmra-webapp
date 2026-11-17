"""the Sphinx page on treatment failure agrees with the implemented calculation"""
import re
from pathlib import Path

from assertpy import assert_that
from django.conf import settings
from django.test import SimpleTestCase

from qmra.risk_assessment.risk import failure_lrv, daily_lrv_loss
from qmra.risk_assessment.tests.test_failure_explanations import REPLACED_RULES

SOURCE = Path(settings.BASE_DIR) / "docs" / "source"


def two_decimals(value: float) -> str:
    """A value as the page prints it; failure_lrv gives -0.0 for one unit, printed as 0.00."""
    return f"{value + 0.0:.2f}".replace("-0.00", "0.00")


def toctree_entries(index: str) -> list[str]:
    """The pages listed in the index's toctree: its indented lines that are not options."""
    lines = index.split(".. toctree::")[1].splitlines()[1:]
    block = []
    for line in lines:
        if line and not line.startswith("   "):
            break
        block.append(line.strip())
    return [entry for entry in block if entry and not entry.startswith(":")]


class TestTreatmentFailurePage(SimpleTestCase):

    def setUp(self):
        self.page = (SOURCE / "treatment-failure.rst").read_text()
        self.text = re.sub(r"\s+", " ", self.page)
        self.table_text = re.sub(r"[\s|]+", " ", self.page)  # table rows as one line of cells

    def test_page_is_linked_from_the_index(self):
        assert_that(toctree_entries((SOURCE / "index.rst").read_text())).contains("treatment-failure")

    def test_page_title_is_treatment_failure(self):
        assert_that(self.page.splitlines()[0]).is_equal_to("Treatment failure")

    def test_failure_lrv_table_matches_the_calculation(self):
        for units in [1, 2, 3, 4, 10]:
            row = " ".join(two_decimals(failure_lrv(lrv, units)) for lrv in [1, 2, 4, 6])
            assert_that(self.table_text).contains(f" {units} {row} ")

    def test_worked_example_matches_the_calculation(self):
        # step A LRV 4 and step B LRV 3, one unit each (docs/failure-daily-lrv-example.md)
        one_failing = 7 - daily_lrv_loss(4, 60, 1)
        assert_that(self.text).contains(f"train LRV of that day is {one_failing:.2f}")
        for duration, label in [(60, "60 min"), (240, "4 h"), (720, "12 h"), (960, "16 h")]:
            both_failing = 7 - daily_lrv_loss(4, duration, 1) - daily_lrv_loss(3, duration, 1)
            assert_that(self.table_text).contains(f" {label} {both_failing:.2f} ")
        default_duration = 4 - daily_lrv_loss(4, 30, 1)
        assert_that(self.text).contains(f"daily LRV of {default_duration:.2f}")
        # a plain average of the LRVs over the day would be far too optimistic
        plain_average = (4 + 3) * (1 - 60 / 1440)
        assert_that(self.text).contains(f"would give {plain_average:.2f} instead of")

    def test_formulas_ranges_and_sources_are_stated(self):
        assert_that(self.text).contains(
            r"\frac{N-1}{N} \cdot 10^{-LRV} + \frac{1}{N}",
            r"d \cdot 10^{-LRV_{fail}} + (1 - d) \cdot 10^{-LRV}",
            "0 to 365", "1 to 1,440", "default 30", "Hambsch", "ADR-0001", "ADR-0002",
        )

    def test_no_replaced_failure_rules(self):
        assert_that(self.text.lower()).does_not_contain(*REPLACED_RULES)
