"""explanations of treatment failure in the FAQ and the configurator's guided tour, as a browser gets them"""
import re
from html import unescape

from assertpy import assert_that
from django.test import TestCase
from django.urls import reverse

FAILURE_QUESTION = "13. How does the tool model treatment failure?"
LIMITATIONS_QUESTION = "14. What are the limitations of this tool?"
# C4 explains D6, which replaced these rules (ADR-0002)
REPLACED_RULES = ["ignores the failure duration", "whole exposure event", "whole day", "overlap"]


def text_of(html: str) -> str:
    """Visible text of an HTML fragment, with whitespace collapsed."""
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html)))


def faq_section(page: str, heading: str) -> str:
    """The text of one FAQ question, from its heading to the next one or the end of the FAQ."""
    faq = page.split('<div class="container w-75 my-4">')[1].split("</div>")[0]
    matching = [s for s in faq.split("<h5>") if s.split("</h5>")[0].strip() == heading]
    assert_that(matching).described_as(f"FAQ question {heading!r}").is_length(1)
    return text_of(matching[0])


def tour_step(page: str, title: str) -> str:
    """The text of one step of the guided tour."""
    match = re.search(r'title: "' + re.escape(title) + r'",\s*content: "((?:[^"\\]|\\.)*)"', page)
    assert_that(match).described_as(f"tour step {title!r}").is_not_none()
    return text_of(match.group(1))


class TestFailureInFaq(TestCase):

    def setUp(self):
        self.page = self.client.get(reverse("faqs")).content.decode()

    def test_treatment_failure_question_explains_inputs_and_rule(self):
        section = faq_section(self.page, FAILURE_QUESTION)
        assert_that(section.lower()).contains(*(term.lower() for term in [
            "failure frequency", "days per year", "failure duration", "minutes", "number of parallel units",
            "exposure event",  # failure days are drawn per exposure event (ADR-0001)
            "failure LRV", "one unit", "0.3",  # D7
            "daily LRV", "mixed-water assumption",
            "best-case", "worst-case", "maximum LRV", "minimum LRV",  # D6
            "combined failure", "random time of day",
            "positive LRVs",  # D4
        ]))

    def test_limitations_mention_units_failing_together(self):
        section = faq_section(self.page, LIMITATIONS_QUESTION)
        assert_that(section).contains("fail together", "with one unit")

    def test_reference_to_the_limitations_question_matches_its_number(self):
        assert_that(self.page).contains(f"see {LIMITATIONS_QUESTION}")
        assert_that(faq_section(self.page, LIMITATIONS_QUESTION)).is_not_empty()

    def test_no_replaced_failure_rules(self):
        section = faq_section(self.page, FAILURE_QUESTION) + faq_section(self.page, LIMITATIONS_QUESTION)
        assert_that(section.lower()).does_not_contain(*REPLACED_RULES)


class TestFailureInGuidedTour(TestCase):

    def setUp(self):
        self.step = tour_step(self.client.get(reverse("assessment")).content.decode(), "Step 4: Treatment")

    def test_treatment_step_mentions_the_three_failure_fields_with_units(self):
        assert_that(self.step).contains(
            "failure frequency (days per year)", "failure duration (minutes)", "number of parallel units")

    def test_no_replaced_failure_rules(self):
        assert_that(self.step.lower()).does_not_contain(*REPLACED_RULES)
