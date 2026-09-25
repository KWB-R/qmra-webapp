"""test computation of risk assessment"""
import warnings

from django.core.management import call_command
from django.test import TestCase
from assertpy import assert_that

from qmra.risk_assessment.models import RiskAssessment, Inflow, Treatment, RiskAssessmentResult
from qmra.risk_assessment.qmra_models import QMRAPathogens, QMRAInflows, QMRATreatments
from qmra.risk_assessment.risk import assess_risk
from qmra.user.models import User


class TestAssesRisk(TestCase):
    databases = ["default", "qmra"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        call_command("seed_default_db")

    def test_with_standard_pathogens_and_all_treatments(self):
        given_user = User.objects.create_user("test-user", "test-user@test.com", "password")
        given_user.save()
        given_ra = RiskAssessment.objects.create(
            user=given_user,
            events_per_year=1,
            volume_per_event=2,
        )
        given_ra.save()
        given_inflows = [
            Inflow.objects.create(
                risk_assessment=given_ra,
                pathogen="Rotavirus",
                min=0.1, max=0.2
            ),
            Inflow.objects.create(
                risk_assessment=given_ra,
                pathogen="Campylobacter jejuni",
                min=0.1, max=0.2
            ),
            Inflow(
                risk_assessment=given_ra,
                pathogen="Cryptosporidium parvum",
                min=0.1, max=0.2
            ),
        ]
        given_treatments = [
            Treatment.from_default(t, given_ra)
            for _, t in QMRATreatments.data.items()
        ]
        given_ra.inflows.set(given_inflows, bulk=False)
        given_ra.treatments.set(given_treatments, bulk=False)

        results = assess_risk(given_ra, given_inflows, given_treatments)

        assert_that(len(results)).is_equal_to(len(given_inflows))

        assert_that(sorted([infl.pathogen for infl in given_inflows])).is_equal_to(
            sorted(results.keys())
        )

    def test_with_all_pathogens(self):
        given_user = User.objects.create_user("test-user", "test-user@test.com", "password")
        given_user.save()
        given_ra = RiskAssessment.objects.create(
            user=given_user,
            events_per_year=1,
            volume_per_event=2,
        )
        given_ra.save()
        given_inflows = [
            Inflow.objects.create(
                risk_assessment=given_ra,
                pathogen=p,
                min=0.1, max=0.2
            ) for p, _ in QMRAPathogens.data.items()
        ]
        given_treatments = [
            Treatment.from_default(QMRATreatments.get("Coagulation, flocculation and media filtration"), given_ra),
            Treatment.from_default(QMRATreatments.get("Slow sand filtration"), given_ra),
        ]
        given_ra.inflows.set(given_inflows, bulk=False)
        given_ra.treatments.set(given_treatments, bulk=False)

        results = assess_risk(given_ra, given_inflows, given_treatments)

        assert_that(len(results)).is_equal_to(len(given_inflows))

        assert_that(sorted([infl.pathogen for infl in given_inflows])).is_equal_to(
            sorted(results.keys())
        )

        for pathogen, r in results.items():
            for attr in r.__dict__:
                if "lrv" in attr:
                    assert_that(getattr(r, attr),
                                f"{attr} > 0 for {pathogen}"
                                ).is_greater_than_or_equal_to(0)
                    assert_that(getattr(r, attr),
                                f"{attr} < 1 for {pathogen}"
                                ).is_less_than_or_equal_to(1)

    def test_regression_test(self):
        given_user = User.objects.create_user("test-user", "test-user@test.com", "password")
        given_user.save()
        given_ra = RiskAssessment.objects.create(
            user=given_user,
            # Exposure = drinking water
            events_per_year=365,
            volume_per_event=1,
        )
        given_ra.save()
        given_inflows = [
            Inflow.objects.create(
                risk_assessment=given_ra,
                pathogen=inflow.pathogen.name,
                min=inflow.min, max=inflow.max
            ) for inflow in QMRAInflows.get("groundwater")
        ]
        given_treatments = [
            Treatment.from_default(QMRATreatments.get("Primary treatment"), given_ra)
        ]
        given_ra.inflows.set(given_inflows, bulk=False)
        given_ra.treatments.set(given_treatments, bulk=False)

        expected_rotavirus = RiskAssessmentResult(
            risk_assessment=given_ra,
            infection_minimum_lrv_min=0.9935,
            infection_minimum_lrv_max=1.,
            infection_minimum_lrv_q1=0.999909,
            infection_minimum_lrv_q3=0.999998,
            infection_minimum_lrv_median=0.999984,
            infection_maximum_lrv_min=0.9771782,
            infection_maximum_lrv_max=1.,
            infection_maximum_lrv_q1=0.999764,
            infection_maximum_lrv_q3=0.999993,
            infection_maximum_lrv_median=0.999954,
            dalys_minimum_lrv_min=0.006954503,
            dalys_minimum_lrv_max=0.007,
            dalys_minimum_lrv_q1=0.006999,
            dalys_minimum_lrv_q3=0.006999987,
            dalys_minimum_lrv_median=0.006999891,
            dalys_maximum_lrv_min=0.006840247,
            dalys_maximum_lrv_max=0.007,
            dalys_maximum_lrv_q1=0.00699835,
            dalys_maximum_lrv_q3=0.00699995,
            dalys_maximum_lrv_median=0.00699968,
        )
        expected_jejuni = RiskAssessmentResult(
            risk_assessment=given_ra,
            infection_minimum_lrv_min=0.6206353,
            infection_minimum_lrv_max=0.999927,
            infection_minimum_lrv_q1=0.9586206,
            infection_minimum_lrv_q3=0.992637,
            infection_minimum_lrv_median=0.9822,
            infection_maximum_lrv_min=0.3300553,
            infection_maximum_lrv_max=0.998453,
            infection_maximum_lrv_q1=0.8156798,
            infection_maximum_lrv_q3=0.9479051,
            infection_maximum_lrv_median=0.8980201,
            dalys_minimum_lrv_min=0.0008564767,
            dalys_minimum_lrv_max=0.0013799,
            dalys_minimum_lrv_q1=0.001322896,
            dalys_minimum_lrv_q3=0.00136984,
            dalys_minimum_lrv_median=0.001355435,
            dalys_maximum_lrv_min=0.0004554763,
            dalys_maximum_lrv_max=.001377865,
            dalys_maximum_lrv_q1=0.001125638,
            dalys_maximum_lrv_q3=0.001308109,
            dalys_maximum_lrv_median=0.001239268,
        )
        expected_parvum = RiskAssessmentResult(
            risk_assessment=given_ra,
            infection_minimum_lrv_min=0.4384957,
            infection_minimum_lrv_max=1,
            infection_minimum_lrv_q1=.9648057,
            infection_minimum_lrv_q3=0.999996,
            infection_minimum_lrv_median=0.998185,
            infection_maximum_lrv_min=0.03984487,
            infection_maximum_lrv_max=.999987,
            infection_maximum_lrv_q1=0.2839756,
            infection_maximum_lrv_q3=0.6926215,
            infection_maximum_lrv_median=0.4572991,
            dalys_minimum_lrv_min=0.0004604205,
            dalys_minimum_lrv_max=0.00105,
            dalys_minimum_lrv_q1=0.001013046,
            dalys_minimum_lrv_q3=0.001049996,
            dalys_minimum_lrv_median=0.001048095,
            dalys_maximum_lrv_min=0.0004183712,
            dalys_maximum_lrv_max=0.001049987,
            dalys_maximum_lrv_q1=0.0002981744,
            dalys_maximum_lrv_q3=0.0007272526,
            dalys_maximum_lrv_median=0.0004801641,
        )
        results = assess_risk(given_ra, given_inflows, given_treatments)
        # all pathogens exceeds all tolerable risk levels
        for r in results.values():
            assert_that(r.infection_risk).is_true()
            assert_that(r.dalys_risk).is_true()

        accepted_tolerance_q = .05  # for q1, median, q3
        accepted_tolerance_ex = .2  # for min and max
        failed = ""
        for attr in results["Rotavirus"].__dict__:
            if "lrv" in attr:
                if "min" == attr.split("_")[-1] or "max" == attr.split("_")[-1]:
                    accepted_tolerance = accepted_tolerance_ex
                else:
                    accepted_tolerance = accepted_tolerance_q
                try:
                    assert_that(getattr(results["Rotavirus"], attr),
                                f"'{attr}' fails regression test for rotavirus") \
                        .is_close_to(getattr(expected_rotavirus, attr), tolerance=accepted_tolerance)
                except AssertionError as e:
                    failed += str(e)+"\n"
        for attr in results["Campylobacter jejuni"].__dict__:
            if "lrv" in attr:
                if "min" == attr.split("_")[-1] or "max" == attr.split("_")[-1]:
                    accepted_tolerance = accepted_tolerance_ex
                else:
                    accepted_tolerance = accepted_tolerance_q
                try:
                    assert_that(getattr(results["Campylobacter jejuni"], attr),
                                f"'{attr}' fails regression test for jejuni") \
                        .is_close_to(getattr(expected_jejuni, attr), tolerance=accepted_tolerance)
                except AssertionError as e:
                    failed += str(e)+"\n"
        for attr in results["Cryptosporidium parvum"].__dict__:
            if "lrv" in attr:
                if "min" == attr.split("_")[-1] or "max" == attr.split("_")[-1]:
                    accepted_tolerance = accepted_tolerance_ex
                else:
                    accepted_tolerance = accepted_tolerance_q
                try:
                    assert_that(getattr(results["Cryptosporidium parvum"], attr),
                                f"'{attr}' fails regression test for parvum") \
                        .is_close_to(getattr(expected_parvum, attr), tolerance=accepted_tolerance)
                except AssertionError as e:
                    failed += str(e) + "\n"
        warnings.warn(failed)

    def test_same_scenario_gives_identical_results(self):
        given_ra = RiskAssessment(events_per_year=365, volume_per_event=1)
        given_inflows = [
            Inflow(risk_assessment=given_ra, pathogen=inflow.pathogen.name, min=inflow.min, max=inflow.max)
            for inflow in QMRAInflows.get("groundwater")
        ]
        given_treatments = [
            Treatment(risk_assessment=given_ra, name="Primary treatment",
                      bacteria_min=0, bacteria_max=0.5, viruses_min=0, viruses_max=0.1, protozoa_min=0, protozoa_max=1)
        ]

        def calculate():
            results = assess_risk(given_ra, given_inflows, given_treatments, save=False)
            return {pathogen: r.as_dict() for pathogen, r in results.items()}

        assert_that(calculate()).is_equal_to(calculate())


STATISTICS = ["min", "q1", "median", "q3", "max"]
EXCEEDANCE_ORDER = ["none", "min", "max"]
PATHOGENS = ["Rotavirus", "Campylobacter jejuni", "Cryptosporidium parvum"]


def calculate(steps: list[dict], events_per_year=365) -> dict[str, dict]:
    """The results of a scenario with these treatment steps, as returned by the calculation."""
    given_ra = RiskAssessment(events_per_year=events_per_year, volume_per_event=1)
    given_inflows = [Inflow(risk_assessment=given_ra, pathogen=p, min=0.1, max=10) for p in PATHOGENS]
    given_treatments = [Treatment(risk_assessment=given_ra, name=f"step {i}", **step) for i, step in enumerate(steps)]
    results = assess_risk(given_ra, given_inflows, given_treatments, save=False)
    return {pathogen: r.as_dict() for pathogen, r in results.items()}


def case_statistics(result: dict, case: str) -> list[float]:
    """Both risk measures of one case: 'minimum_lrv' is worst-case, 'maximum_lrv' is best-case."""
    return [result[f"{measure}_{case}_{stat}"] for measure in ["infection", "dalys"] for stat in STATISTICS]


# made-up steps whose LRVs keep the risk well below 1, so failures change the results visibly
STRONG_STEP = dict(bacteria_min=3, bacteria_max=4, viruses_min=3, viruses_max=4, protozoa_min=3, protozoa_max=4)
WEAK_STEP = dict(bacteria_min=2, bacteria_max=3, viruses_min=2, viruses_max=3, protozoa_min=2, protozoa_max=3)


class TestFailureDaysWorstCase(TestCase):

    def test_failure_frequency_0_gives_the_results_without_failure_inputs(self):
        without = calculate([STRONG_STEP, WEAK_STEP])
        with_zero = calculate([dict(STRONG_STEP, failure_frequency=0, failure_duration=600),
                               dict(WEAK_STEP, failure_frequency=0, failure_duration=1)])

        assert_that(with_zero).is_equal_to(without)

    def test_always_failing_step_loses_its_positive_minimum_lrvs_in_worst_case(self):
        failing = calculate([dict(STRONG_STEP, failure_frequency=365), WEAK_STEP])
        without_min_lrvs = calculate([dict(STRONG_STEP, bacteria_min=0, viruses_min=0, protozoa_min=0), WEAK_STEP])

        for pathogen in PATHOGENS:
            with self.subTest(pathogen):
                assert_that(case_statistics(failing[pathogen], "minimum_lrv")).is_equal_to(
                    case_statistics(without_min_lrvs[pathogen], "minimum_lrv"))

    def test_higher_failure_frequency_never_lowers_the_risk(self):
        results = [calculate([dict(STRONG_STEP, failure_frequency=f), WEAK_STEP]) for f in [0, 1, 10, 100, 365]]

        for pathogen in PATHOGENS:
            for step, (lower, higher) in enumerate(zip(results, results[1:])):
                with self.subTest(pathogen=pathogen, step=step):
                    for case in ["minimum_lrv", "maximum_lrv"]:
                        for low, high in zip(case_statistics(lower[pathogen], case),
                                             case_statistics(higher[pathogen], case)):
                            assert_that(high).is_greater_than_or_equal_to(low)
                    for exceedance in ["infection_risk", "dalys_risk"]:
                        assert_that(EXCEEDANCE_ORDER.index(higher[pathogen][exceedance])).is_greater_than_or_equal_to(
                            EXCEEDANCE_ORDER.index(lower[pathogen][exceedance]))
        worst_median = [r["Rotavirus"]["infection_minimum_lrv_median"] for r in results]
        assert_that(worst_median[-1]).is_greater_than(worst_median[0])

    def test_failure_duration_does_not_change_worst_case(self):
        short = calculate([dict(STRONG_STEP, failure_frequency=50, failure_duration=1), WEAK_STEP])
        long = calculate([dict(STRONG_STEP, failure_frequency=50, failure_duration=1440), WEAK_STEP])

        for pathogen in PATHOGENS:
            assert_that(case_statistics(long[pathogen], "minimum_lrv")).is_equal_to(
                case_statistics(short[pathogen], "minimum_lrv"))

    def test_worst_case_is_never_below_best_case(self):
        for frequencies in [(0, 0), (0, 5), (20, 5), (365, 5)]:
            results = calculate([dict(STRONG_STEP, failure_frequency=frequencies[0]),
                                 dict(WEAK_STEP, failure_frequency=frequencies[1])])
            for pathogen in PATHOGENS:
                with self.subTest(frequencies=frequencies, pathogen=pathogen):
                    for worst, best in zip(case_statistics(results[pathogen], "minimum_lrv"),
                                           case_statistics(results[pathogen], "maximum_lrv")):
                        assert_that(worst).is_greater_than_or_equal_to(best)

    def test_failure_removes_only_positive_lrvs(self):
        # bacteria regrow at this step, viruses are removed, protozoa pass unchanged
        step = dict(bacteria_min=-1, bacteria_max=-0.5, viruses_min=3, viruses_max=4, protozoa_min=0, protozoa_max=0)
        normal = calculate([step, WEAK_STEP])
        failing = calculate([dict(step, failure_frequency=365), WEAK_STEP])

        assert_that(failing["Campylobacter jejuni"]).is_equal_to(normal["Campylobacter jejuni"])
        assert_that(failing["Cryptosporidium parvum"]).is_equal_to(normal["Cryptosporidium parvum"])
        assert_that(failing["Rotavirus"]["infection_minimum_lrv_median"]).is_greater_than(
            normal["Rotavirus"]["infection_minimum_lrv_median"])

    def test_same_scenario_with_failures_gives_identical_results(self):
        steps = [dict(STRONG_STEP, failure_frequency=12.5), dict(WEAK_STEP, failure_frequency=40)]

        assert_that(calculate(steps, events_per_year=20)).is_equal_to(calculate(steps, events_per_year=20))
