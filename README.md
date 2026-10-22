# Administrative Coordination and Permitting Delays

Computational dataset and semi-Markov simulation code for *Administrative Coordination and Permitting Delays: An Open-Data-Informed Simulation Study*.

## Scope

The repository contains adopted published phase means, explicit scenario assumptions, and synthetic simulation results. It does not contain raw municipal event logs or individual administrative records. Calibration inputs derive from published BPI Challenge 2015 summaries and the diagnostic report by Teinemaa, Leontjeva, and Masing (2015).

## Reproduction

Tested with Python 3.12 and NumPy 1.26.4.

```sh
python -m pip install -r requirements.txt
python scripts/run_all.py
python -m unittest discover -s tests -v
python scripts/check_integrity.py
```

The pipeline regenerates input ledgers, aggregate outputs, replication metrics, input-scenario metrics, complete input vectors, matched contrasts, sensitivity sweeps, and figure-source data. Existing generated data files are overwritten. The base random seed is 20261021. Environment metadata records the generating environment; results in other NumPy versions are not asserted to be bitwise identical.

## Repository structure

- `src/model.py`: model equations and experiment functions.
- `scripts/run_all.py`: generation and export pipeline.
- `scripts/check_integrity.py`: release-file checksum verification.
- `tests/`: executable validation checks.
- `data/inputs/`: adopted published-summary inputs and scenario parameter ledger.
- `data/processed/`: generated CSV/JSON datasets.
- `DATA_DICTIONARY.md`: schemas, units, signs, and interval definitions.
- `metadata/`: environment, provenance, and machine-readable validation record.
- `CITATION.cff`: citation metadata.
- `.zenodo.json`: deposit metadata without an assigned DOI or license.
- `SHA256SUMS`: checksums for distributed files.

## Experimental design

The configuration block compares C0–C3 under B0 using 30 replications of 2,000 cases and 100 input scenarios of 1,500 cases. The intervention block evaluates B0 and I1–I3 within C1–C3. Policies within a configuration share complete input vectors and trajectory seeds. Policy-dependent branches can change consumption of random draws; exact alignment of all random variates across policies is not claimed.

All 16 phase-scale factors, baseline rework probability, and handoff-delay parameter are archived for each input scenario. The C2 grid contains 20 cells. Effectiveness, targeting noise, and shape sensitivity use dedicated seeds and 25,000 cases per policy/setting. Their baselines are experiment-specific.

## Interpretation

Durations are elapsed calendar times, not active labor hours. Completion by Day 56 is not a legal-compliance indicator. Replicate-percentile ranges describe finite-batch simulation variability. Assumed-input variation intervals describe sensitivity to declared perturbations, not confidence intervals for field effects. Implementation checks do not establish external validation. Cost weights are hypothetical relative units. The historical BIMP percentage is contextual because its endpoint and intervention differ.

## Citation and upstream evidence

Use `CITATION.cff` for the software/data package. No repository URL, publication DOI, or archive DOI is asserted before assignment.

- van Dongen, B. F. (2015). BPI Challenge 2015. 4TU.ResearchData. Collection DOI: 10.4121/uuid:31a308ef-c844-48da-948c-305d167a0ec1.
- Teinemaa, I., Leontjeva, A., and Masing, K.-O. (2015). *BPIC 2015: Diagnostics of Building Permit Application Process in Dutch Municipalities*. BPI Challenge 2015 technical report.

## License

The simulation software and associated documentation are licensed under
the MIT License. See LICENSE.

Copyright (c) 2026 Arash Aghili.

Third-party materials retain their original rights and license terms.
