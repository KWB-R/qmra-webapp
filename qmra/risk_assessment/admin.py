from django.contrib import admin
from qmra.risk_assessment.qmra_models import QMRASource, QMRAPathogen, QMRAInflow, \
    QMRATreatment, QMRAExposure

"""
- Separate QMRAModels from UserModels (and db)
- models.py must be able to load without an existing db
- db can be bootstrapped with csvs through seed_qmra_db 
- served qmra_db can be downloaded as csv from the admin page
- run export_default and collectstatic every time an entity is saved
    from django.core.management import call_command
    call_command('my_command', 'foo', bar='baz')
"""


class DefaultInflowModelInline(admin.TabularInline):
    model = QMRAInflow
    fields = ["pathogen", "min", "max", "reference"]


@admin.register(QMRASource)
class DefaultSourceModelAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    inlines = [DefaultInflowModelInline]


@admin.register(QMRAExposure)
class DefaultExposureModelAdmin(admin.ModelAdmin):
    list_display = ["name", "events_per_year", "volume_per_event"]
    # inlines = [ReferenceInline]


@admin.register(QMRAPathogen)
class DefaultPathogenModelAdmin(admin.ModelAdmin):
    list_display = ["name", "group"]


@admin.register(QMRATreatment)
class DefaultTreatmentModelAdmin(admin.ModelAdmin):
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
        "bacteria_reference",
        ("viruses_min", "viruses_max"),
        "viruses_reference",
        ("protozoa_min", "protozoa_max"),
        "protozoa_reference"
    ]
