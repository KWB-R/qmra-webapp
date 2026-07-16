import io

from assertpy import assert_that
from django.test import TestCase
import pandas as pd

from qmra.risk_assessment import exports
from qmra.risk_assessment.models import RiskAssessment, Inflow, Treatment
from qmra.risk_assessment.qmra_models import QMRATreatments
from qmra.risk_assessment.risk import assess_risk
from qmra.user.models import User


class TestResultExport(TestCase):

    def test_that(self):
        given_user = User.objects.create_user("test-user2", "test-user@test.com", "password")
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
            for t in list(QMRATreatments.data.values())[:3]
        ]
        given_ra.inflows.set(given_inflows, bulk=False)
        given_ra.treatments.set(given_treatments, bulk=False)

        results = assess_risk(given_ra, given_inflows, given_treatments)
        given_ra = RiskAssessment.objects.get(pk=given_ra.id)
        with io.BytesIO() as buffer:
            exports.risk_assessment_as_zip(buffer, given_ra)
            buffer.seek(0)
            with open("test.zip", "wb") as f:
                f.write(buffer.getvalue())
            assert_that(buffer).is_not_none()

    def test_treatments_export_includes_failure_fields(self):
        given_user = User.objects.create_user("test-user3", "test-user@test.com", "password")
        given_ra = RiskAssessment.objects.create(
            user=given_user,
            events_per_year=1,
            volume_per_event=2,
        )
        given_inflow = Inflow.objects.create(
            risk_assessment=given_ra,
            pathogen="Rotavirus",
            min=0.1,
            max=0.2,
        )
        given_treatment = Treatment.from_default(QMRATreatments.get("Primary treatment"), given_ra)
        given_ra.inflows.set([given_inflow], bulk=False)
        given_ra.treatments.set([given_treatment], bulk=False)
        assess_risk(given_ra, [given_inflow], [given_treatment])

        treatments_df = exports.treatments_as_df(given_ra.treatments)

        assert_that(treatments_df.columns).contains("Failure duration (minutes)")
        assert_that(treatments_df.columns).contains("Failure frequency (days/year)")
