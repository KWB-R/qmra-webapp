from django import forms
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory, HiddenInput
from crispy_forms.bootstrap import AppendedText, Modal
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Row, Column, Div, HTML, Button

from qmra.risk_assessment.models import Inflow, DefaultPathogens, DefaultTreatments, Treatment, \
    RiskAssessment


class RiskAssessmentForm(forms.ModelForm):
    class Meta:
        model = RiskAssessment
        fields = [
            "name",
            "description",
            "source_name",
            "exposure_name",
            "events_per_year",
            "volume_per_event"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["source_name"].label = "Select a source type to add inflows"
        self.fields['exposure_name'].widget.attrs['min'] = 0
        self.fields['volume_per_event'].widget.attrs['min'] = 0
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.label_class = "text-muted small"
        self.helper.layout = Layout(
            Row(Column("name"), Column("description")),
            Row(Column("exposure_name"), Column("events_per_year"), Column("volume_per_event"), css_id="exposure-form-fieldset"),
            # Row("source_name", css_id="source-form")
        )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data["events_per_year"] <= 0:
            self.add_error("events_per_year", "this field must be greater than 0")
        if cleaned_data["volume_per_event"] <= 0:
            self.add_error("volume_per_event", "this field must be greater than 0")
        return cleaned_data


class InflowForm(forms.ModelForm):
    # DELETE = forms.BooleanField(label="remove")

    class Meta:
        model = Inflow
        fields = ['pathogen', 'min', 'max']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.render_hidden_fields = False
        self.helper.render_unmentioned_fields = False
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.label_class = "text-muted small"
        self.fields['pathogen'].choices = DefaultPathogens.choices()
        self.fields['pathogen'].label = "Pathogen"
        self.fields['min'].widget.attrs['min'] = 0
        self.fields['max'].widget.attrs['min'] = 0
        self.fields['min'].label = "Minimum concentration"
        self.fields['max'].label = "Maximum concentration"
        self.fields['max'].required = True
        self.helper.layout = Layout(
            'pathogen',
            AppendedText('min', 'N/L'),
            AppendedText('max', 'N/L'),
            # "DELETE"
        )

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data["min"] < 0:
            self.add_error("min", "this field must be positive or 0")
        if cleaned_data["max"] < 0:
            self.add_error("max", "this field must be positive or 0")
        if cleaned_data["min"] >= cleaned_data["max"]:
            msg = "minimum concentration must be less than maximum concentration"
            self.add_error("min", msg)
            self.add_error("max", msg)
        return cleaned_data


InflowFormSetBase = modelformset_factory(
    Inflow, form=InflowForm,
    extra=0, max_num=30, min_num=0,
    can_delete=True, can_delete_extra=True
)


class InflowFormSet(InflowFormSetBase):
    def get_deletion_widget(self):
        return forms.CheckboxInput(attrs=dict(label="remove"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        # for form in self.forms:
        #     form.fields["DELETE"].label = "remove"

    def clean(self):
        cleaned_data = [f for f in self.forms if not self._should_delete_form(f)]
        unq_pathogens = {f.cleaned_data["pathogen"] for f in cleaned_data}
        if len(unq_pathogens) < len(cleaned_data):
            raise ValidationError("each pathogen must be unique")


class TreatmentForm(forms.ModelForm):
    class Meta:
        model = Treatment
        fields = [
            "name",
            "bacteria_min",
            "bacteria_max",
            'viruses_min',
            'viruses_max',
            "protozoa_min",
            "protozoa_max"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.label_class = "text-muted small"
        self.fields['name'].choices = DefaultTreatments.choices()
        self.fields['name'].label = ""
        self.fields['bacteria_min'].label = ""
        self.fields['bacteria_max'].label = ""
        self.fields['viruses_min'].label = ""
        self.fields['viruses_max'].label = ""
        self.fields['protozoa_min'].label = ""
        self.fields['protozoa_max'].label = ""
        self.fields['bacteria_min'].widget.attrs['min'] = 0
        self.fields['bacteria_max'].widget.attrs['min'] = 0
        self.fields['viruses_min'].widget.attrs['min'] = 0
        self.fields['viruses_max'].widget.attrs['min'] = 0
        self.fields['protozoa_min'].widget.attrs['min'] = 0
        self.fields['protozoa_max'].widget.attrs['min'] = 0
        label_style = "class='text-muted text-center w-100' style='margin-top: .4em;'"
        self.helper.layout = Layout(
            Field("name", css_class="disabled-input text-center"),
            Row(Column(HTML(f"<div></div>")),
                Column(HTML(f"<label class='text-muted text-center w-100'>Minimum</label>")),
                Column(HTML(f"<label class='text-muted text-center w-100'>Maximum</label>"))),
            Row(Column(HTML(f"<label {label_style}>Bacteria LRV:</label>")),
                Column("bacteria_min"), Column("bacteria_max")),
            Row(Column(HTML(f"<label {label_style}>Viruses LRV:</label>")),
                Column("viruses_min"), Column("viruses_max")),
            Row(Column(HTML(f"<label {label_style}>Protozoa LRV:</label>")),
                Column("protozoa_min"), Column("protozoa_max")),
            # Row(Column("DELETE"))
        )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data["bacteria_min"] < 0:
            self.add_error("bacteria_min", "this field must be positive or 0")
        if cleaned_data["bacteria_max"] < 0:
            self.add_error("bacteria_max", "this field must be positive or 0")
        if cleaned_data["viruses_min"] < 0:
            self.add_error("viruses_min", "this field must be positive or 0")
        if cleaned_data["viruses_max"] < 0:
            self.add_error("viruses_max", "this field must be positive or 0")
        if cleaned_data["protozoa_min"] < 0:
            self.add_error("protozoa_min", "this field must be positive or 0")
        if cleaned_data["protozoa_max"] < 0:
            self.add_error("protozoa_max", "this field must be positive or 0")
        msg = "min. must be less than max"
        if cleaned_data["bacteria_min"] > cleaned_data["bacteria_max"]:
            self.add_error("bacteria_min", msg)
        if cleaned_data["viruses_min"] > cleaned_data["viruses_max"]:
            self.add_error("viruses_min", msg)
        if cleaned_data["protozoa_min"] > cleaned_data["protozoa_max"]:
            self.add_error("protozoa_min", msg)
        return cleaned_data


TreatmentFormSetBase = modelformset_factory(
    Treatment, form=TreatmentForm,
    extra=0, max_num=30, min_num=0,
    can_delete=True, can_delete_extra=True
)


class AddTreatmentForm(forms.Form):
    select_treatment = forms.ChoiceField(choices=DefaultTreatments.choices(), widget=forms.Select())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["select_treatment"].required = False
        self.fields["select_treatment"].label = "Select treatment to add"
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.label_class = "text-muted"
        self.helper.layout = Layout(
            "select_treatment",
        )


class TreatmentFormSet(TreatmentFormSetBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        if not kwargs.get("queryset", False):
            self.queryset = Treatment.objects.none()
