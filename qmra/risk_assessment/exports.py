from zipfile import ZipFile
import base64
from django.db.models import QuerySet
from django.template.loader import render_to_string

from qmra.risk_assessment.models import RiskAssessment, RiskAssessmentResult, Inflow, Treatment
import pandas as pd

from qmra.risk_assessment.plots import risk_plots


def inflows_as_df(inflows: QuerySet[Inflow]):
    dfs = []
    for inflow in inflows.all():
        dfs += [pd.DataFrame({
            "Pathogen": [inflow.pathogen],
            "Minimum Concentration": [inflow.min],
            "Maximum Concentration": [inflow.max],
        })]
    return pd.concat(dfs)


def treatments_as_df(treatments: QuerySet[Treatment]) -> pd.DataFrame:
    dfs = []
    for t in treatments.all():
        dfs += [pd.DataFrame({
            "Treatment": [t.name] * 3,
            "Pathogen group": ["Viruses", "Bacteria", "Protozoa"],
            "Maximum LRV": [t.viruses_max, t.bacteria_max, t.protozoa_max],
            "Minimum LRV": [t.viruses_min, t.bacteria_min, t.protozoa_min]
        })]
    return pd.concat(dfs)


def risk_assessment_result_as_df(pathogen: str, r: RiskAssessmentResult) -> pd.DataFrame:
    return pd.DataFrame({
        ("", "pathogen"): [pathogen] * 2,
        ("", "stat"): ["Maximum LRV", "Minimum LRV"],
        ("Infection prob.", "min"): [
            r.infection_maximum_lrv_min, r.infection_minimum_lrv_min
        ],
        ("Infection prob.", "25%"): [
            r.infection_maximum_lrv_q1, r.infection_minimum_lrv_q1
        ],
        ("Infection prob.", "50%"): [
            r.infection_maximum_lrv_median, r.infection_minimum_lrv_median
        ],
        ("Infection prob.", "75%"): [
            r.infection_maximum_lrv_q3, r.infection_minimum_lrv_q3
        ],
        ("Infection prob.", "max"): [
            r.infection_maximum_lrv_max, r.infection_minimum_lrv_max
        ],
        ("DALYs pppy", "min"): [
            r.dalys_maximum_lrv_min, r.dalys_minimum_lrv_min
        ],
        ("DALYs pppy", "25%"): [
            r.dalys_maximum_lrv_q1, r.dalys_minimum_lrv_q1
        ],
        ("DALYs pppy", "50%"): [
            r.dalys_maximum_lrv_median, r.dalys_minimum_lrv_median
        ],
        ("DALYs pppy", "75%"): [
            r.dalys_maximum_lrv_q3, r.dalys_minimum_lrv_q3
        ],
        ("DALYs pppy", "max"): [
            r.dalys_maximum_lrv_max, r.dalys_minimum_lrv_max
        ],
    })


def results_as_df(results: dict[str, RiskAssessmentResult]) -> pd.DataFrame:
    dfs = []
    for pathogen, r in results.items():
        dfs += [risk_assessment_result_as_df(pathogen, r)]
    return pd.concat(dfs)


def risk_assessment_as_zip(buffer, risk_assessment: RiskAssessment):
    inflows = inflows_as_df(risk_assessment.inflows)
    treatments = treatments_as_df(risk_assessment.treatments)
    results = results_as_df({r.pathogen: r for r in risk_assessment.results.all()})
    plots = risk_plots(risk_assessment.results.all(), "png")
    report = render_to_string("assessment-result-export.html",
                              context=dict(results=risk_assessment.results.all(),
                                           infection_risk=risk_assessment.infection_risk,
                                           risk_plot_data=base64.b64encode(plots[0]).decode("utf-8"),
                                           daly_plot_data=base64.b64encode(plots[1]).decode("utf-8")))
    with ZipFile(buffer, mode="w") as archive:
        archive.mkdir("exposure-assessment")
        archive.mkdir("results-plots")
        archive.writestr("exposure-assessment/inflows.csv", inflows.to_csv(sep=",", decimal=".", index=False))
        archive.writestr("exposure-assessment/treatments.csv", treatments.to_csv(sep=",", decimal=".", index=False))
        archive.writestr(f"{risk_assessment.name}-result.csv", results.to_csv(sep=",", decimal=".", index=False))
        archive.writestr(f"{risk_assessment.name}-report.html", report)
        archive.writestr("results-plots/infection-probability.png", plots[0])
        archive.writestr("results-plots/dalys-pppy.png", plots[1])
