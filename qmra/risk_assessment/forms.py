from django import forms
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory
from crispy_forms.bootstrap import AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Row, Column, HTML

from qmra.risk_assessment.models import Inflow, DefaultTreatments, Treatment, \
    RiskAssessment, DefaultExposures, DefaultSources
from qmra.user.models import User


def _zero_if_none(x): return x if x is not None else 0


class RiskAssessmentForm(forms.ModelForm):
    source_name = forms.ChoiceField()
    exposure_name = forms.ChoiceField()

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
        self.fields["source_name"].label = "Select a source water type to add pathogen concentrations"
        self.fields["exposure_name"].choices = DefaultExposures.choices()
        self.fields["source_name"].choices = DefaultSources.choices()
        self.fields['events_per_year'].widget.attrs['min'] = 0
        self.fields['volume_per_event'].widget.attrs['min'] = 0
        self.fields['volume_per_event'].label = "Volume per event in liters"
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.label_class = "text-muted small"
        self.helper.layout = Layout(
            Row(Column("name"), Column("description"), css_id="name-and-description"),
            Row(Column("exposure_name"), Column("events_per_year"), Column("volume_per_event"), css_id="exposure-form-fieldset"),
            # Row("source_name", css_id="source-form")
        )

    def set_user(self, user: User):
        self.fields["exposure_name"].choices = [
            ["Your Exposures", [(e.name, e.name) for e in user.exposures.all()]],
            *self.fields["exposure_name"].choices
        ]
        self.fields["source_name"].choices = [
            ["Your Sources", [(s.name, s.name) for s in user.sources.all()]],
            *self.fields["source_name"].choices
        ]
        return self

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
        self.initial.update(kwargs.get("initial", {}))
        self.helper = FormHelper(self)
        self.helper.render_hidden_fields = False
        self.helper.render_unmentioned_fields = False
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.label_class = "text-muted small"
        self.fields['pathogen'].disabled = True
        self.fields['pathogen'].label = "Reference Pathogen"
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
        mn, mx = cleaned_data.get("min", 0), cleaned_data.get("max", 0)
        if mn < 0:
            self.add_error("min", "this field must be positive or 0")
        if mx < 0:
            self.add_error("max", "this field must be positive or 0")
        if mn > mx:
            msg = "minimum concentration must be less than maximum concentration"
            self.add_error("min", msg)
            self.add_error("max", msg)
        return cleaned_data


InflowFormSetBase = modelformset_factory(
    Inflow, form=InflowForm,
    extra=0, max_num=3, min_num=3,
    can_delete=False, can_delete_extra=False
)


class InflowFormSet(InflowFormSetBase):

    def __init__(self, *args, **kwargs):
        kwargs["initial"] = [
                    {"pathogen": "Rotavirus"},
                    {"pathogen": 'Campylobacter jejuni'},
                    {"pathogen": "Cryptosporidium parvum"},
                ]
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        # for form in self.forms:
        #     form.fields["DELETE"].label = "remove"

    def clean(self):
        cleaned_data = [f for f in self.forms if not self._should_delete_form(f)]
        unq_pathogens = {f.cleaned_data["pathogen"] for f in cleaned_data if f.cleaned_data.get("pathogen", False)}
        if len(unq_pathogens) < len(cleaned_data):
            raise ValidationError("each pathogen must be unique")


class TreatmentForm(forms.ModelForm):
    name = forms.ChoiceField()

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
        # self.fields['name'].choices = DefaultTreatments.choices()
        self.fields['name'].label = ""
        self.fields['bacteria_min'].label = ""
        self.fields['bacteria_max'].label = ""
        self.fields['viruses_min'].label = ""
        self.fields['viruses_max'].label = ""
        self.fields['protozoa_min'].label = ""
        self.fields['protozoa_max'].label = ""
        label_style = "class='text-muted text-center w-100' style='margin-top: .4em;'"
        self.helper.layout = Layout(
            Field("name", css_class="disabled-input d-none"),
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
        b_min = _zero_if_none(cleaned_data.get("bacteria_min", 0))
        b_max = _zero_if_none(cleaned_data.get("bacteria_max", 0))
        v_min = _zero_if_none(cleaned_data.get("viruses_min", 0))
        v_max = _zero_if_none(cleaned_data.get("viruses_max", 0))
        p_min = _zero_if_none(cleaned_data.get("protozoa_min", 0))
        p_max = _zero_if_none(cleaned_data.get("protozoa_max", 0))
        msg = "min. must be less than max"
        if b_min > b_max:
            self.add_error("bacteria_min", msg)
        if v_min > v_max:
            self.add_error("viruses_min", msg)
        if p_min > p_max:
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

    def set_user(self, user: User):
        self.fields["select_treatment"].choices = [
            *self.fields["select_treatment"].choices,
            *[(t.name, t.name) for t in user.treatments.all()]
        ]
        return self


class TreatmentFormSet(TreatmentFormSetBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.form.base_fields["name"].choices = DefaultTreatments.choices()
        if not kwargs.get("queryset", False):
            self.queryset = Treatment.objects.none()

    def set_user(self, user: User):
        self.form.base_fields["name"].choices = [
            *self.form.base_fields['name'].choices,
            *[(t.name, t.name) for t in user.treatments.all()]
        ]
        return self