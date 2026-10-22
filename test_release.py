"""Validation of model invariants, archived datasets, and experiment matching."""
import unittest, json, csv, sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.model import SEED, simulate_permitting_cohort

def records(name):
    with (ROOT/'data/processed'/name).open(newline='') as f:return list(csv.DictReader(f))

class ReleaseTests(unittest.TestCase):
    def test_model_invariants_and_exact_repeatability(self):
        a=simulate_permitting_cohort(5000,'C2_threshold_governance','I2_rework_prevention',np.random.default_rng(SEED))
        b=simulate_permitting_cohort(5000,'C2_threshold_governance','I2_rework_prevention',np.random.default_rng(SEED))
        self.assertTrue(np.array_equal(a['raw_T_dec'],b['raw_T_dec']))
        self.assertTrue(np.all(a['raw_T_irrev']>a['raw_T_dec']))
        self.assertTrue(np.all(a['raw_T_dec']>a['raw_t_S1']))
        self.assertTrue(np.all(a['raw_t_S1']>0))
    def test_zero_rework_switch(self):
        a=simulate_permitting_cohort(5000,'C1_linear_handoff','B0_baseline',np.random.default_rng(SEED),disable_rework=True)
        self.assertFalse(np.any(a['raw_has_rework_1']))
        self.assertFalse(np.any(a['raw_has_rework_2']))
    def test_archived_implementation_checks(self):
        v=json.loads((ROOT/'data/processed/verification.json').read_text())
        self.assertTrue(v['test1_positivity_all_phases_gt_zero'])
        self.assertTrue(v['test2_strict_milestone_ordering'])
        self.assertTrue(v['test3a_pure_feedforward_route']['passed'])
        self.assertTrue(v['test3b_zero_rework_mixture_route']['passed'])
        self.assertTrue(v['test4_deterministic_seed_replicability'])
        self.assertTrue(v['test5_external_benchmark_complete_rework_removal']['zero_first_and_second_loop_rework_verified'])
    def test_full_input_vector_matching(self):
        rows=records('input_vectors.csv');self.assertEqual(len(rows),1600)
        columns=[k for k in rows[0] if k.startswith('phase_scale_')]+['rework_prob_base','handoff_delay_base','trajectory_seed']
        self.assertEqual(len(columns),19)
        groups={}
        for r in rows:
            if r['block']=='intervention':groups.setdefault((r['configuration'],r['scenario_index']),[]).append(tuple(r[c] for c in columns))
        self.assertEqual(len(groups),300)
        for g in groups.values():self.assertEqual(len(g),4);self.assertEqual(len(set(g)),1)
    def test_grid(self):
        g=records('complexity_grid.csv');self.assertEqual(len(g),20)
        self.assertEqual(sum(r['hump_emerges']=='True' for r in g),16)
        for r in g:
            v=min(float(r['median_Mid'])-float(r['median_Low']),float(r['median_Mid'])-float(r['median_High']))-2
            self.assertAlmostEqual(v,float(r['excess_above_2d_criterion_V']),delta=.02)
    def test_ensemble_dimensions(self):
        self.assertEqual(len(records('replication_metrics.csv')),480)
        self.assertEqual(len(records('input_scenario_metrics.csv')),1600)
        self.assertEqual(len(records('matched_contrasts.csv')),54)
    def test_figure_interval_semantics(self):
        for r in records('figure_data.csv'):
            if r['interval_lower']:
                self.assertEqual(r['figure'],'3')
                self.assertLessEqual(float(r['interval_lower']),float(r['interval_upper']))
    def test_effectiveness_baseline_is_shared(self):
        rows=records('sensitivity_effectiveness.csv')
        baseline=[r for r in rows if r['policy']=='B0_baseline']
        self.assertEqual(len(baseline),4)
        self.assertEqual(len({r['R_180'] for r in baseline}),1)
        b=float(baseline[0]['R_180'])
        for r in rows:
            if r['policy']!='B0_baseline':self.assertAlmostEqual(b-float(r['R_180']),float(r['reduction_R_180_vs_same_seed_B0']),delta=.02)

if __name__=='__main__':unittest.main()
