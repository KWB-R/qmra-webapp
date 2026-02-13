import uuid

from django.db import models
from django.db.models import QuerySet

from qmra.risk_assessment.qmra_models import QMRAPathogens, QMRATreatment
from qmra.user.models import User


# @dtc.dataclass


class Inflow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    risk_assessment = models.ForeignKey("RiskAssessment", related_name="inflows", on_delete=models.CASCADE)
    pathogen = models.CharField(choices=QMRAPathogens.choices(),
                                blank=False, null=False, max_length=256)
    # reference = models.ForeignKey(
    #     Reference, blank=True, null=True, default=None,
    #     on_delete=models.CASCADE)
    min = models.FloatField()
    max = models.FloatField()
    # pathogen_in_ref = models.CharField(max_length=200, default="unknown")
    # notes = models.CharField(max_length=200, default="unknown")


class Treatment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    risk_assessment = models.ForeignKey("RiskAssessment", related_name="treatments", on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    train_index = models.IntegerField(blank=False, null=False, default=0)
    bacteria_min = models.FloatField(blank=True, null=True)
    bacteria_max = models.FloatField(blank=True, null=True)
    viruses_min = models.FloatField(blank=True, null=True)
    viruses_max = models.FloatField(blank=True, null=True)
    protozoa_min = models.FloatField(blank=True, null=True)
    protozoa_max = models.FloatField(blank=True, null=True)

    @classmethod
    def from_default(cls, default: QMRATreatment, risk_assessment):
        return Treatment.objects.create(
            risk_assessment=risk_assessment,
            name=default.name,
            bacteria_min=default.bacteria_min,
            bacteria_max=default.bacteria_max,
            viruses_min=default.viruses_min,
            viruses_max=default.viruses_max,
            protozoa_min=default.protozoa_min,
            protozoa_max=default.protozoa_max,
        )

    def above_max_lrv(self):
        return [field for field in [
            "Viruses LRV Maximum" if self.viruses_max is not None and self.viruses_max > 6 else None,
            "Bacteria LRV Maximum" if self.bacteria_max is not None and self.bacteria_max > 6 else None,
            "Protozoa LRV Maximum" if self.protozoa_max is not None and self.protozoa_max > 6 else None,
        ] if field is not None]


class RiskAssessment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="risk_assessments")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    name = models.CharField(max_length=64, default="", blank=True)
    description = models.TextField(max_length=500, default="", blank=True)
    source_name = models.CharField(blank=True, max_length=256)
    inflows: QuerySet[Inflow]
    treatments: QuerySet[Treatment]
    exposure_name = models.CharField(blank=True, max_length=256)
    events_per_year = models.IntegerField()
    volume_per_event = models.FloatField()

    results: QuerySet["RiskAssessmentResult"]

    @property
    def infection_risk(self):
        risks = {r.infection_risk for r in self.results.all()}
        return 'max' if 'max' in risks else ("min" if 'min' in risks else 'none')

    @property
    def dalys_risk(self):
        return any(r.dalys_risk for r in self.results.all())

    @property
    def pathogens_labels(self):
        return ", ".join([inflow.pathogen for inflow in self.inflows.all()])

    @property
    def treatments_labels(self):
        return ", ".join([treatment.name for treatment in self.treatments.all()])

    def results_list(self):
        return [r.as_dict() for r in self.results.all()]

    def __str__(self):
        return self.name


class RiskAssessmentResult(models.Model):
    risk_assessment = models.ForeignKey(RiskAssessment, on_delete=models.CASCADE, related_name="results")

    pathogen = models.CharField(choices=QMRAPathogens.choices(), max_length=256)
    infection_risk = models.CharField(choices=[("min", "min"), ("max", "max"), ("none", "none")], max_length=4)
    dalys_risk = models.CharField(choices=[("min", "min"), ("max", "max"), ("none", "none")], max_length=4)
    infection_minimum_lrv_min = models.FloatField()
    infection_minimum_lrv_max = models.FloatField()
    infection_minimum_lrv_q1 = models.FloatField()
    infection_minimum_lrv_q3 = models.FloatField()
    infection_minimum_lrv_median = models.FloatField()
    infection_maximum_lrv_min = models.FloatField()
    infection_maximum_lrv_max = models.FloatField()
    infection_maximum_lrv_q1 = models.FloatField()
    infection_maximum_lrv_q3 = models.FloatField()
    infection_maximum_lrv_median = models.FloatField()
    dalys_minimum_lrv_min = models.FloatField()
    dalys_minimum_lrv_max = models.FloatField()
    dalys_minimum_lrv_q1 = models.FloatField()
    dalys_minimum_lrv_q3 = models.FloatField()
    dalys_minimum_lrv_median = models.FloatField()
    dalys_maximum_lrv_min = models.FloatField()
    dalys_maximum_lrv_max = models.FloatField()
    dalys_maximum_lrv_q1 = models.FloatField()
    dalys_maximum_lrv_q3 = models.FloatField()
    dalys_maximum_lrv_median = models.FloatField()

    def as_dict(self):
        return dict(
            ra_name=self.risk_assessment.name,
            pathogen=self.pathogen,
            infection_risk=self.infection_risk,
            dalys_risk=self.dalys_risk,
            infection_minimum_lrv_min=self.infection_minimum_lrv_min,
            infection_minimum_lrv_max=self.infection_minimum_lrv_max,
            infection_minimum_lrv_q1=self.infection_minimum_lrv_q1,
            infection_minimum_lrv_q3=self.infection_minimum_lrv_q3,
            infection_minimum_lrv_median=self.infection_minimum_lrv_median,
            infection_maximum_lrv_min=self.infection_maximum_lrv_min,
            infection_maximum_lrv_max=self.infection_maximum_lrv_max,
            infection_maximum_lrv_q1=self.infection_maximum_lrv_q1,
            infection_maximum_lrv_q3=self.infection_maximum_lrv_q3,
            infection_maximum_lrv_median=self.infection_maximum_lrv_median,
            dalys_minimum_lrv_min=self.dalys_minimum_lrv_min,
            dalys_minimum_lrv_max=self.dalys_minimum_lrv_max,
            dalys_minimum_lrv_q1=self.dalys_minimum_lrv_q1,
            dalys_minimum_lrv_q3=self.dalys_minimum_lrv_q3,
            dalys_minimum_lrv_median=self.dalys_minimum_lrv_median,
            dalys_maximum_lrv_min=self.dalys_maximum_lrv_min,
            dalys_maximum_lrv_max=self.dalys_maximum_lrv_max,
            dalys_maximum_lrv_q1=self.dalys_maximum_lrv_q1,
            dalys_maximum_lrv_q3=self.dalys_maximum_lrv_q3,
            dalys_maximum_lrv_median=self.dalys_maximum_lrv_median
        )
