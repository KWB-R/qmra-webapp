from django.contrib import admin
from django.core.management import call_command

from qmra.risk_assessment.qmra_models import QMRASource, QMRAPathogen, QMRAInflow, \
    QMRATreatment, QMRAExposure, QMRAReference

"""

"""


def save_model(self, request, obj, form, change):
    super(type(self), self).save_model(request, obj, form, change)
    call_command("export_default")
    call_command("collectstatic", "--no-input")


@admin.register(QMRAReference)
class QMRAReferenceAdmin(admin.ModelAdmin):
    list_display = ["name", "link"]
    save_model = save_model


class QMRAInflowInline(admin.TabularInline):
    model = QMRAInflow
    fields = ["pathogen", "min", "max", "reference"]


@admin.register(QMRASource)
class QMRASourceAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    inlines = [QMRAInflowInline]

    save_model = save_model


@admin.register(QMRAExposure)
class QMRAExposureAdmin(admin.ModelAdmin):
    list_display = ["name", "events_per_year", "volume_per_event"]
    # inlines = [ReferenceInline]

    save_model = save_model


@admin.register(QMRAPathogen)
class QMRAPathogenAdmin(admin.ModelAdmin):
    list_display = ["name", "group"]

    save_model = save_model


@admin.register(QMRATreatment)
class QMRATreatmentAdmin(admin.ModelAdmin):
    list_display = [
        "name", "group",
        "bacteria_min",
        "bacteria_max",
        "viruses_min",
        "viruses_max",
        "protozoa_min",
        "protozoa_max",
    ]
    fields = [
        ("name", "group"),
        ("bacteria_min", "bacteria_max"),
        "bacteria_references",
        ("viruses_min", "viruses_max"),
        "viruses_references",
        ("protozoa_min", "protozoa_max"),
        "protozoa_references"
    ]
    filter_horizontal = ["bacteria_references", "viruses_references", "protozoa_references"]

    save_model = save_model
