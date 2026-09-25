from typing import Iterable

import numpy as np

from qmra.risk_assessment.models import RiskAssessment, RiskAssessmentResult, Treatment
from qmra.risk_assessment.qmra_models import PathogenGroup, QMRAPathogens


N_SAMPLES = 10_000  # inflow concentration samples per reference pathogen
N_YEARS = 1000  # simulated years
BEST_CASE = "maximum_lrv"  # result fields of best-case, which uses every step's maximum LRV
WORST_CASE = "minimum_lrv"  # result fields of worst-case, which uses every step's minimum LRV
INFECTION_REFERENCE_LEVEL = 10 ** -4  # annual probability of infection
DALYS_REFERENCE_LEVEL = 10 ** -6  # DALYs per person per year


def sample_exposure_events(inflow_min: float, inflow_max: float, events_per_year: int,
                           n_samples: int = N_SAMPLES, n_years: int = N_YEARS):
    """Log10 inflow concentration samples, and for each simulated exposure event the position of the sample it uses.

    Both cases of a scenario use the same samples and events, so they differ only by their LRVs.
    """
    generator = np.random.default_rng(seed=42)
    log_concentrations = generator.normal(
        loc=(np.log10(inflow_min + 10 ** (-8)) + np.log10(inflow_max)) / 2,
        scale=(np.log10(inflow_max) - np.log10(inflow_min + 10 ** (-8))) / 4,
        size=n_samples
    )
    sample_positions = generator.choice(n_samples, size=(n_years, events_per_year), replace=True)
    return log_concentrations, sample_positions


def get_annual_risk(log_concentrations: np.ndarray, sample_positions: np.ndarray, event_lrvs: np.ndarray,
                    volume_per_event: float, distribution) -> np.ndarray:
    """Annual probability of infection of each simulated year; event_lrvs holds the LRV of each exposure event."""
    # the dose-response is evaluated once per distinct LRV and concentration sample, then looked up per event
    lrvs, lrv_positions = np.unique(event_lrvs, return_inverse=True)
    dose = (10 ** (log_concentrations[np.newaxis, :] - lrvs[:, np.newaxis])) * volume_per_event
    event_probs = distribution.pdf(dose)[lrv_positions.reshape(sample_positions.shape), sample_positions]
    return 1 - np.prod(1 - event_probs, axis=1)


def summarize(annual_risks: np.ndarray) -> dict:
    return dict(
        min=annual_risks.min(),
        max=annual_risks.max(),
        q1=np.percentile(annual_risks, 25),
        q3=np.percentile(annual_risks, 75),
        median=np.median(annual_risks),
    )


def reference_level_exceedance(best_case_mean: float, worst_case_mean: float, reference_level: float) -> str:
    """'max' if even best-case exceeds the health-based reference level, 'min' if only worst-case does."""
    return "max" if best_case_mean > reference_level else ("min" if worst_case_mean > reference_level else "none")


def lrv_by_pathogen_group(treatments: Iterable[Treatment]) -> dict:
    lrvs = {
        PathogenGroup.Bacteria: dict(min=0, max=0),
        PathogenGroup.Viruses: dict(min=0, max=0),
        PathogenGroup.Protozoa: dict(min=0, max=0)
    }

    def zero_if_none(x): return x if x is not None else 0

    for t in treatments:
        lrvs[PathogenGroup.Bacteria]["min"] += zero_if_none(t.bacteria_min)
        lrvs[PathogenGroup.Bacteria]["max"] += zero_if_none(t.bacteria_max)
        lrvs[PathogenGroup.Viruses]["min"] += zero_if_none(t.viruses_min)
        lrvs[PathogenGroup.Viruses]["max"] += zero_if_none(t.viruses_max)
        lrvs[PathogenGroup.Protozoa]["min"] += zero_if_none(t.protozoa_min)
        lrvs[PathogenGroup.Protozoa]["max"] += zero_if_none(t.protozoa_max)
    return lrvs


def assess_risk(risk_assessment: RiskAssessment, inflows, treatments, save=True) -> dict[str, RiskAssessmentResult]:
    # assuming the model has been already validated
    lrvs = lrv_by_pathogen_group(treatments)
    results = {}

    for inflow in inflows:
        # unpack params
        pathogen = QMRAPathogens.get(inflow.pathogen)
        group = pathogen.group
        dist = pathogen.get_distribution()

        def to_dalys(pr, pat=pathogen):
            return pr * pat.infection_to_illness * pat.dalys_per_case

        log_concentrations, sample_positions = sample_exposure_events(
            inflow.min, inflow.max, risk_assessment.events_per_year)
        cases = {}
        for case, lrv in [(BEST_CASE, lrvs[group]["max"]), (WORST_CASE, lrvs[group]["min"])]:
            event_lrvs = np.full(sample_positions.shape, lrv, dtype=float)
            cases[case] = get_annual_risk(log_concentrations, sample_positions, event_lrvs,
                                          risk_assessment.volume_per_event, dist)
        stats = {}
        for case, annual_risks in cases.items():
            for stat, value in summarize(annual_risks).items():
                stats[f"infection_{case}_{stat}"] = value
                stats[f"dalys_{case}_{stat}"] = to_dalys(value)
        best_case_mean = cases[BEST_CASE].mean()
        worst_case_mean = cases[WORST_CASE].mean()
        results[inflow.pathogen] = RiskAssessmentResult(
            risk_assessment=risk_assessment,
            infection_risk=reference_level_exceedance(best_case_mean, worst_case_mean, INFECTION_REFERENCE_LEVEL),
            dalys_risk=reference_level_exceedance(to_dalys(best_case_mean), to_dalys(worst_case_mean),
                                                  DALYS_REFERENCE_LEVEL),
            pathogen=inflow.pathogen,
            **stats,
        )
        if save:
            results[inflow.pathogen].save()
    return results
