"""test computation of risk assessment"""
import warnings

from django.test import TestCase
from assertpy import assert_that

from qmra.risk_assessment.models import RiskAssessment, Inflow, Treatment, DefaultTreatments, RiskAssessmentResult, \
    DefaultPathogens, DefaultInflows
from qmra.risk_assessment.risk import assess_risk
from qmra.user.models import User


class TestAssesRisk(TestCase):
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
            for _, t in DefaultTreatments.data.items()
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
            ) for p, _ in DefaultPathogens.data.items()
        ]
        given_treatments = [
            Treatment.from_default(DefaultTreatments.get("Conventional clarification"), given_ra),
            Treatment.from_default(DefaultTreatments.get("Slow sand filtration"), given_ra),
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
                pathogen=inflow.pathogen_name,
                min=inflow.min, max=inflow.max
            ) for inflow in DefaultInflows.get("groundwater")
        ]
        given_treatments = [
            Treatment.from_default(DefaultTreatments.get("Primary treatment"), given_ra)
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