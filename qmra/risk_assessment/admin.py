from django.contrib import admin
from django.core.management import call_command

from qmra.risk_assessment.qmra_models import QMRASource, QMRAPathogen, QMRAInflow, \
    QMRATreatment, QMRAExposure, QMRAReference

"""

"""


def _changeform_view(self, request, object_id, form_url, extra_context):
    # this method of ModelAdmin is wrapped in a transaction and it calls save_model() and save_related()
    # and then returns a response.
    # we extend it to update the static data every time an admin changes a model (and/or its related)
    response = super(type(self), self)._changeform_view(request, object_id, form_url, extra_context)
    call_command("export_default")
    call_command("collectstatic", "--no-input")
    return response


@admin.register(QMRAReference)
class QMRAReferenceAdmin(admin.ModelAdmin):
    list_display = ["name", "link"]
    _changeform_view = _changeform_view


class QMRAInflowInline(admin.TabularInline):
    model = QMRAInflow
    fields = ["pathogen", "min", "max", "reference"]


@admin.register(QMRASource)
class QMRASourceAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    inlines = [QMRAInflowInline]

    _changeform_view = _changeform_view


@admin.register(QMRAExposure)
class QMRAExposureAdmin(admin.ModelAdmin):
    list_display = ["name", "events_per_year", "volume_per_event"]
    # inlines = [ReferenceInline]

    _changeform_view = _changeform_view


@admin.register(QMRAPathogen)
class QMRAPathogenAdmin(admin.ModelAdmin):
    list_display = ["name", "group"]

    _changeform_view = _changeform_view


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

    _changeform_view = _changeform_view
