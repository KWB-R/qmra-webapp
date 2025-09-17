from django.core.management.base import BaseCommand
from qmra.risk_assessment.qmra_models import QMRAReferences, QMRASources, QMRAPathogens, QMRAInflows, \
    QMRATreatments, QMRAExposures


class Command(BaseCommand):
    help = "Create the default static data of qmra"

    def handle(self, *args, **options):
        for _, ref in QMRAReferences.data.items():
            ref.save()
        for _, pat in QMRAPathogens.data.items():
            pat.save()
        for _, source in QMRASources.data.items():
            source.save()
        for _, inflows in QMRAInflows.data.items():
            for inflow in inflows:
                inflow.save()
        for _, treatment in QMRATreatments.data.items():
            treatment.save()
        for _, exposure in QMRAExposures.data.items():
            exposure.save()


if __name__ == '__main__':
    Command().handle()
