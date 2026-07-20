import json
import os
import tempfile
from pathlib import Path
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

    def test_runtime_static_root_is_preferred_when_present(self):
        under_test = QMRATreatments
        original_static_root = os.environ.get("STATIC_ROOT")
        original_raw_data = under_test._raw_data
        with tempfile.TemporaryDirectory() as tmpdir:
            runtime_file = Path(tmpdir) / "data" / "default-treatments.json"
            runtime_file.parent.mkdir(parents=True, exist_ok=True)
            runtime_file.write_text(
                json.dumps({
                    "Runtime treatment": {
                        "id": 999,
                        "name": "Runtime treatment",
                        "group": "Filtration",
                        "description": "loaded from runtime static root",
                        "bacteria_min": 1.0,
                        "bacteria_max": 2.0,
                        "viruses_min": 1.0,
                        "viruses_max": 2.0,
                        "protozoa_min": 1.0,
                        "protozoa_max": 2.0,
                        "bacteria_references": [],
                        "viruses_references": [],
                        "protozoa_references": [],
                    }
                }),
                encoding="utf-8",
            )
            os.environ["STATIC_ROOT"] = tmpdir
            under_test._raw_data = None

            assert_that(under_test.raw_data).contains_key("Runtime treatment")
            assert_that(under_test.raw_data).does_not_contain_key("UV/H2O2")

        if original_static_root is None:
            os.environ.pop("STATIC_ROOT", None)
        else:
            os.environ["STATIC_ROOT"] = original_static_root
        under_test._raw_data = original_raw_data


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
