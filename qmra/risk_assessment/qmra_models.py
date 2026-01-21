import abc
import dataclasses as dtc
import enum
import json
from itertools import groupby
from typing import Optional, Any

import numpy as np
from django.db import models
from django.forms import model_to_dict
from django.utils.functional import classproperty


"""
IMPORTANT NOTE:

qmra has 2 databases:
1. 'default' contains the users' defaults and risk_assessment data
2. 'qmra' contains the KWB's defaults and is managed only by KWB

to bootstrap the 'qmra' db:
```
python manage.py collect_default_static_entities  # create data/default-*.json from the original QMRA data (.csv in raw_public_data/)
python manage.py seed_default_db  # ingest the json into the 'qmra' db
```
additionally, 
```
python manage.py export_default
```
re-create the json **from** the 'qmra' db and is called every time an admin saves something in the admin page

In order to provide the correct choices in server-side rendered forms, this module exposes `StaticEntities` models.
These classes read the .json files (not the 'qmra' db!) and scrape the keys for valid choices.

"""

class ExponentialDistribution:
    def __init__(self, k):
        self.k = k

    def pdf(self, x):
        return 1 - np.exp(-self.k * x)


class BetaPoissonDistribution:
    def __init__(self, alpha, n50):
        self.alpha = alpha
        self.n50 = n50

    def pdf(self, x):
        return 1 - (1 + x * (2 ** (1 / self.alpha) - 1) / self.n50) ** -self.alpha


class StaticEntity(metaclass=abc.ABCMeta):
    _raw_data: Optional[dict[str, dict[str, Any]]] = None

    @property
    @abc.abstractmethod
    def source(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def model(self) -> dtc.dataclass:
        pass

    @property
    @abc.abstractmethod
    def primary_key(self) -> str:
        pass

    @classproperty
    def raw_data(cls) -> dict[str, dict[str, Any]]:
        # because an admin can change this data while the app runs,
        # we need _raw_data to be loaded dynamically...
        with open(cls.source, "r") as f:
            cls._raw_data = json.load(f)
        return cls._raw_data

    @classproperty
    def data(cls) -> dict[str, model]:
        return {k: cls.model.from_dict(r) for k, r in cls.raw_data.items()}

    @classmethod
    @abc.abstractmethod
    def choices(cls):
        pass

    @classmethod
    def get(cls, pk: str):
        return cls.data[pk]


class QMRAReference(models.Model):
    name = models.CharField(blank=False, null=False, max_length=256)
    link = models.URLField(blank=False, null=False, max_length=512)

    @classmethod
    def from_dict(cls, data: dict):
        return QMRAReference(
            pk=data["ReferenceID"],
            name=data["ReferenceName"],
            link=data["ReferenceLink"]
        )

    def to_dict(self):
        return dict(
            ReferenceID=self.pk,
            ReferenceName=self.name,
            ReferenceLink=self.link
        )

    def __str__(self):
        return self.name


class QMRAReferences(StaticEntity):
    source = "qmra/static/data/default-references.json"
    model = QMRAReference
    primary_key = "name"


class PathogenGroup(models.TextChoices):
    Bacteria = "Bacteria"
    Viruses = "Viruses"
    Protozoa = "Protozoa"


class ModelDistributionType(enum.Enum):
    exponential = "exponential"
    beta_poisson = "beta-Poisson"


class QMRASource(models.Model):
    name = models.CharField(blank=False, null=False, max_length=256)
    description = models.CharField(blank=False, null=False, max_length=512)

    @classmethod
    def from_dict(cls, data) -> "QMRASource":
        return QMRASource(
            pk=data["id"], name=data["name"], description=data['description']
        )

    def to_dict(self) -> dict:
        data = model_to_dict(self)
        data["id"] = self.pk
        return data


class QMRASources(StaticEntity):
    source = "qmra/static/data/default-sources.json"
    model = QMRASource
    primary_key = "name"

    @classmethod
    def choices(cls):
        grouped = {grp: list(v) for grp, v in
                   groupby(sorted(cls.data.values(), key=lambda x: x.name), key=lambda x: x.name.split(",")[0])}
        return [
            ("", "---------"),
            *[(k, [(x.name, x.name) for x in v]) for k, v in grouped.items()],
            ("other", "other")
        ]


class QMRAPathogen(models.Model):
    group = models.CharField(choices=PathogenGroup.choices,
                             blank=False, null=False, max_length=256)
    name = models.CharField(blank=False, null=False, max_length=256)
    # fields from "doseResponse.csv"
    best_fit_model = models.CharField(choices=[(m.value, m.value) for m in ModelDistributionType],
                                      blank=False, null=False, max_length=256)
    k = models.FloatField(blank=True, null=True)
    alpha = models.FloatField(blank=True, null=True)
    n50 = models.FloatField(blank=True, null=True)
    # fields from "health.csv"
    infection_to_illness = models.FloatField(blank=True, null=True, default=True)
    dalys_per_case = models.FloatField(blank=True, null=True, default=True)

    @classmethod
    def from_dict(cls, data) -> "QMRAPathogen":
        return QMRAPathogen(
            pk=data["id"],
            group=data["group"],
            name=data["name"],
            best_fit_model=data["best_fit_model"],
            k=data["k"],
            alpha=data["alpha"],
            n50=data["n50"],
            infection_to_illness=data["infection_to_illness"],
            dalys_per_case=data["dalys_per_case"],
        )

    def to_dict(self) -> dict:
        return model_to_dict(self)

    def get_distribution(self):
        if self.best_fit_model == ModelDistributionType.exponential.value:
            return ExponentialDistribution(self.k)
        elif self.best_fit_model == ModelDistributionType.beta_poisson.value:
            return BetaPoissonDistribution(self.alpha, self.n50)
        else:
            raise TypeError(f"Unknown ModelDistributionType: {self.best_fit_model}")

    def __str__(self):
        return self.name


class QMRAPathogens(StaticEntity):
    source = "qmra/static/data/default-pathogens.json"
    model = QMRAPathogen
    primary_key = "name"

    @classmethod
    def choices(cls):
        grouped = {grp: list(v) for grp, v in groupby(cls.data.values(), key=lambda x: x.group)}
        return [
            ("", "---------"),
            *[(grp, [(x.name, x.name) for x in v]) for grp, v in grouped.items()],
        ]


class QMRAInflow(models.Model):
    source = models.ForeignKey(QMRASource, on_delete=models.CASCADE)
    pathogen = models.ForeignKey(QMRAPathogen, on_delete=models.CASCADE)
    min: float = models.FloatField()
    max: float = models.FloatField()
    reference = models.ForeignKey(QMRAReference, blank=True, null=True, on_delete=models.CASCADE)

    @classmethod
    def from_dict(cls, data: dict):
        return QMRAInflow(
            pk=data["id"],
            source=QMRASource.objects.get(name=data["source_name"]),
            pathogen=QMRAPathogen.objects.get(name=data["pathogen_name"]),
            reference_id=data.get("ReferenceID", None),
            min=data["min"],
            max=data["max"]
        )

    def to_dict(self):
        data = model_to_dict(self, exclude={"source", "pathogen"})
        data["source_name"] = self.source.name
        data["pathogen_name"] = self.pathogen.name
        data["ReferenceID"] = str(self.reference.pk) if self.reference is not None else None
        data["id"] = self.pk
        return data


class QMRAInflows(StaticEntity):
    source = "qmra/static/data/default-inflows.json"
    model = QMRAInflow
    primary_key = None

    @classproperty
    def data(cls):
        return {k: [QMRAInflow.from_dict(d) for d in data]
                for k, data in cls.raw_data.items()}

    @classmethod
    def choices(cls):
        return []


class QMRATreatment(models.Model):
    name: str = models.CharField(max_length=256)
    group: str = models.CharField(max_length=256)
    description: str = models.CharField(max_length=512)
    bacteria_min: Optional[float] = models.FloatField(blank=True, null=True)
    bacteria_max: Optional[float] = models.FloatField(blank=True, null=True)
    bacteria_reference = models.ForeignKey(QMRAReference, blank=True, null=True, on_delete=models.CASCADE,
                                           related_name="bacteria_lrv")
    bacteria_references = models.ManyToManyField(QMRAReference, related_name="bacteria_lrvs")

    viruses_min: Optional[float] = models.FloatField(blank=True, null=True)
    viruses_max: Optional[float] = models.FloatField(blank=True, null=True)
    viruses_reference = models.ForeignKey(QMRAReference, blank=True, null=True, on_delete=models.CASCADE,
                                          related_name="viruses_lrv")
    viruses_references = models.ManyToManyField(QMRAReference, related_name="viruses_lrvs")

    protozoa_min: Optional[float] = models.FloatField(blank=True, null=True)
    protozoa_max: Optional[float] = models.FloatField(blank=True, null=True)
    protozoa_reference = models.ForeignKey(QMRAReference, blank=True, null=True, on_delete=models.CASCADE,
                                           related_name="protozoa_lrv")
    protozoa_references = models.ManyToManyField(QMRAReference, related_name="protozoa_lrvs")

    @classmethod
    def from_dict(cls, data):
        return QMRATreatment(
            pk=data["id"],
            name=data['name'],
            group=data['group'],
            description=data['description'],
            bacteria_min=data['bacteria_min'],
            bacteria_max=data['bacteria_max'],
            bacteria_reference_id=int(data["bacteria_reference"]) \
                if data["bacteria_reference"] is not None else None,
            viruses_min=data['viruses_min'],
            viruses_max=data['viruses_max'],
            viruses_reference_id=int(data["viruses_reference"]) \
                if data["viruses_reference"] is not None else None,
            protozoa_min=data['protozoa_min'],
            protozoa_max=data['protozoa_max'],
            protozoa_reference_id=int(data["protozoa_reference"]) \
                if data["protozoa_reference"] is not None else None,
        )

    def to_dict(self):
        data = model_to_dict(self)
        data["bacteria_reference"] = str(self.bacteria_reference.pk) if self.bacteria_reference is not None else None
        data["bacteria_references"] = [ref.pk for ref in self.bacteria_references.all()]
        data["viruses_reference"] = str(self.viruses_reference.pk) if self.viruses_reference is not None else None
        data["viruses_references"] = [ref.pk for ref in self.viruses_references.all()]
        data["protozoa_reference"] = str(self.protozoa_reference.pk) if self.protozoa_reference is not None else None
        data["protozoa_references"] = [ref.pk for ref in self.protozoa_references.all()]
        return data


class QMRATreatments(StaticEntity):
    source = "qmra/static/data/default-treatments.json"
    model = QMRATreatment
    primary_key = "name"

    @classmethod
    def choices(cls):
        return [
            *[(x.name, x.name) for x in sorted(cls.data.values(), key=lambda x: x.name)],
        ]


class QMRAExposure(models.Model):
    name: str = models.CharField(max_length=256)
    description: str = models.CharField(max_length=256)
    events_per_year: int = models.IntegerField()
    volume_per_event: float = models.FloatField()
    reference = models.ForeignKey(QMRAReference, blank=True, null=True, on_delete=models.CASCADE)

    @classmethod
    def from_dict(cls, data):
        return QMRAExposure(
            pk=data["id"],
            name=data["name"],
            description=data["description"],
            events_per_year=data["events_per_year"],
            volume_per_event=data["volume_per_event"],
            reference_id=int(data["ReferenceID"]) if data["ReferenceID"] is not None else None
        )

    def to_dict(self):
        data = model_to_dict(self)
        data["id"] = self.pk
        data["ReferenceID"] = str(self.reference.pk) if self.reference is not None else None
        return data


class QMRAExposures(StaticEntity):
    source = "qmra/static/data/default-exposures.json"
    model = QMRAExposure
    primary_key = "name"

    @classmethod
    def choices(cls):
        grouped = {grp: list(v) for grp, v in
                   groupby(sorted(cls.data.values(), key=lambda x: x.name), key=lambda x: x.name.split(",")[0])}
        return [
            ("", "---------"),
            *[(k, [(x.name, x.name) for x in sorted(v, key=lambda x: x.name)]) for k, v in grouped.items()],
            ("other", "other")
        ]
