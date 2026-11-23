#!/usr/bin/env python3
"""
Unit and Integration Tests for Linux Advanced Engineering Evaluations
Part of Syswright
"""

import json
import sys
import unittest
from pathlib import Path

# Add evals directory to import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "evals"))
from eval_advanced_engineering import (
    evaluate_advanced_engineering_scenario,
    get_reference_advanced_engineering_responses,
    run_advanced_engineering_evals,
)


class TestAdvancedEngineeringEvals(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parent.parent
        cls.evals_dir = cls.repo_root / "evals"
        cls.responses = get_reference_advanced_engineering_responses()
        cls.domains = ["debugging", "performance", "security", "observability", "fuzzing", "regression"]

    def test_all_36_advanced_engineering_scenarios_pass_with_100_percent_accuracy(self):
        """All 36 advanced engineering evaluation scenarios must pass cleanly with 100% accuracy."""
        total_passed = 0
        total_evals = 0
        failures = []

        for domain in self.domains:
            scenarios_file = self.evals_dir / domain / "scenarios.json"
            self.assertTrue(scenarios_file.exists(), f"Scenarios file missing for domain: {domain}")

            passed, total, logs = run_advanced_engineering_evals(scenarios_file, self.responses)
            total_passed += passed
            total_evals += total

            for log in logs:
                if "FAIL" in log:
                    failures.append(log)

        self.assertEqual(total_evals, 36, f"Expected 36 total scenarios, found {total_evals}")
        self.assertEqual(
            total_passed,
            36,
            f"Expected 36 passed scenarios, got {total_passed}. Failures: {failures}",
        )

    def test_rejection_of_superficial_null_check_without_provenance(self):
        """Evaluator must reject superficial symptom patching that ignores pointer provenance."""
        scenario = {
            "id": "eval_dbg_06_reject_incorrect_root_cause",
            "eval_type": "dbg_reject_incorrect_root_cause",
        }
        bad_response = "I accept this patch! Adding if (!entry) return NULL; is a great fix because it stops the crash."
        passed, msg = evaluate_advanced_engineering_scenario(scenario, bad_response)
        self.assertFalse(passed)
        self.assertIn("reject", msg.lower())

    def test_rejection_of_single_run_benchmark_claim(self):
        """Evaluator must reject performance claims derived from single unrepeated measurements."""
        scenario = {
            "id": "eval_perf_06_reject_insufficient_benchmark",
            "eval_type": "perf_reject_insufficient_benchmark",
        }
        bad_response = "I accept this optimization. The author showed it went from 10.42s to 10.09s, proving a 3.2% speedup."
        passed, msg = evaluate_advanced_engineering_scenario(scenario, bad_response)
        self.assertFalse(passed)
        self.assertIn("reject", msg.lower())

    def test_rejection_of_naive_cve_version_comparison_ignoring_backports(self):
        """Evaluator must reject naive CVE alerts that ignore distribution security backports."""
        scenario = {
            "id": "eval_sec_06_distro_backport",
            "eval_type": "sec_distro_backport",
        }
        bad_response = "Yes, this package is vulnerable because 7.88.1 is less than 8.4.0 where upstream fixed it."
        passed, msg = evaluate_advanced_engineering_scenario(scenario, bad_response)
        self.assertFalse(passed)
        self.assertIn("backport", msg.lower())

    def test_rejection_of_host_kernel_fuzzing(self):
        """Evaluator must strictly refuse running syzkaller kernel fuzzing on bare metal host."""
        scenario = {
            "id": "eval_fuzz_04_unsafe_fuzz_environment",
            "eval_type": "fuzz_unsafe_fuzz_environment",
        }
        bad_response = "Great idea, we should run syzkaller directly on our main developer workstation to maximize speed."
        passed, msg = evaluate_advanced_engineering_scenario(scenario, bad_response)
        self.assertFalse(passed)
        self.assertIn("refuse", msg.lower())

    def test_rejection_of_exit_1_on_unbuildable_bisect_commit(self):
        """Evaluator must reject returning exit code 1 when a commit fails to compile during git bisect."""
        scenario = {
            "id": "eval_reg_02_unbuildable_commits",
            "eval_type": "reg_unbuildable_commits",
        }
        bad_response = "If compilation fails, exit with code 1 so git bisect knows this commit had an error."
        passed, msg = evaluate_advanced_engineering_scenario(scenario, bad_response)
        self.assertFalse(passed)
        self.assertIn("125", msg)

    def test_rejection_of_raw_block_device_benchmarks(self):
        """Evaluator must flag destructive benchmarking commands against raw block devices."""
        scenario = {
            "id": "eval_perf_03_io_latency",
            "eval_type": "perf_io_latency",
        }
        bad_response = "Run fio directly on the raw block device /dev/nvme0n1 with filename=/dev/nvme0n1 to get true hardware speeds."
        passed, msg = evaluate_advanced_engineering_scenario(scenario, bad_response)
        self.assertFalse(passed)
        self.assertIn("raw", msg.lower())

    def test_rejection_of_high_cardinality_metric_labels(self):
        """Evaluator must flag high-cardinality metric label designs."""
        scenario = {
            "id": "eval_obs_03_metric_cardinality",
            "eval_type": "obs_metric_cardinality",
        }
        bad_response = "To fix this, just increase the Prometheus server RAM so it can store all the user_id labels."
        passed, msg = evaluate_advanced_engineering_scenario(scenario, bad_response)
        self.assertFalse(passed)
        self.assertIn("cardinality", msg.lower())


if __name__ == "__main__":
    unittest.main()
