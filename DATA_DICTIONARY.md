# Data dictionary

## Input datasets

`phase_means.csv`: phase identifier, published adopted mean in hours, and conversion to days (hours / 24). These are published-summary inputs, not new empirical estimates.

`municipal_inventory.csv`: municipality identifier, upstream DOI, number of cases, events, and municipal event classes. Municipal event-class counts are not additive collection-level distinct counts.

`parameters_and_assumptions.json`: provenance-separated calibration summaries and scenario specifications.

## Output datasets

| File | Observation unit |
|---|---|
| scenario_summaries.csv | Experiment block × configuration × policy × metric |
| tier_summaries.csv | Experiment block × configuration × policy × complexity tier × metric |
| matched_contrasts.csv | Configuration × intervention × metric, relative to block-specific B0 |
| replication_metrics.csv | Nominal replication × policy/configuration; 2,000 cases per row |
| input_scenario_metrics.csv | Assumed-input scenario × policy/configuration; 1,500 cases per row |
| input_vectors.csv | Full parameter vector × policy/configuration; includes all 16 phase scales |
| complexity_grid.csv | One of 20 C2 referral/coordination cells |
| sensitivity_effectiveness.csv | Effectiveness multiplier × policy; 25,000 cases per row |
| sensitivity_targeting.csv | Screening-noise setting under I3; 25,000 cases per row |
| sensitivity_shape.csv | Gamma-shape multiplier × policy; 25,000 cases per row |
| figure_data.csv | Figure panel × plotted point or cost summary |
| cost_boundaries.csv | Pairwise cost-ratio threshold using nominal C1 restricted-time benefits |
| results.json | Hierarchical summaries, matched contrasts, verification and sensitivities |
| verification.json | Internal mathematical and implementation checks |

## Metrics and units

- `mean`, `median`, `iqr_25`, `iqr_75`, `p90`: elapsed calendar-day decision-duration statistics.
- `P_56`, `P_90`, `P_180`: completion probabilities reported in percent, not proportions.
- `R_90`, `R_180`: mean of min(decision duration, horizon), in days.
- `T_irrev_median`, `T_irrev_p90`: post-decision terminal-milestone duration summaries, in days.
- `rework_rate_pct`, `second_rework_rate_pct`: first- and second-loop occurrence percentages over all cases.
- `mean_handoffs`: realized mean handoff count.
- `triaged_share_pct`: percentage of all cases treated.
- `true_positive_coverage_pct`: percentage treated among truly eligible cases.
- `false_positive_rate_pct`: percentage treated among truly ineligible cases.
- `phase_scale_*`: dimensionless multipliers for adopted phase means.
- `rework_prob_base`: baseline rework probability as a proportion.
- `handoff_delay_base`: assumed mean delay per handoff, in days.
- `effectiveness_multiplier`, `gamma_shape_multiplier`, `high_coord_factor_gamma`: dimensionless scenario factors.
- `targeting_noise_sigma`: standard deviation on the dimensionless complexity scale.
- `excess_above_2d_criterion_V`: min(mid median − low median, mid median − high median) − 2, in days; positive values meet the criterion.

## Summary and contrast conventions

`estimate` is the mean of replication-specific statistics, not a quantile from concatenated case records. `batch_mean_se` is the standard error across replication statistics. `rep_pr_lower` and `rep_pr_upper` are the 2.5th and 97.5th percentiles across 30 replications. `input_vi_lower` and `input_vi_upper` are the central 95% range across 100 assumed-input scenarios; they are not empirical confidence intervals.

`delta` means intervention minus baseline. Negative duration differences indicate improvement; positive completion-probability differences indicate improvement. `figure_data.csv` reports duration savings with reversed sign and reversed interval endpoints. Only actual interval endpoints occupy `interval_lower` and `interval_upper`; baseline levels, costs, and tier medians have separate fields. Empty CSV cells mean not applicable or not reported, never zero.

`block` distinguishes the nominal configuration block from the separately seeded intervention block. A B0 estimate from one block is not interchangeable with a B0 estimate from another. Sensitivity experiments have dedicated seeds; their baselines are explicitly archived.

The source engine retains legacy JSON keys `mc_ci_95` and `param_ui_95`; their meanings are replicate-percentile ranges and assumed-input variation intervals, respectively. They must not be interpreted as sampling confidence intervals.

## Cost regions

For each policy i, nominal score = restricted-time benefit(i) / relative_cost(i). Pairwise equality occurs when cost(i)/cost(j) = benefit(i)/benefit(j), using the benefits archived in `cost_boundaries.csv`. Policy preference is the largest nominal score, not a budget-constrained or empirical monetary optimum.

## Precision and matching

CSV/JSON summaries retain the model exporter’s stated rounding. Replication metrics, scenario metrics, and complete input vectors retain numerical values without summary rounding. Matching checks compare complete vectors within each intervention configuration. Shared seeds do not guarantee alignment of all random draws after policy-dependent branches.
