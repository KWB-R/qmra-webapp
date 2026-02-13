from unittest import TestCase
from assertpy import assert_that
from qmra.risk_assessment.qmra_models import PathogenGroup, QMRASource, QMRASources, QMRAPathogen, \
    QMRAPathogens, QMRATreatment, QMRATreatments, QMRAExposure, QMRAExposures


class TestDefaultPathogens(TestCase):
    expected_length = 3
    def test_properties(self):
        under_test = QMRAPathogens

        assert_that(under_test.raw_data).is_instance_of(dict)
        assert_that(len(under_test.raw_data)).is_equal_to(self.expected_length)

        assert_that(under_test.data).is_instance_of(dict)
        assert_that(under_test.data[list(under_test.data.keys())[0]]).is_instance_of(QMRAPathogen)
        assert_that(len(under_test.data)).is_equal_to(self.expected_length)

    def test_get(self):
        under_test = QMRAPathogens

        rotavirus = under_test.get("Rotavirus")
        assert_that(rotavirus).is_instance_of(QMRAPathogen)
        assert_that(rotavirus.name).is_equal_to("Rotavirus")
        assert_that(rotavirus.group).is_equal_to(PathogenGroup.Viruses)

        jejuni = under_test.get("Campylobacter jejuni")
        assert_that(jejuni).is_instance_of(QMRAPathogen)
        assert_that(jejuni.name).is_equal_to("Campylobacter jejuni")
        assert_that(jejuni.group).is_equal_to(PathogenGroup.Bacteria)

        parvum = under_test.get("Cryptosporidium parvum")
        assert_that(parvum).is_instance_of(QMRAPathogen)
        assert_that(parvum.name).is_equal_to("Cryptosporidium parvum")
        assert_that(parvum.group).is_equal_to(PathogenGroup.Protozoa)

    def test_choices(self):
        under_test = QMRAPathogens

        choices = under_test.choices()
        # print(choices)
        assert_that(choices).is_instance_of(list)
        # assert_that(len(choices)).is_equal_to(self.expected_length+2)  # other, blank
        assert_that(choices[0]).is_instance_of(tuple)
        assert_that(choices[0][0]).is_instance_of(str)
        assert_that(choices[0][1]).is_instance_of(str)


class TestDefaultSources(TestCase):
    expected_length = 8

    def test_properties(self):
        under_test = QMRASources

        assert_that(under_test.raw_data).is_instance_of(dict)
        assert_that(len(under_test.raw_data)).is_equal_to(self.expected_length)

        assert_that(under_test.data).is_instance_of(dict)
        assert_that(under_test.data[list(under_test.data.keys())[0]]).is_instance_of(QMRASource)
        assert_that(len(under_test.data)).is_equal_to(self.expected_length)

    def test_choices(self):
        under_test = QMRASources

        choices = under_test.choices()
        # print(choices)
        assert_that(choices).is_instance_of(list)
        # assert_that(len(choices)).is_equal_to(self.expected_length+2)  # other, blank
        assert_that(choices[0]).is_instance_of(tuple)
        assert_that(choices[0][0]).is_instance_of(str)
        assert_that(choices[0][1]).is_instance_of(str)


class TestDefaultTreatments(TestCase):
    expected_length = 22

    def test_properties(self):
        under_test = QMRATreatments

        assert_that(under_test.raw_data).is_instance_of(dict)
        assert_that(len(under_test.raw_data)).is_equal_to(self.expected_length)

        assert_that(under_test.data).is_instance_of(dict)
        assert_that(under_test.data[list(under_test.data.keys())[0]]).is_instance_of(QMRATreatment)
        assert_that(len(under_test.data)).is_equal_to(self.expected_length)

    def test_choices(self):
        under_test = QMRATreatments

        choices = under_test.choices()
        # print(choices)
        assert_that(choices).is_instance_of(list)
        # assert_that(len(choices)).is_equal_to(self.expected_length+2)  # other, blank
        assert_that(choices[0]).is_instance_of(tuple)
        assert_that(choices[0][0]).is_instance_of(str)
        assert_that(choices[0][1]).is_instance_of(str)


class TestDefaultExposures(TestCase):
    expected_length = 8

    def test_properties(self):
        under_test = QMRAExposures

        assert_that(under_test.raw_data).is_instance_of(dict)
        assert_that(len(under_test.raw_data)).is_equal_to(self.expected_length)

        assert_that(under_test.data).is_instance_of(dict)
        assert_that(under_test.data[list(under_test.data.keys())[0]]).is_instance_of(QMRAExposure)
        assert_that(len(under_test.data)).is_equal_to(self.expected_length)

    def test_choices(self):
        under_test = QMRAExposures

        choices = under_test.choices()
        # print(choices)
        assert_that(choices).is_instance_of(list)
        # assert_that(len(choices)).is_equal_to(self.expected_length+2)  # other, blank
        assert_that(choices[0]).is_instance_of(tuple)
        assert_that(choices[0][0]).is_instance_of(str)
        assert_that(choices[0][1]).is_instance_of(str)