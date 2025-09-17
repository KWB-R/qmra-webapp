import json
from django.core.management.base import BaseCommand
from qmra.risk_assessment.qmra_models import QMRAReference, QMRAReferences, QMRASource, \
    QMRASources, QMRAPathogen, QMRAPathogens, QMRAInflow, QMRAInflows, QMRATreatment, \
    QMRATreatments, QMRAExposure, QMRAExposures


def save_as_json(data, destination: str):
    with open(destination, "w") as f:
        json.dump(data, f)


class Command(BaseCommand):
    help = "export the default data of qmra to json files for serving them as statics"

    def add_arguments(self, parser):
        parser.add_argument('--format', type=str, help="'json' (default) or 'csv' ", default="json")

    def handle(self, *args, **options):
        save_as_json(
            {src.name: src.to_dict() for src in QMRASource.objects.all()},
            QMRASources.source
        )
        save_as_json(
            {pathogen.name: model_to_dict(pathogen) for pathogen in QMRAPathogen.objects.all()},
            QMRAPathogens.source
        )
        save_as_json(
            {src.name: [inflow.to_dict() for inflow in QMRAInflow.objects.filter(source__name=src.name).all()]
             for src in QMRASource.objects.all()},
            QMRAInflows.source
        )
        save_as_json(
            {t.name: t.to_dict() for t in QMRATreatment.objects.all()},
            QMRATreatments.source
        )
        save_as_json(
            {e.name: e.to_dict() for e in QMRAExposure.objects.all()},
            QMRAExposures.source
        )
        save_as_json(
            {str(ref.pk): ref.to_dict() for ref in QMRAReference.objects.all()},
            QMRAReferences.source
        )


if __name__ == '__main__':
    Command().handle()
