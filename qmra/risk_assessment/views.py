import io
import math

from crispy_forms.utils import render_crispy_form
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.context_processors import csrf
from django.urls import reverse

from qmra.risk_assessment import exports
from qmra.risk_assessment.forms import InflowFormSet, RiskAssessmentForm, TreatmentFormSet, AddTreatmentForm
from qmra.risk_assessment.models import Inflow, RiskAssessment, Treatment
from qmra.risk_assessment.plots import risk_plots
from qmra.risk_assessment.risk import assess_risk
from django.db import transaction

from qmra.risk_assessment.user_models import UserExposureForm, UserTreatmentForm, UserSourceForm, UserExposure, \
    UserSource, UserTreatment
import numpy as np
import pandas as pd


ALLOWED_SOURCE_PATHOGENS = {
    "Rotavirus",
    "Campylobacter jejuni",
    "Cryptosporidium parvum",
}


def _bad_fit_response(message: str, status=422):
    return JsonResponse({"error": message}, status=status)


def _fit_negative_binomial_from_series(series: pd.Series):
    if series.empty:
        raise ValueError("The pathogen column has no values.")

    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.isna().any():
        raise ValueError("All measurements must be integers.")
    if (numeric < 0).any():
        raise ValueError("All measurements must be non-negative integers.")
    if not ((numeric % 1) == 0).all():
        raise ValueError("All measurements must be integers.")

    values = numeric.astype(np.int64).to_numpy()
    if values.size < 5:
        raise ValueError("At least 5 measurements are required to fit a negative binomial distribution.")

    mu = float(values.mean())
    variance = float(values.var(ddof=1))
    if variance <= mu:
        raise ValueError("Negative binomial fit failed because variance must be greater than the mean.")

    r = (mu ** 2) / (variance - mu)
    p = r / (r + mu)

    if r <= 0 or p <= 0 or p >= 1:
        raise ValueError("Negative binomial fit failed due to invalid fitted parameters.")

    simulated = np.random.default_rng(7).negative_binomial(r, p, size=5000)
    q025 = float(np.quantile(simulated, 0.025))
    q975 = float(np.quantile(simulated, 0.975))

    bins = np.arange(simulated.min(), simulated.max() + 2) - 0.5
    hist_counts, hist_edges = np.histogram(simulated, bins=bins)
    centers = ((hist_edges[:-1] + hist_edges[1:]) / 2).astype(int)

    return {
        "n_samples": int(values.size),
        "mu": mu,
        "variance": variance,
        "r": float(r),
        "p": float(p),
        "q025": float(math.floor(q025)),
        "q975": float(math.ceil(q975)),
        "histogram": {
            "x": centers.tolist(),
            "y": hist_counts.tolist(),
        }
    }


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
        treatment.train_index = -1
        treatment.save()
    # save the order of the treatments (:crossed_finger:...)
    for i, treatment in enumerate(risk_assessment.treatments.all()):
        treatment.train_index = i
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


# @login_required(login_url="/login")
def risk_assessment_view(request, risk_assessment_id=None):
    if not request.user.is_authenticated:
        # free trial, no save button
        return render(request, "assessment-configurator.html",
                      context=dict(
                          risk_assessment_form=RiskAssessmentForm(
                              prefix="ra",
                              initial=dict(name=f"Assessment")),
                          inflow_form=InflowFormSet(queryset=Inflow.objects.none(), prefix="inflow"),
                          add_treatment_form=AddTreatmentForm(),
                          treatment_form=TreatmentFormSet(prefix="treatments")
                      ))
    if request.method == "POST":
        if risk_assessment_id is not None:
            instance = RiskAssessment.objects.get(id=risk_assessment_id)
            inflows = instance.inflows.all()
            treatments = instance.treatments.order_by("train_index").all()
        else:
            instance = None
            inflows = Inflow.objects.none()
            treatments = Treatment.objects.none()
        risk_assessment_form = RiskAssessmentForm(request.POST, instance=instance, prefix="ra").set_user(request.user)
        inflow_form = InflowFormSet(request.POST, queryset=inflows, prefix="inflow")
        treatment_form = TreatmentFormSet(request.POST, queryset=treatments, prefix="treatments").set_user(request.user)
        if risk_assessment_form.is_valid() and \
                inflow_form.is_valid() and \
                treatment_form.is_valid():
            ra = create_risk_assessment(request.user, risk_assessment_form, inflow_form, treatment_form)
            for r in ra.results.all():
                r.delete()
            ra = assess_and_save_results(ra)
            if request.GET.get("redirect", False):
                return HttpResponseRedirect(reverse("assessments"))
            return HttpResponseRedirect(reverse("assessment", kwargs=dict(risk_assessment_id=ra.id)))
        else:
            print(inflow_form.errors)
            print(treatment_form.errors)
            return render(request, "assessment-configurator.html",
                          context=dict(
                              risk_assessment=RiskAssessment.objects.get(id=risk_assessment_id) if risk_assessment_id is not None else None,
                              risk_assessment_form=risk_assessment_form.set_user(request.user),
                              inflow_form=inflow_form,
                              add_treatment_form=AddTreatmentForm().set_user(request.user),
                              treatment_form=treatment_form.set_user(request.user),
                              user_exposure_form=UserExposureForm(),
                              user_source_form=UserSourceForm(),
                              user_treatment_form=UserTreatmentForm(),
                              user_exposures=UserExposure.objects.filter(user=request.user).all(),
                              user_sources=UserSource.objects.filter(user=request.user).all(),
                              user_treatments=UserTreatment.objects.filter(user=request.user).all(),
                          ))
    if risk_assessment_id is None:
        return render(request, "assessment-configurator.html",
                      context=dict(
                          risk_assessment_form=RiskAssessmentForm(
                              prefix="ra", initial=dict(name=f"Assessment {len(request.user.risk_assessments.all())+1}")
                          ).set_user(request.user),
                          inflow_form=InflowFormSet(queryset=Inflow.objects.none(), prefix="inflow"),
                          add_treatment_form=AddTreatmentForm().set_user(request.user),
                          treatment_form=TreatmentFormSet(prefix="treatments").set_user(request.user),
                          user_exposure_form=UserExposureForm(),
                          user_source_form=UserSourceForm(),
                          user_treatment_form=UserTreatmentForm(),
                          user_exposures=UserExposure.objects.filter(user=request.user).all(),
                          user_sources=UserSource.objects.filter(user=request.user).all(),
                          user_treatments=UserTreatment.objects.filter(user=request.user).all(),
                      ))
    risk_assessment = RiskAssessment.objects.get(id=risk_assessment_id)
    if request.method == "DELETE":
        risk_assessment.delete()
        return render(request, "risk-assessment-list.html",
                      context=dict(assessments=request.user.risk_assessments.all()))

    return render(request, "assessment-configurator.html",
                  context=dict(
                      risk_assessment=risk_assessment,
                      risk_assessment_form=RiskAssessmentForm(instance=risk_assessment, prefix="ra").set_user(request.user),
                      inflow_form=InflowFormSet(queryset=risk_assessment.inflows.all(), prefix="inflow"),
                      add_treatment_form=AddTreatmentForm().set_user(request.user),
                      treatment_form=TreatmentFormSet(queryset=risk_assessment.treatments.order_by("train_index").all(), prefix="treatments").set_user(request.user),
                      user_exposure_form=UserExposureForm(),
                      user_source_form=UserSourceForm(),
                      user_treatment_form=UserTreatmentForm(),
                      user_exposures=UserExposure.objects.filter(user=request.user).all(),
                      user_sources=UserSource.objects.filter(user=request.user).all(),
                      user_treatments=UserTreatment.objects.filter(user=request.user).all(),
                  ))


# @login_required(login_url="/login")
def risk_assessment_result(request):
    if request.method == "POST":
        risk_assessment_form = RiskAssessmentForm(request.POST, instance=None, prefix="ra")
        inflow_form = InflowFormSet(request.POST, prefix="inflow")
        treatment_form = TreatmentFormSet(request.POST, prefix="treatments")
        if request.user.is_authenticated:
            risk_assessment_form = risk_assessment_form.set_user(request.user)
            treatment_form = treatment_form.set_user(request.user)
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
            plots = risk_plots(results.values())
            return render(request, "assessment-result.html",
                          context=dict(results=results.values(),
                                       infection_risk=risk_category,
                                       risk_plot=plots[0], daly_plot=plots[1],
                                       max_lrv_warning_for={t.name: t.above_max_lrv()
                                                            for t in treatments
                                                            if len(t.above_max_lrv())}))
        else:
            # print(inflow_form.errors)
            # print(treatment_form.errors)
            return HttpResponse(status=422)

    elif request.method == "GET":
        risk_assessment_id = request.GET.get("id")
        if risk_assessment_id is not None:
            risk_assessment = RiskAssessment.objects.get(id=risk_assessment_id)
            if not any(risk_assessment.results.all()):
                risk_assessment = assess_and_save_results(risk_assessment)
            results = risk_assessment.results.all()
            plots = risk_plots(results)
            return render(request, "assessment-result.html",
                          context=dict(results=results,
                                       infection_risk=risk_assessment.infection_risk,
                                       risk_plot=plots[0], daly_plot=plots[1],
                                       max_lrv_warning_for={t.name: t.above_max_lrv()
                                                            for t in risk_assessment.treatments.all()
                                                            if len(t.above_max_lrv())}))


@login_required(login_url="/login")
def export_risk_assessment(request, risk_assessment_id=None):
    if risk_assessment_id is not None:
        risk_assessment = RiskAssessment.objects.get(id=risk_assessment_id)
        if not any(risk_assessment.results.all()):
            risk_assessment = assess_and_save_results(risk_assessment)
        response = HttpResponse(content_type="application/zip")
        response["Content-Disposition"] = (
                "attachment; filename=" + str(risk_assessment.name) + ".zip"
        )
        exports.risk_assessment_as_zip(response, risk_assessment)
        return response
    return HttpResponse(status=422)


@login_required(login_url="/login")
def create_exposure(request):
    if request.method == "POST":
        exposure_form = UserExposureForm(request.POST)
        if exposure_form.is_valid():
            # handle duplicate names
            if any(UserExposure.objects.filter(name=exposure_form.instance.name, user=request.user).all()):
                exposure_form.add_error("name", "'name' must be unique. You already have an exposure with this name")
                ctx = {}
                ctx.update(csrf(request))
                return HttpResponse(render_crispy_form(exposure_form, context=ctx), status=422)
            exposure_form.instance.user = request.user
            exposure_form.save(commit=True)
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        return HttpResponse(status=422)
    return HttpResponse(status=404)


def list_exposures(request):
    if not request.user.is_authenticated:
        return JsonResponse({})
    return JsonResponse({e["name"]: e for e in UserExposure.objects.filter(user=request.user).values().all()})


@login_required(login_url="/login")
def create_source(request):
    if request.method == "POST":
        source_form = UserSourceForm(request.POST)
        if source_form.is_valid():
            # handle duplicate names
            if any(UserExposure.objects.filter(name=source_form.instance.name, user=request.user).all()):
                source_form.add_error("name", "'name' must be unique. You already have a source with this name")
                ctx = {}
                ctx.update(csrf(request))
                return HttpResponse(render_crispy_form(source_form, context=ctx), status=422)
            source_form.instance.user = request.user
            source_form.save(commit=True)
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        return HttpResponse(status=422)
    return HttpResponse(status=404)


def list_sources(request):
    if not request.user.is_authenticated:
        return JsonResponse({})
    return JsonResponse({s["name"]: s for s in UserSource.objects.filter(user=request.user).values().all()})


@login_required(login_url="/login")
def fit_source_pathogen_distribution(request):
    if request.method != "POST":
        return HttpResponse(status=404)

    pathogen = request.POST.get("pathogen")
    if pathogen not in ALLOWED_SOURCE_PATHOGENS:
        return _bad_fit_response("Unsupported pathogen selected.")

    csv_file = request.FILES.get("file")
    if csv_file is None:
        return _bad_fit_response("Please upload a CSV file.")
    if csv_file.size > 5 * 1024 * 1024:
        return _bad_fit_response("Uploaded file is too large. Maximum allowed size is 5 MB.")

    try:
        content = csv_file.read().decode("utf-8")
        df = pd.read_csv(io.StringIO(content))
    except Exception:
        return _bad_fit_response("Could not read the CSV file. Please upload a valid UTF-8 CSV.")

    if pathogen not in df.columns:
        return _bad_fit_response(f"CSV must include a column named '{pathogen}'.")

    try:
        fit = _fit_negative_binomial_from_series(df[pathogen].dropna())
    except ValueError as err:
        return _bad_fit_response(str(err))

    return JsonResponse({
        "pathogen": pathogen,
        **fit,
    })


def list_inflows(request):
    if not request.user.is_authenticated:
        return JsonResponse({})
    return JsonResponse({s["name"]: [
        dict(pathogen_name="Rotavirus", source_name=s["name"],
             min=s["rotavirus_min"], max=s["rotavirus_max"],
             referenceID=None
             ),
        dict(pathogen_name="Campylobacter jejuni", source_name=s["name"],
             min=s["campylobacter_min"], max=s["campylobacter_max"],
             referenceID=None
             ),
        dict(pathogen_name="Cryptosporidium parvum", source_name=s["name"],
             min=s["cryptosporidium_min"], max=s["cryptosporidium_max"],
             referenceID=None
             ),
    ] for s in UserSource.objects.filter(user=request.user).values().all()})


@login_required(login_url="/login")
def create_treatment(request):
    if request.method == "POST":
        treatment_form = UserTreatmentForm(request.POST)
        if treatment_form.is_valid():
            # handle duplicate names
            if any(UserExposure.objects.filter(name=treatment_form.instance.name, user=request.user).all()):
                treatment_form.add_error("name", "'name' must be unique. You already have a treatment with this name")
                ctx = {}
                ctx.update(csrf(request))
                return HttpResponse(render_crispy_form(treatment_form, context=ctx), status=422)
            treatment_form.instance.user = request.user
            treatment_form.save(commit=True)
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        return HttpResponse(status=422)
    return HttpResponse(status=404)


def list_treatments(request):
    if not request.user.is_authenticated:
        return JsonResponse({})
    return JsonResponse({t["name"]: {**t, "treatment_name": t["name"]}
                         for t in UserTreatment.objects.filter(user=request.user).values().all()})
