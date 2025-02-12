import uuid

from crispy_forms.bootstrap import AppendedText
from django.db import models
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Row, Column, HTML, Submit

from qmra.risk_assessment.forms import _zero_if_none
from qmra.user.models import User


class UserExposure(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exposures")
    name = models.TextField()
    description = models.TextField(blank=True, null=True)
    events_per_year = models.IntegerField()
    volume_per_event = models.FloatField()


class UserExposureForm(forms.ModelForm):
    class Meta:
        model = UserExposure
        fields = [
            "name",
            "description",
            "events_per_year",
            "volume_per_event"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].label = "Exposure name"
        self.fields["description"].label = "Description"
        self.fields['volume_per_event'].widget.attrs['min'] = 0
        self.fields['volume_per_event'].label = "Volume per event in liters"
        self.helper = FormHelper(self)
        self.helper.form_action = "exposure"
        self.helper.form_tag = True
        self.helper.label_class = "text-muted small"
        self.helper.form_id = "user-exposure-form"
        self.helper.layout = Layout(
            Row(Column("name"), Column("description"), css_id="name-and-description"),
            Row(Column("events_per_year"), Column("volume_per_event"), css_id="exposure-form-fieldset"),
            Submit('submit', 'Submit')
        )


class UserSource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name="sources", on_delete=models.CASCADE)
    name = models.TextField(max_length=64)
    rotavirus_min = models.FloatField(blank=True, null=True)
    rotavirus_max = models.FloatField(blank=True, null=True)
    campylobacter_min = models.FloatField(blank=True, null=True)
    campylobacter_max = models.FloatField(blank=True, null=True)
    cryptosporidium_min = models.FloatField(blank=True, null=True)
    cryptosporidium_max = models.FloatField(blank=True, null=True)


class UserSourceForm(forms.ModelForm):
    pathogen1 = forms.ChoiceField(choices=[("", "Rotavirus")])
    pathogen2 = forms.ChoiceField(choices=[("", "Campylobacter jejuni")])
    pathogen3 = forms.ChoiceField(choices=[("", "Cryptosporidium parvum")])

    class Meta:
        model = UserSource
        fields = [
            "name",
            "rotavirus_min",
            "rotavirus_max",
            "campylobacter_min",
            "campylobacter_max",
            "cryptosporidium_min",
            "cryptosporidium_max"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].label = "Source water name"
        self.helper = FormHelper(self)
        self.helper.form_action = "source"
        self.helper.form_tag = True
        self.helper.form_id = "user-source-form"
        self.helper.label_class = "text-muted small"
        self.fields["pathogen1"].disabled = True
        self.fields["pathogen1"].required = False
        self.fields["pathogen1"].label = "Reference Pathogen"
        self.fields["pathogen2"].disabled = True
        self.fields["pathogen2"].required = False
        self.fields["pathogen2"].label = ""
        self.fields["pathogen3"].disabled = True
        self.fields["pathogen3"].required = False
        self.fields["pathogen3"].label = ""
        self.fields['rotavirus_min'].widget.attrs['min'] = 0
        self.fields['rotavirus_max'].widget.attrs['min'] = 0
        self.fields['campylobacter_min'].widget.attrs['min'] = 0
        self.fields['campylobacter_min'].label = ""
        self.fields['campylobacter_max'].widget.attrs['min'] = 0
        self.fields['campylobacter_max'].label = ""
        self.fields['cryptosporidium_min'].widget.attrs['min'] = 0
        self.fields['cryptosporidium_min'].label = ""
        self.fields['cryptosporidium_max'].widget.attrs['min'] = 0
        self.fields['cryptosporidium_max'].label = ""
        self.fields['rotavirus_min'].label = "Minimum concentration"
        self.fields['rotavirus_max'].label = "Maximum concentration"
        self.helper.layout = Layout(
            'name',
            Row(
                Column("pathogen1"),
                Column(AppendedText('rotavirus_min', 'N/L')),
                Column(AppendedText('rotavirus_max', 'N/L'))
            ),
            Row(
                Column("pathogen2"),
                Column(AppendedText('campylobacter_min', 'N/L')),
                Column(AppendedText('campylobacter_max', 'N/L'))
            ),
            Row(
                Column("pathogen3"),
                Column(AppendedText('cryptosporidium_min', 'N/L')),
                Column(AppendedText('cryptosporidium_max', 'N/L'))
            ),
            Submit("Submit", "Submit")

            # "DELETE"
        )


class UserTreatment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name="treatments", on_delete=models.CASCADE)
    name = models.TextField(max_length=64)
    bacteria_min = models.FloatField(blank=True, null=True)
    bacteria_max = models.FloatField(blank=True, null=True)
    viruses_min = models.FloatField(blank=True, null=True)
    viruses_max = models.FloatField(blank=True, null=True)
    protozoa_min = models.FloatField(blank=True, null=True)
    protozoa_max = models.FloatField(blank=True, null=True)


class UserTreatmentForm(forms.ModelForm):
    class Meta:
        model = UserTreatment
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
        self.helper.form_tag = True
        self.helper.form_id = "user-treatment-form"
        self.helper.form_action = "treatment"
        self.helper.label_class = "text-muted small"
        self.fields['name'].label = "treatment name"
        self.fields['bacteria_min'].label = ""
        self.fields['bacteria_max'].label = ""
        self.fields['viruses_min'].label = ""
        self.fields['viruses_max'].label = ""
        self.fields['protozoa_min'].label = ""
        self.fields['protozoa_max'].label = ""
        label_style = "class='text-muted text-center w-100' style='margin-top: .4em;'"
        self.helper.layout = Layout(
            Field("name"),
            Row(Column(HTML(f"<div></div>")),
                Column(HTML(f"<label class='text-muted text-center w-100'>Minimum</label>")),
                Column(HTML(f"<label class='text-muted text-center w-100'>Maximum</label>"))),
            Row(Column(HTML(f"<label {label_style}>Bacteria LRV:</label>")),
                Column("bacteria_min"), Column("bacteria_max")),
            Row(Column(HTML(f"<label {label_style}>Viruses LRV:</label>")),
                Column("viruses_min"), Column("viruses_max")),
            Row(Column(HTML(f"<label {label_style}>Protozoa LRV:</label>")),
                Column("protozoa_min"), Column("protozoa_max")),
            Submit('submit', 'Submit')
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
