from typing import Iterable

import numpy as np

from qmra.risk_assessment.models import RiskAssessment, RiskAssessmentResult, Treatment
from qmra.risk_assessment.qmra_models import PathogenGroup, QMRAPathogens


N_SAMPLES = 10_000  # inflow concentration samples per reference pathogen
N_YEARS = 1000  # simulated years
BEST_CASE = "maximum_lrv"  # result fields of best-case, which uses every step's maximum LRV
WORST_CASE = "minimum_lrv"  # result fields of worst-case, which uses every step's minimum LRV
MINUTES_PER_DAY = 1440  # failure durations are given in minutes within one day
FAILURE_SEED = 2019  # failure days have their own generator, independent of the concentration samples
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


def draw_failing_events(treatments: list[Treatment], events_per_year: int,
                        n_years: int = N_YEARS) -> list[np.ndarray | None]:
    """For each treatment step, a mask of the simulated exposure events that fall on one of its failure days.

    An event falls on a failure day with probability failure frequency / 365, independently per step (ADR-0001).
    A step without failures gets None and no draws. Each step draws from its own stream, keyed by its position in
    the train, so raising one step's failure frequency only adds failure days and leaves the other steps' as they are.
    """
    failing_events = []
    for position, t in enumerate(treatments):
        if t.failure_frequency > 0:
            draws = np.random.default_rng([FAILURE_SEED, position]).random((n_years, events_per_year))
            failing_events.append(draws < t.failure_frequency / 365)
        else:
            failing_events.append(None)
    return failing_events


def failing_steps(treatments: list[Treatment], failing_events: list[np.ndarray | None], group: PathogenGroup,
                  bound: str) -> list[tuple[np.ndarray, float, int, int]]:
    """The steps that fail on some days and then lose LRV for this pathogen group, as (their failing events, their
    minimum or maximum LRV, failure duration, number of parallel units). A step whose LRV is 0 or below loses nothing
    when it fails (D4)."""
    steps = []
    for t, failing in zip(treatments, failing_events):
        lrv = step_lrv(t, group, bound)
        if failing is not None and lrv > 0:
            steps.append((failing, lrv, t.failure_duration, t.parallel_units))
    return steps


def failure_lrv(lrv: float, parallel_units: int) -> float:
    """LRV of a step while one of its parallel units is down (D7, ADR-0002): that unit's share of the water is not
    treated, the others' is treated with the step's LRV, mixed by concentration. 0 for one unit, at most log10 of the
    number of units."""
    return -np.log10((parallel_units - 1) / parallel_units * 10 ** -lrv + 1 / parallel_units)


def daily_lrv_loss(lrv: float, failure_duration: int, parallel_units: int) -> float:
    """How much LRV a failing step loses on a failure day under the mixed-water assumption (ADR-0002).

    The consumed water mixes water treated during the failure event, with the failure LRV, and water treated in
    normal operation, in proportion to the failure duration. The mixture is averaged by concentration, never by LRV.
    """
    failing_share = failure_duration / MINUTES_PER_DAY
    daily_lrv = -np.log10(failing_share * 10 ** -failure_lrv(lrv, parallel_units)
                          + (1 - failing_share) * 10 ** -lrv)
    return lrv - daily_lrv


def event_lrvs_of_case(train_lrv: float, treatments: list[Treatment], failing_events: list[np.ndarray | None],
                       group: PathogenGroup, bound: str, shape: tuple) -> np.ndarray:
    """LRV of each exposure event in one case: best-case starts from every step's maximum LRV, worst-case from its
    minimum LRV. On a failure day each failing step loses what its daily LRV lacks, so combined failures add up
    without further rules (D6)."""
    event_lrvs = np.full(shape, train_lrv, dtype=float)
    for failing, lrv, failure_duration, parallel_units in failing_steps(treatments, failing_events, group, bound):
        event_lrvs[failing] -= daily_lrv_loss(lrv, failure_duration, parallel_units)
    return event_lrvs


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


def step_lrv(treatment: Treatment, group: PathogenGroup, bound: str) -> float:
    """A step's minimum or maximum LRV for a pathogen group; an empty LRV counts as 0."""
    lrv = getattr(treatment, f"{group.lower()}_{bound}")
    return lrv if lrv is not None else 0


def lrv_by_pathogen_group(treatments: Iterable[Treatment]) -> dict:
    lrvs = {group: dict(min=0, max=0) for group in PathogenGroup}
    for t in treatments:
        for group in PathogenGroup:
            for bound in ["min", "max"]:
                lrvs[group][bound] += step_lrv(t, group, bound)
    return lrvs


def assess_risk(risk_assessment: RiskAssessment, inflows, treatments, save=True) -> dict[str, RiskAssessmentResult]:
    # assuming the model has been already validated
    treatments = list(treatments)
    lrvs = lrv_by_pathogen_group(treatments)
    # the same failure days for both cases and all reference pathogens
    failing_events = draw_failing_events(treatments, risk_assessment.events_per_year)
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
        event_lrvs = {
            BEST_CASE: event_lrvs_of_case(lrvs[group]["max"], treatments, failing_events, group, "max",
                                          sample_positions.shape),
            WORST_CASE: event_lrvs_of_case(lrvs[group]["min"], treatments, failing_events, group, "min",
                                           sample_positions.shape),
        }
        cases = {case: get_annual_risk(log_concentrations, sample_positions, lrvs_of_case,
                                       risk_assessment.volume_per_event, dist)
                 for case, lrvs_of_case in event_lrvs.items()}
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
