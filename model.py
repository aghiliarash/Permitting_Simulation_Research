"""Semi-Markov permitting model and declared simulation experiments."""

import csv
import json
import math
import os
from typing import Dict, Any, List
import numpy as np
SEED = 20261021
OBSERVED_BPI2015_MUNICIPALITIES = {'M1': {'doi': '10.4121/uuid:a0addfda-2044-4541-a450-fdcc9fe16d17', 'cases': 1199, 'events': 52217, 'event_classes': 398, 'mean_events_per_case': 43.55, 'cross_replay_fitness': [0.972, 0.918, 0.974, 0.948, 0.945], 'organizational_profile': '3 specialized role clusters (admin, regular DM, environmental DM); phase-transfer registration lags'}, 'M2': {'doi': '10.4121/uuid:63a8435a-077d-4ece-97cd-2c76d394d99c', 'cases': 832, 'events': 44354, 'event_classes': 410, 'mean_events_per_case': 53.31, 'cross_replay_fitness': [0.843, 0.97, 0.864, 0.847, 0.857], 'organizational_profile': 'Generalist roles with high self-loops; extended-case & objection delays; shared staff (560530, 560532) with M5'}, 'M3': {'doi': '10.4121/uuid:ed445cdd-27d5-4d77-a1f7-59fe7360cfbe', 'cases': 1409, 'events': 59681, 'event_classes': 383, 'mean_events_per_case': 42.36, 'cross_replay_fitness': [0.933, 0.9, 0.936, 0.944, 0.905], 'organizational_profile': 'Single generalist cluster with frequent inter-resource handoffs; intake confirmation delays'}, 'M4': {'doi': '10.4121/uuid:679b11cf-47cd-459e-a6de-9ca614e25985', 'cases': 1053, 'events': 47293, 'event_classes': 356, 'mean_events_per_case': 44.91, 'cross_replay_fitness': [0.967, 0.931, 0.972, 0.979, 0.944], 'organizational_profile': 'Strong April/June closure peaks; sign-off bottleneck at resource 560752 in decision irrevocable stage'}, 'M5': {'doi': '10.4121/uuid:b32c6fe5-f212-4286-9774-58dd53511cf8', 'cases': 1156, 'events': 59083, 'event_classes': 398, 'mean_events_per_case': 51.11, 'cross_replay_fitness': [0.916, 0.919, 0.923, 0.909, 0.933], 'organizational_profile': 'High completeness-subcase frequency; hub concentration at resources 560600 and 560602'}}
PHASE_HOURS = {'application_received': 88.536, 'asked_additional_info': 759.022, 'additional_info_received': 255.366, 'application_receptive': 536.76, 'advice_known': 26.873, 'concept_draft_decision_ready': 753.279, 'concept_decision_ready': 64.952, 'draft_decision_ready': 47.889, 'draft_decision_made': 4.0, 'decision_ready': 105.43, 'decision_taken': 53.156, 'decision_sent': 62.512, 'decision_irrevocable': 982.356, 'end_phase': 68.548, 'prematurely_terminated': 684.699, 'permanently_suspended': 871.624}
PHASE_DAYS = {k: v / 24.0 for k, v in PHASE_HOURS.items()}

def build_parameters_and_assumptions() -> Dict[str, Any]:
    """Build the complete, machine-readable parameter and assumption file."""
    return {'metadata': {'study_title': 'Administrative Coordination and Permitting Delays: An Open-Data-Informed Simulation Study', 'version_date': '2026-10-21', 'random_seed': SEED, 'primary_evidence_source': 'BPI Challenge 2015 (Five Dutch Municipalities, 4TU.ResearchData DOI: 10.4121/uuid:31a308ef-c844-48da-948c-305d167a0ec1)', 'diagnostic_reference': 'Teinemaa, Leontjeva, & Masing (2015), BPIC 2015: Diagnostics of Building Permit Application Process in Dutch Municipalities'}, 'layer_A_observed_evidence': {'collection_totals': {'municipalities': 5, 'total_applications': 5649, 'total_events': 262628, 'unique_activity_codes': 495, 'unique_english_activity_names': 356, 'core_2013_2014_phase_subsample_cases': 1351, 'core_frequent_variants_count': 18, 'observed_inter_arrival_mean_hours': 13.0, 'observed_administrators_count': 15, 'observed_decision_makers_count': 31, 'timestamp_identifiability_note': 'Teinemaa et al. (2015, Sec. 2, pp. 3-6) audited eight timestamp attributes and identified extensive missingness in five attributes (dueDate, dateStop, planned, endDatePlanned, and endDate), measuring elapsed intervals using sequential time:timestamp values with three-digit action codes (01_HOOFD_xxx) used to order events within tied timestamp batches. Subtracting time:timestamp from dateFinished also produced negative differences whose recording conventions could not be clarified with the process owner.', 'provenance': 'Directly observed in published source (van Dongen 2015; Teinemaa et al. 2015, Sec. 2 & Sec. 6)'}, 'municipalities': OBSERVED_BPI2015_MUNICIPALITIES, 'phase_holding_durations_hours': PHASE_HOURS, 'phase_holding_durations_days': {k: round(v, 4) for k, v in PHASE_DAYS.items()}, 'contextual_bimp_reference': {'baseline_duration_units': 6249.6, 'rework_eliminated_duration_units': 4720.8, 'relative_duration_reduction_pct': 24.46, 'simulations_per_scenario': 3, 'cases_per_simulation': 2000, 'provenance': 'Published stochastic what-if BIMP simulation in Teinemaa et al. (2015, Sec. 6, Table 5, p. 21), which estimated branching probabilities, fitted exponential phase-duration distributions, and ran three simulations of 2,000 cases for each scenario (modifying both clarification phases and premature termination steps). Used as a contextual comparison, not as an independent validation test or calibration target.'}}, 'layer_B_simulation_assumptions': {'distributional_and_uncertainty_assumptions': {'phase_holding_time_distributions': 'Gamma distributions parameterized to preserve exact published Layer A phase means with assumed baseline shape parameters: S1 k=1.0 (exponential fit in Teinemaa et al. 2015 Fig. 16), S2 loop k=2.0, S3 receptive k=1.5, S3 advice k=1.2, S4 concept/draft/decision_ready k=1.5 (draft_made k=1.0), S5 taken/sent k=1.5, S6 irrevocable k=3.0 (end k=1.5)', 'replicate_percentile_range_definition': '95% Replicate-Percentile Range [Rep PR] (2.5th to 97.5th percentile across 30 Monte Carlo replications of N=2,000 cases under fixed baseline parameters), describing finite-batch simulation variability alongside batch-mean standard error SE_batch', 'assumed_input_variation_interval_definition': '95% Assumed-Input Variation Interval {Input VI} across 100 parameter vectors theta_j applying an assumed 12% coefficient of variation (Gamma scaling) to all phase holding-time means, Normal(0.28, 0.03) clipped to [0.18, 0.40] for baseline rework probability, and Normal(3.2, 0.40) clipped to [2.0, 4.5] days for handoff delay', 'matched_input_contrast_design': 'Within each configuration, B0_baseline, I1_routing_continuity, I2_rework_prevention, and I3_targeted_intake are evaluated across the exact same 100 parameter vectors theta_j (rng_theta = default_rng(cfg_seed + 100000)) and matched trajectory seeds (rng_traj = default_rng(cfg_seed + 200000 + j) and rng_mc = default_rng(cfg_seed + r)), isolating Delta_j = g(I, theta_j) - g(B0, theta_j)', 'provenance': 'Scenario assumption (distributional shapes and 12% input-perturbation bands are modeling assumptions, not empirically estimated sampling distributions)'}, 'complexity_index': {'distribution': 'Beta(2.0, 2.0)', 'low_band': [0.0, 0.35], 'intermediate_band': [0.35, 0.7], 'high_band': [0.7, 1.0], 'provenance': 'Scenario assumption (normalized operational complexity proxy for required subcases and advice steps)'}, 'branching_handoff_and_rework_specification': {'first_loop_rework_probability_formula': 'p_rework_1(C_i) = clip(rework_prob_base + 0.20 * (C_i - 0.50), 0.05, 0.65) when rework is active; 0.0 when disable_rework=True', 'second_loop_conditional_prob_formula': 'p_rework_2_given_1(C_i) = 0.15 * (p_rework_1_eff(C_i) / 0.28), scaling proportionally with effective first-loop rework probability', 'second_loop_duration_scaling': 0.85, 'extended_draft_branch_prob_formula': '0.10 + 0.55 * C_i (mean = 0.375 over Beta(2,2))', 'advice_step_condition': '1 advice step if C_i >= 0.35; 50% weight additional advice step if C_i > 0.70', 'expected_handoffs_formula': 'H_i ~ Poisson(max(0.1, (1.5 + 3.2 * C_i) * handoff_mult + 1.2 * n_rework_loops))', 'case_level_handoff_delay_draw': 'Each case i draws a shared case-level per-handoff delay factor d_i ~ Gamma(2.0, eta / 2.0) multiplying its realized handoff count H_i (T_coord,i = H_i * d_i)', 'provenance': 'Scenario assumption'}, 'competing_coordination_configurations': {'C0_no_friction': {'demand_multiplier_rho': 1.0, 'handoff_delay_eta_days': 0.0, 'description': 'Reference holding times without additional coordination penalties (published BPI 2015 phase holding durations with zero added handoff penalty)'}, 'C1_linear_handoff': {'demand_multiplier_rho': 1.0, 'handoff_delay_eta_days': 3.2, 'description': "Linear handoff friction where each case's Poisson handoff count H_i is multiplied by a case-level draw d_i ~ Gamma(2, 1.6) days (mean 3.2 d)"}, 'C2_threshold_governance': {'demand_multiplier_rho': 1.0, 'low_tier_handoff_delay_days': 0.8, 'base_handoff_delay_days': 1.6, 'mid_tier_extra_handoffs_mean': 3.5, 'mid_tier_referral_delay_days': 6.8, 'high_tier_coordination_factor_gamma': 0.78, 'description': 'Threshold referral regime where intermediate cases (0.35 <= C_i <= 0.70) incur extra specialist referrals while high-tier cases (C_i > 0.70) receive senior case-team coordination scaling S3 and S4 by gamma_high'}, 'C3_congestion_rework': {'demand_multiplier_rho': 1.25, 'handoff_delay_eta_days': 3.2, 'imposed_congestion_multiplier_formula': '1.0 + 0.65 * (rho - 1.0) * (1.0 + 0.90 * mean_p_rework_eff), plus 1.12x scaling on S2 rework holding time and 1.10x scaling on handoff delay', 'description': 'Imposed workload-and-rework congestion scenario increasing upper-tail delay relative to the reference comparison via a parametric multiplier (not an empirical estimate of a real 25% arrival increase or an endogenous continuous-time queueing model)'}}, 'core_management_interventions': {'B0_baseline': {'description': 'Unmodified baseline permitting workflow', 'handoff_reduction_fraction': 0.0, 'rework_prob_reduction_fraction': 0.0, 'rework_duration_reduction_fraction': 0.0, 'hypothetical_relative_cost_units': 0.0}, 'I1_routing_continuity': {'description': 'Case-ownership continuity reducing inter-resource handoffs by 60%', 'handoff_reduction_fraction': 0.6, 'rework_prob_reduction_fraction': 0.0, 'rework_duration_reduction_fraction': 0.0, 'hypothetical_relative_cost_units': 1.0}, 'I2_rework_prevention': {'description': 'Pre-submission digital completeness check reducing clarification rework probability by 50% and rework holding time by 15%', 'handoff_reduction_fraction': 0.0, 'rework_prob_reduction_fraction': 0.5, 'rework_duration_reduction_fraction': 0.15, 'hypothetical_relative_cost_units': 1.7}, 'I3_targeted_intake': {'description': 'Targeted early intake review for upper-complexity cases (C_i > 0.55, ~42.4% of applications at baseline) reducing their rework probability by 45%, rework duration by 25%, and handoffs by 50%', 'handoff_reduction_fraction_targeted': 0.5, 'rework_prob_reduction_fraction_targeted': 0.45, 'rework_duration_reduction_fraction_targeted': 0.25, 'complexity_threshold': 0.55, 'targeting_accuracy_baseline': 1.0, 'hypothetical_relative_cost_units': 1.3}}}}

def simulate_permitting_cohort(n_cases: int, config: str, intervention: str, rng: np.random.Generator, phase_scale_factors: Dict[str, float]=None, rework_prob_base: float=0.28, handoff_delay_base: float=3.2, c2_mid_extra_handoffs: float=3.5, c2_high_coord_factor: float=0.78, intervention_eff_scale: float=1.0, i3_random_targeting_error: float=0.0, gamma_shape_multiplier: float=1.0, disable_rework: bool=False, pure_feedforward_test3a: bool=False, zero_rework_mixture_test3b: bool=False) -> Dict[str, Any]:
    """

    Simulate n_cases building-permit applications through the 6-state Wabo

    semi-Markov process.

    """
    if phase_scale_factors is None:
        phase_scale_factors = {k: 1.0 for k in PHASE_DAYS}
    p_days = {k: PHASE_DAYS[k] * phase_scale_factors.get(k, 1.0) for k in PHASE_DAYS}
    C = rng.beta(2.0, 2.0, size=n_cases)
    low_mask = C < 0.35
    mid_mask = (C >= 0.35) & (C <= 0.7)
    high_mask = C > 0.7
    true_target_mask = C > 0.55
    rho = 1.25 if config == 'C3_congestion_rework' else 1.0
    base_handoffs = 1.5 + 3.2 * C
    if disable_rework or pure_feedforward_test3a or zero_rework_mixture_test3b:
        p_rework_i = np.zeros(n_cases)
    else:
        p_rework_i = np.clip(rework_prob_base + 0.2 * (C - 0.5), 0.05, 0.65)
    rework_time_mult = np.ones(n_cases)
    handoff_mult = np.ones(n_cases)
    triaged = np.zeros(n_cases, dtype=bool)
    eff = intervention_eff_scale
    if intervention == 'I1_routing_continuity':
        handoff_mult *= max(0.0, 1.0 - 0.6 * eff)
    elif intervention == 'I2_rework_prevention':
        p_rework_i *= max(0.0, 1.0 - 0.5 * eff)
        rework_time_mult *= max(0.2, 1.0 - 0.15 * eff)
    elif intervention == 'I3_targeted_intake':
        if i3_random_targeting_error > 0.0:
            noise = rng.normal(0.0, i3_random_targeting_error, size=n_cases)
            triaged = C + noise > 0.55
        else:
            triaged = C > 0.55
        p_rework_i = np.where(triaged, p_rework_i * max(0.0, 1.0 - 0.45 * eff), p_rework_i)
        rework_time_mult = np.where(triaged, max(0.2, 1.0 - 0.25 * eff), 1.0)
        handoff_mult = np.where(triaged, max(0.0, 1.0 - 0.5 * eff), 1.0)
    mean_p_rework = float(np.mean(p_rework_i))
    if config == 'C3_congestion_rework':
        congestion_mult = 1.0 + 0.65 * (rho - 1.0) * (1.0 + 0.9 * mean_p_rework)
    else:
        congestion_mult = 1.0

    def draw_gamma(mean_val: float, base_shape: float, size: int) -> np.ndarray:
        k = max(0.5, base_shape * gamma_shape_multiplier)
        scale = mean_val / k
        return rng.gamma(shape=k, scale=scale, size=size)
    t_S1 = draw_gamma(p_days['application_received'], 1.0, n_cases)
    has_rework_1 = rng.random(n_cases) < p_rework_i
    has_rework_2 = has_rework_1 & (rng.random(n_cases) < 0.15 * (p_rework_i / 0.28))
    n_rework_loops = has_rework_1.astype(int) + has_rework_2.astype(int)
    rework_cycle_mean = p_days['asked_additional_info'] + p_days['additional_info_received']
    t_rework_raw = draw_gamma(rework_cycle_mean, 2.0, n_cases) * has_rework_1 + draw_gamma(rework_cycle_mean * 0.85, 2.0, n_cases) * has_rework_2
    t_S2 = t_rework_raw * rework_time_mult * (1.12 if config == 'C3_congestion_rework' else 1.0)
    t_receptive = draw_gamma(p_days['application_receptive'], 1.5, n_cases)
    if pure_feedforward_test3a:
        needs_advice = np.ones(n_cases, dtype=bool)
        extra_advice = np.zeros(n_cases, dtype=bool)
    else:
        needs_advice = C >= 0.35
        extra_advice = C > 0.7
    t_advice = draw_gamma(p_days['advice_known'], 1.2, n_cases) * needs_advice + draw_gamma(p_days['advice_known'], 1.2, n_cases) * extra_advice * 0.5
    t_S3 = (t_receptive + t_advice) * congestion_mult
    if pure_feedforward_test3a:
        is_extended = np.zeros(n_cases, dtype=bool)
    else:
        prob_extended = np.clip(0.1 + 0.55 * C, 0.05, 0.75)
        is_extended = rng.random(n_cases) < prob_extended
    t_concept_ext = draw_gamma(p_days['concept_draft_decision_ready'], 1.5, n_cases)
    t_concept_std = draw_gamma(p_days['concept_decision_ready'], 1.5, n_cases)
    t_concept = np.where(is_extended, t_concept_ext, t_concept_std)
    t_draft_ready = draw_gamma(p_days['draft_decision_ready'], 1.5, n_cases)
    t_draft_made = draw_gamma(p_days['draft_decision_made'], 1.0, n_cases)
    t_dec_ready = draw_gamma(p_days['decision_ready'], 1.5, n_cases)
    t_S4 = (t_concept + t_draft_ready + t_draft_made + t_dec_ready) * congestion_mult
    expected_handoffs = base_handoffs * handoff_mult + 1.2 * n_rework_loops
    realized_handoffs = rng.poisson(np.maximum(0.1, expected_handoffs))
    if config == 'C0_no_friction' or pure_feedforward_test3a or zero_rework_mixture_test3b:
        t_coord = np.zeros(n_cases)
    elif config in ('C1_linear_handoff', 'C3_congestion_rework'):
        per_handoff = draw_gamma(handoff_delay_base, 2.0, n_cases)
        t_coord = realized_handoffs * per_handoff * (1.1 if config == 'C3_congestion_rework' else 1.0)
    elif config == 'C2_threshold_governance':
        base_h_delay = realized_handoffs * draw_gamma(1.6, 2.0, n_cases)
        extra_mid_referrals = rng.poisson(np.maximum(0.0, c2_mid_extra_handoffs * handoff_mult), size=n_cases)
        referral_penalty_mid = extra_mid_referrals * draw_gamma(6.8, 2.0, n_cases)
        t_coord_low = realized_handoffs * draw_gamma(0.8, 2.0, n_cases)
        t_coord_mid = base_h_delay + referral_penalty_mid
        t_coord_high = base_h_delay
        t_coord = np.select([low_mask, mid_mask, high_mask], [t_coord_low, t_coord_mid, t_coord_high])
        t_S3 = np.where(high_mask, t_S3 * c2_high_coord_factor, t_S3)
        t_S4 = np.where(high_mask, t_S4 * c2_high_coord_factor, t_S4)
    else:
        raise ValueError(f'Unknown configuration: {config}')
    t_S5 = draw_gamma(p_days['decision_taken'], 1.5, n_cases) + draw_gamma(p_days['decision_sent'], 1.5, n_cases)
    T_dec = t_S1 + t_S2 + t_S3 + t_S4 + t_coord + t_S5
    t_S6 = draw_gamma(p_days['decision_irrevocable'], 3.0, n_cases) + draw_gamma(p_days['end_phase'], 1.5, n_cases)
    T_irrev = T_dec + t_S6

    def compute_metrics(arr: np.ndarray) -> Dict[str, float]:
        return {'mean': float(np.mean(arr)), 'median': float(np.median(arr)), 'iqr_25': float(np.percentile(arr, 25)), 'iqr_75': float(np.percentile(arr, 75)), 'p90': float(np.percentile(arr, 90)), 'P_56': float(np.mean(arr <= 56.0) * 100.0), 'P_90': float(np.mean(arr <= 90.0) * 100.0), 'P_180': float(np.mean(arr <= 180.0) * 100.0), 'R_90': float(np.mean(np.minimum(arr, 90.0))), 'R_180': float(np.mean(np.minimum(arr, 180.0)))}
    overall = compute_metrics(T_dec)
    overall['T_irrev_median'] = float(np.median(T_irrev))
    overall['T_irrev_p90'] = float(np.percentile(T_irrev, 90))
    overall['rework_rate_pct'] = float(np.mean(has_rework_1) * 100.0)
    overall['second_rework_rate_pct'] = float(np.mean(has_rework_2) * 100.0)
    overall['mean_handoffs'] = float(np.mean(realized_handoffs))
    if intervention == 'I3_targeted_intake':
        overall['triaged_share_pct'] = float(np.mean(triaged) * 100.0)
        overall['true_positive_coverage_pct'] = float(np.mean(triaged[true_target_mask]) * 100.0)
        overall['false_positive_rate_pct'] = float(np.mean(triaged[~true_target_mask]) * 100.0)
    by_tier = {'Low': compute_metrics(T_dec[low_mask]), 'Intermediate': compute_metrics(T_dec[mid_mask]), 'High': compute_metrics(T_dec[high_mask])}
    return {'overall': overall, 'by_tier': by_tier, 'raw_T_dec': T_dec, 'raw_T_irrev': T_irrev, 'raw_t_S1': t_S1, 'raw_has_rework_1': has_rework_1, 'raw_has_rework_2': has_rework_2}

def run_scenario_with_uncertainty(config: str, intervention: str, n_mc_reps: int=30, n_cases: int=2000, n_param_draws: int=100, base_seed: int=SEED) -> Dict[str, Any]:
    """

    Evaluate both finite-batch simulation variability across 30 replications

    (95% Replicate-Percentile Range [Rep PR] and batch-mean SE) and assumed

    input-parameter variation across 100 parameter vectors theta_j (95%

    Assumed-Input Variation Interval {Input VI} under 12% CV on phase means).

    When a common base_seed is supplied across B0, I1, I2, and I3 within a

    configuration, every intervention receives the exact same 100 parameter

    vectors theta_j and matched trajectory seeds.

    """
    mc_records = []
    tier_records = {'Low': [], 'Intermediate': [], 'High': []}
    for r in range(n_mc_reps):
        rng_mc = np.random.default_rng(base_seed + r)
        res = simulate_permitting_cohort(n_cases=n_cases, config=config, intervention=intervention, rng=rng_mc)
        mc_records.append(res['overall'])
        for t in ('Low', 'Intermediate', 'High'):
            tier_records[t].append(res['by_tier'][t])
    rng_theta = np.random.default_rng(base_seed + 100000)
    param_records = []
    theta_records = []
    for j in range(n_param_draws):
        scale_factors = {k: float(rng_theta.gamma(shape=1.0 / 0.12 ** 2, scale=0.12 ** 2)) for k in PHASE_DAYS}
        rework_draw = float(np.clip(rng_theta.normal(0.28, 0.03), 0.18, 0.4))
        handoff_draw = float(np.clip(rng_theta.normal(3.2, 0.4), 2.0, 4.5))
        theta_records.append({'phase_scale_factors': scale_factors.copy(), 'intake_duration_scale': float(scale_factors['application_received']), 'rework_prob_base': rework_draw, 'handoff_delay_base': handoff_draw})
        rng_traj = np.random.default_rng(base_seed + 200000 + j)
        res_p = simulate_permitting_cohort(n_cases=1500, config=config, intervention=intervention, rng=rng_traj, phase_scale_factors=scale_factors, rework_prob_base=rework_draw, handoff_delay_base=handoff_draw)
        param_records.append(res_p['overall'])
    summary = {}
    for k in mc_records[0].keys():
        mc_vals = np.array([r[k] for r in mc_records])
        p_vals = np.array([r[k] for r in param_records])
        summary[k] = {'estimate': round(float(np.mean(mc_vals)), 2), 'se_batch': round(float(np.std(mc_vals, ddof=1) / math.sqrt(n_mc_reps)), 2), 'mc_ci_95': [round(float(np.percentile(mc_vals, 2.5)), 2), round(float(np.percentile(mc_vals, 97.5)), 2)], 'param_ui_95': [round(float(np.percentile(p_vals, 2.5)), 2), round(float(np.percentile(p_vals, 97.5)), 2)]}
    tier_summary = {}
    for t in ('Low', 'Intermediate', 'High'):
        tier_summary[t] = {}
        for k in ('median', 'p90', 'P_56', 'P_180', 'R_90', 'R_180'):
            vals = np.array([r[k] for r in tier_records[t]])
            tier_summary[t][k] = round(float(np.mean(vals)), 2)
    return {'overall': summary, 'by_tier': tier_summary, '_mc_records': mc_records, '_param_records': param_records, '_theta_records': theta_records}

def compute_paired_contrasts(intv_raw: Dict[str, Any], b0_raw: Dict[str, Any]) -> Dict[str, Any]:
    """Compute matched-scenario differences Delta_j = g(I, theta_j) - g(B0, theta_j)."""
    contrasts = {}
    for k in ('median', 'p90', 'P_56', 'P_180', 'R_90', 'R_180'):
        mc_diff = np.array([r[k] for r in intv_raw['_mc_records']]) - np.array([r[k] for r in b0_raw['_mc_records']])
        p_diff = np.array([r[k] for r in intv_raw['_param_records']]) - np.array([r[k] for r in b0_raw['_param_records']])
        contrasts[f'delta_{k}'] = {'estimate': round(float(np.mean(mc_diff)), 2), 'se_batch': round(float(np.std(mc_diff, ddof=1) / math.sqrt(len(mc_diff))), 2), 'rep_pr_95': [round(float(np.percentile(mc_diff, 2.5)), 2), round(float(np.percentile(mc_diff, 97.5)), 2)], 'input_vi_95': [round(float(np.percentile(p_diff, 2.5)), 2), round(float(np.percentile(p_diff, 97.5)), 2)]}
    return contrasts

def run_verification_and_sensitivity_suite() -> Dict[str, Any]:
    """Execute verification tests (Tests 1-5) and sensitivity analyses."""
    rng = np.random.default_rng(SEED)
    res_check = simulate_permitting_cohort(60000, 'C1_linear_handoff', 'B0_baseline', rng)
    test1_positivity = bool(np.all(res_check['raw_T_dec'] > 0) and np.all(res_check['raw_t_S1'] > 0))
    test2_ordering = bool(np.all(res_check['raw_T_irrev'] > res_check['raw_T_dec']) and np.all(res_check['raw_T_dec'] > res_check['raw_t_S1']))
    analytical_mean_test3a = PHASE_DAYS['application_received'] + PHASE_DAYS['application_receptive'] + PHASE_DAYS['advice_known'] + PHASE_DAYS['concept_decision_ready'] + PHASE_DAYS['draft_decision_ready'] + PHASE_DAYS['draft_decision_made'] + PHASE_DAYS['decision_ready'] + PHASE_DAYS['decision_taken'] + PHASE_DAYS['decision_sent']
    rng_3a = np.random.default_rng(SEED)
    res_3a = simulate_permitting_cohort(100000, 'C0_no_friction', 'B0_baseline', rng_3a, pure_feedforward_test3a=True)
    sim_mean_3a = float(np.mean(res_3a['raw_T_dec']))
    sim_se_3a = float(np.std(res_3a['raw_T_dec'], ddof=1) / math.sqrt(100000))
    diff_3a = abs(sim_mean_3a - analytical_mean_test3a)
    z_score_3a = diff_3a / sim_se_3a
    rel_err_3a_pct = diff_3a / analytical_mean_test3a * 100.0
    test3a_passed = bool(z_score_3a < 1.96 and rel_err_3a_pct < 0.5)
    f_035 = 3.0 * 0.35 ** 2 - 2.0 * 0.35 ** 3
    f_070 = 3.0 * 0.7 ** 2 - 2.0 * 0.7 ** 3
    p_needs_advice = 1.0 - f_035
    p_extra_advice = 1.0 - f_070
    expected_advice_mult = p_needs_advice + 0.5 * p_extra_advice
    p_ext_mean = 0.1 + 0.55 * 0.5
    analytical_mean_test3b = PHASE_DAYS['application_received'] + PHASE_DAYS['application_receptive'] + expected_advice_mult * PHASE_DAYS['advice_known'] + (1.0 - p_ext_mean) * PHASE_DAYS['concept_decision_ready'] + p_ext_mean * PHASE_DAYS['concept_draft_decision_ready'] + PHASE_DAYS['draft_decision_ready'] + PHASE_DAYS['draft_decision_made'] + PHASE_DAYS['decision_ready'] + PHASE_DAYS['decision_taken'] + PHASE_DAYS['decision_sent']
    rng_3b = np.random.default_rng(SEED)
    res_3b = simulate_permitting_cohort(100000, 'C0_no_friction', 'B0_baseline', rng_3b, zero_rework_mixture_test3b=True)
    sim_mean_3b = float(np.mean(res_3b['raw_T_dec']))
    sim_se_3b = float(np.std(res_3b['raw_T_dec'], ddof=1) / math.sqrt(100000))
    diff_3b = abs(sim_mean_3b - analytical_mean_test3b)
    z_score_3b = diff_3b / sim_se_3b
    rel_err_3b_pct = diff_3b / analytical_mean_test3b * 100.0
    test3b_passed = bool(z_score_3b < 1.96 and rel_err_3b_pct < 0.5)
    r1 = simulate_permitting_cohort(5000, 'C2_threshold_governance', 'I2_rework_prevention', np.random.default_rng(SEED))
    r2 = simulate_permitting_cohort(5000, 'C2_threshold_governance', 'I2_rework_prevention', np.random.default_rng(SEED))
    test4_seed_exact = bool(np.array_equal(r1['raw_T_dec'], r2['raw_T_dec']))
    rng_b = np.random.default_rng(SEED)
    base_c0_res = simulate_permitting_cohort(50000, 'C0_no_friction', 'B0_baseline', rng_b)
    norew_c0_res = simulate_permitting_cohort(50000, 'C0_no_friction', 'B0_baseline', rng_b, disable_rework=True)
    assert not np.any(norew_c0_res['raw_has_rework_1']) and (not np.any(norew_c0_res['raw_has_rework_2']))
    reduction_c0_pct = (base_c0_res['overall']['mean'] - norew_c0_res['overall']['mean']) / base_c0_res['overall']['mean'] * 100.0
    base_c1_res = simulate_permitting_cohort(50000, 'C1_linear_handoff', 'B0_baseline', rng_b)
    norew_c1_res = simulate_permitting_cohort(50000, 'C1_linear_handoff', 'B0_baseline', rng_b, disable_rework=True)
    assert not np.any(norew_c1_res['raw_has_rework_1']) and (not np.any(norew_c1_res['raw_has_rework_2']))
    reduction_c1_pct = (base_c1_res['overall']['mean'] - norew_c1_res['overall']['mean']) / base_c1_res['overall']['mean'] * 100.0
    zero_rework_verified = bool(norew_c0_res['overall']['rework_rate_pct'] == 0.0 and norew_c0_res['overall']['second_rework_rate_pct'] == 0.0 and (norew_c1_res['overall']['rework_rate_pct'] == 0.0) and (norew_c1_res['overall']['second_rework_rate_pct'] == 0.0))
    hump_grid = []
    for extra_h in [0.0, 1.5, 3.0, 3.5, 5.0]:
        for gamma_high in [1.0, 0.9, 0.78, 0.65]:
            rng_g = np.random.default_rng(SEED + 500)
            res_g = simulate_permitting_cohort(20000, 'C2_threshold_governance', 'B0_baseline', rng_g, c2_mid_extra_handoffs=extra_h, c2_high_coord_factor=gamma_high)
            m_low = res_g['by_tier']['Low']['median']
            m_mid = res_g['by_tier']['Intermediate']['median']
            m_high = res_g['by_tier']['High']['median']
            r90_low = res_g['by_tier']['Low']['R_90']
            r90_mid = res_g['by_tier']['Intermediate']['R_90']
            r90_high = res_g['by_tier']['High']['R_90']
            excess_v = min(m_mid - m_low, m_mid - m_high) - 2.0
            is_hump = m_mid > m_low + 2.0 and m_mid > m_high + 2.0
            hump_grid.append({'mid_extra_handoffs': extra_h, 'high_coord_factor_gamma': gamma_high, 'median_Low': round(m_low, 2), 'median_Mid': round(m_mid, 2), 'median_High': round(m_high, 2), 'R90_Low': round(r90_low, 2), 'R90_Mid': round(r90_mid, 2), 'R90_High': round(r90_high, 2), 'excess_above_2d_criterion_V': round(excess_v, 2), 'hump_emerges': bool(is_hump)})
    rng_s_b0 = np.random.default_rng(SEED + 900)
    r_s_b0 = simulate_permitting_cohort(25000, 'C1_linear_handoff', 'B0_baseline', rng_s_b0)['overall']
    b0_sens_eff = {'median': round(r_s_b0['median'], 2), 'p90': round(r_s_b0['p90'], 2), 'P_56': round(r_s_b0['P_56'], 2), 'R_180': round(r_s_b0['R_180'], 2), '_raw_R_180': float(r_s_b0['R_180']), '_raw_p90': float(r_s_b0['p90'])}
    sensitivity_effectiveness = []
    for eff_scale in [0.5, 0.75, 1.0, 1.25]:
        row = {'effectiveness_multiplier': eff_scale, 'B0_baseline': {'median': b0_sens_eff['median'], 'p90': b0_sens_eff['p90'], 'P_56': b0_sens_eff['P_56'], 'R_180': b0_sens_eff['R_180']}}
        for intv in ['I1_routing_continuity', 'I2_rework_prevention', 'I3_targeted_intake']:
            rng_s = np.random.default_rng(SEED + 900)
            r_s = simulate_permitting_cohort(25000, 'C1_linear_handoff', intv, rng_s, intervention_eff_scale=eff_scale)['overall']
            row[intv] = {'median': round(r_s['median'], 2), 'p90': round(r_s['p90'], 2), 'P_56': round(r_s['P_56'], 2), 'R_180': round(r_s['R_180'], 2), 'reduction_R_180_vs_same_seed_B0': round(b0_sens_eff['_raw_R_180'] - float(r_s['R_180']), 2), 'reduction_p90_vs_same_seed_B0': round(b0_sens_eff['_raw_p90'] - float(r_s['p90']), 2)}
        sensitivity_effectiveness.append(row)
    sensitivity_targeting_error = []
    for sigma_err in [0.0, 0.1, 0.2, 0.3]:
        rng_t = np.random.default_rng(SEED + 1200)
        r_t = simulate_permitting_cohort(25000, 'C1_linear_handoff', 'I3_targeted_intake', rng_t, i3_random_targeting_error=sigma_err)['overall']
        sensitivity_targeting_error.append({'targeting_noise_sigma': sigma_err, 'triaged_share_pct': round(r_t['triaged_share_pct'], 2), 'true_positive_coverage_pct': round(r_t['true_positive_coverage_pct'], 2), 'false_positive_rate_pct': round(r_t['false_positive_rate_pct'], 2), 'median': round(r_t['median'], 2), 'p90': round(r_t['p90'], 2), 'P_56': round(r_t['P_56'], 2), 'R_180': round(r_t['R_180'], 2)})
    sensitivity_holding_shape = []
    for k_mult in [0.5, 1.0, 2.0]:
        row = {'gamma_shape_multiplier': k_mult}
        for intv in ['B0_baseline', 'I1_routing_continuity', 'I2_rework_prevention', 'I3_targeted_intake']:
            rng_k = np.random.default_rng(SEED + 1500)
            r_k = simulate_permitting_cohort(25000, 'C1_linear_handoff', intv, rng_k, gamma_shape_multiplier=k_mult)['overall']
            row[intv] = {'median': round(r_k['median'], 2), 'p90': round(r_k['p90'], 2), 'R_180': round(r_k['R_180'], 2)}
        sensitivity_holding_shape.append(row)
    return {'verification_tests': {'test1_positivity_all_phases_gt_zero': test1_positivity, 'test2_strict_milestone_ordering': test2_ordering, 'test3a_pure_feedforward_route': {'analytical_expected_days': round(analytical_mean_test3a, 4), 'simulated_mean_days': round(sim_mean_3a, 4), 'mc_standard_error_days': round(sim_se_3a, 4), 'abs_discrepancy_days': round(diff_3a, 4), 'z_score': round(z_score_3a, 4), 'relative_error_pct': round(rel_err_3a_pct, 4), 'passed': test3a_passed}, 'test3b_zero_rework_mixture_route': {'analytical_expected_days': round(analytical_mean_test3b, 4), 'simulated_mean_days': round(sim_mean_3b, 4), 'mc_standard_error_days': round(sim_se_3b, 4), 'abs_discrepancy_days': round(diff_3b, 4), 'z_score': round(z_score_3b, 4), 'relative_error_pct': round(rel_err_3b_pct, 4), 'passed': test3b_passed}, 'test4_deterministic_seed_replicability': test4_seed_exact, 'test5_external_benchmark_complete_rework_removal': {'published_teinemaa_bimp_reduction_pct': 24.46, 'zero_first_and_second_loop_rework_verified': zero_rework_verified, 'C0_baseline_mean_days': round(base_c0_res['overall']['mean'], 2), 'C0_zero_rework_mean_days': round(norew_c0_res['overall']['mean'], 2), 'simulated_C0_complete_rework_removal_reduction_pct': round(reduction_c0_pct, 2), 'C1_baseline_mean_days': round(base_c1_res['overall']['mean'], 2), 'C1_zero_rework_mean_days': round(norew_c1_res['overall']['mean'], 2), 'simulated_C1_complete_rework_removal_reduction_pct': round(reduction_c1_pct, 2)}}, 'c2_hump_emergence_grid': hump_grid, 'sensitivity_effectiveness': sensitivity_effectiveness, 'sensitivity_targeting_error': sensitivity_targeting_error, 'sensitivity_holding_shape': sensitivity_holding_shape}
