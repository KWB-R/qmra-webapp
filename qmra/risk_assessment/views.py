from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from qmra.risk_assessment.forms import InflowFormSet, RiskAssessmentForm, TreatmentFormSet, AddTreatmentForm
from qmra.risk_assessment.models import Inflow, RiskAssessment, Treatment
from qmra.risk_assessment.plots import risk_plots
from qmra.risk_assessment.risk import assess_risk
from django.db import transaction

# - treatments categories
# - calculator layout
# - finish comparison doc
# - inflows and treatments in results
# - refresh / loading
# - consistent icons
# - styling login / registration
# - more tests
# - no crispy...

@transaction.atomic
def create_risk_assessment(user, risk_assessment_form, inflow_form, treatment_form):
    risk_assessment = risk_assessment_form.save(commit=False)
    risk_assessment.user = user
    with_same_name = RiskAssessment.objects.filter(user=user, name=risk_assessment.name).first()
    if with_same_name is not None and risk_assessment.id != with_same_name.id is not None:
        risk_assessment.name = risk_assessment.name + " (2)"
    risk_assessment.save()
    inflows = inflow_form.save(commit=False)
    for deleted in inflow_form.deleted_forms:
        deleted.instance.delete()
    for inflow in inflows:
        inflow.risk_assessment = risk_assessment
        inflow.save()
    treatments = treatment_form.save(commit=False)
    for deleted in treatment_form.deleted_forms:
        deleted.instance.delete()
    for treatment in treatments:
        treatment.risk_assessment = risk_assessment
        treatment.save()
    return risk_assessment


@transaction.atomic
def assess_and_save_results(risk_assessment: RiskAssessment) -> RiskAssessment:
    results = assess_risk(risk_assessment, risk_assessment.inflows.all(),
                          risk_assessment.treatments.all())
    for r in results.values():
        r.save()
    return RiskAssessment.objects.get(id=risk_assessment.id)


@login_required(login_url="/login")
def list_risk_assessment_view(request):
    return render(request, "risk-assessment-list.html",
                  context=dict(assessments=request.user.risk_assessments.order_by("-created_at").all()))


@login_required(login_url="/login")
def risk_assessment_view(request, risk_assessment_id=None):
    if request.method == "POST":
        if risk_assessment_id is not None:
            instance = RiskAssessment.objects.get(id=risk_assessment_id)
            inflows = instance.inflows.all()
            treatments = instance.treatments.all()
        else:
            instance = None
            inflows = Inflow.objects.none()
            treatments = Treatment.objects.none()
        risk_assessment_form = RiskAssessmentForm(request.POST, instance=instance, prefix="ra")
        inflow_form = InflowFormSet(request.POST, queryset=inflows, prefix="inflow")
        treatment_form = TreatmentFormSet(request.POST, queryset=treatments, prefix="treatments")
        if risk_assessment_form.is_valid() and \
                inflow_form.is_valid() and \
                treatment_form.is_valid():
            ra = create_risk_assessment(request.user, risk_assessment_form, inflow_form, treatment_form)
            for r in ra.results.all():
                r.delete()
            ra = assess_and_save_results(ra)
            return HttpResponseRedirect(reverse("assessments"))
        else:
            print(inflow_form.errors)
            print(treatment_form.errors)
            return render(request, "assessment-configurator.html",
                          context=dict(
                              risk_assessment=RiskAssessment.objects.get(id=risk_assessment_id) if risk_assessment_id is not None else None,
                              risk_assessment_form=risk_assessment_form,
                              inflow_form=inflow_form,
                              add_treatment_form=AddTreatmentForm(),
                              treatment_form=treatment_form
                          ))
    if risk_assessment_id is None:
        return render(request, "assessment-configurator.html",
                      context=dict(
                          risk_assessment_form=RiskAssessmentForm(
                              prefix="ra", initial=dict(name=f"Assessment {len(request.user.risk_assessments.all())+1}")),
                          inflow_form=InflowFormSet(queryset=Inflow.objects.none(), prefix="inflow"),
                          add_treatment_form=AddTreatmentForm(),
                          treatment_form=TreatmentFormSet(prefix="treatments")
                      ))
    risk_assessment = RiskAssessment.objects.get(id=risk_assessment_id)
    if request.method == "DELETE":
        risk_assessment.delete()
        return render(request, "risk-assessment-list.html",
                      context=dict(assessments=request.user.risk_assessments.all()))

    return render(request, "assessment-configurator.html",
                  context=dict(
                      risk_assessment=risk_assessment,
                      risk_assessment_form=RiskAssessmentForm(instance=risk_assessment, prefix="ra"),
                      inflow_form=InflowFormSet(queryset=risk_assessment.inflows.all(), prefix="inflow"),
                      add_treatment_form=AddTreatmentForm(),
                      treatment_form=TreatmentFormSet(queryset=risk_assessment.treatments.all(), prefix="treatments")
                  ))


@login_required(login_url="/login")
def risk_assessment_result(request):
    if request.method == "POST":
        risk_assessment_form = RiskAssessmentForm(request.POST, instance=None, prefix="ra")
        inflow_form = InflowFormSet(request.POST, prefix="inflow")
        treatment_form = TreatmentFormSet(request.POST, prefix="treatments")
        if risk_assessment_form.is_valid() and \
                inflow_form.is_valid() and \
                treatment_form.is_valid():
            ra = risk_assessment_form.save(commit=False)
            # print(inflow_form.is_valid(), treatment_form.is_valid())
            inflows = [f.instance for f in inflow_form.forms if f not in inflow_form.deleted_forms]
            treatments = [f.instance for f in treatment_form.forms if f not in treatment_form.deleted_forms]
            results = assess_risk(ra,
                                  inflows,
                                  treatments, save=False)
            risks = {r.infection_risk for r in results.values()}
            risk_category = 'max' if 'max' in risks else ("min" if 'min' in risks else 'none')
            plots = risk_plots(results.values(), risk_category)
            return render(request, "assessment-result.html",
                          context=dict(results=results.values(),
                                       infection_risk=risk_category,
                                       risk_plot=plots[0], daly_plot=plots[1]))
        else:
            print(inflow_form.errors)
            print(treatment_form.errors)
            return HttpResponse(status=422)

    elif request.method == "GET":
        risk_assessment_id = request.GET.get("id")
        if risk_assessment_id is not None:
            risk_assessment = RiskAssessment.objects.get(id=risk_assessment_id)
            if not any(risk_assessment.results.all()):
                risk_assessment = assess_and_save_results(risk_assessment)
            results = risk_assessment.results.all()
            plots = risk_plots(results, risk_assessment.infection_risk)
            return render(request, "assessment-result.html",
                          context=dict(results=results,
                                       infection_risk=risk_assessment.infection_risk,
                                       risk_plot=plots[0], daly_plot=plots[1]))
