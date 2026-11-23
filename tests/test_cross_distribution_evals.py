#!/usr/bin/env python3
"""
Unit and Integration Tests for Linux Cross-Distribution Engineering Evaluations
Part of Linux Engineering (Phase 6)
"""

import json
import sys
import unittest
from pathlib import Path

# Add evals directory to import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "evals"))
from eval_cross_distribution import (
    evaluate_cross_distribution_scenario,
    get_reference_cross_distribution_responses,
    run_cross_distribution_evals,
)


class TestCrossDistributionEvals(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parent.parent
        cls.evals_dir = cls.repo_root / "evals"
        cls.responses = get_reference_cross_distribution_responses()
        cls.domains = [
            "debian-packaging",
            "ubuntu-packaging",
            "rpm-packaging",
            "fedora-packaging",
            "opensuse-packaging",
            "distribution-engineering",
            "reproducible-builds",
            "release-maintenance",
        ]

    def test_all_48_cross_distribution_scenarios_pass_with_100_percent_accuracy(self):
        """All 48 cross-distribution evaluation scenarios must pass cleanly with 100% accuracy."""
        total_passed = 0
        total_evals = 0
        failures = []

        for domain in self.domains:
            scenarios_file = self.evals_dir / domain / "scenarios.json"
            self.assertTrue(scenarios_file.exists(), f"Scenarios file missing for domain: {domain}")

            passed, total, logs = run_cross_distribution_evals(scenarios_file, self.responses)
            total_passed += passed
            total_evals += total

            for log in logs:
                if "FAIL" in log:
                    failures.append(log)

        self.assertEqual(total_evals, 48, f"Expected 48 total scenarios, found {total_evals}")
        self.assertEqual(
            total_passed,
            48,
            f"Expected 48 passed scenarios, got {total_passed}. Failures: {failures}",
        )

    def test_rejection_of_unchecked_scriptlet_in_rpm_upgrade(self):
        """Evaluator must reject RPM scriptlets that stop services without checking $1 == 0."""
        scenario = {
            "id": "eval_rpm_03_scriptlet_trap",
            "eval_type": "rpm_scriptlet_trap",
        }
        bad_response = "Just put systemctl stop myapp.service directly in %preun so it stops cleanly."
        passed, msg = evaluate_cross_distribution_scenario(scenario, bad_response)
        self.assertFalse(passed)
        self.assertIn("$1", msg)

    def test_rejection_of_binary_upload_to_launchpad_ppa(self):
        """Evaluator must reject uploading compiled binary packages directly to Launchpad PPAs."""
        scenario = {
            "id": "eval_ubu_01_ppa_preparation",
            "eval_type": "ubu_ppa_preparation",
        }
        bad_response = "Build binary .deb packages with dpkg-deb -b and upload the .deb files directly using dput."
        passed, msg = evaluate_cross_distribution_scenario(scenario, bad_response)
        self.assertFalse(passed)
        self.assertIn("source", msg.lower())

    def test_rejection_of_package_deletion_for_repository_rollback(self):
        """Evaluator must reject simply deleting packages from pools as an emergency rollback strategy."""
        scenario = {
            "id": "eval_dist_05_rollback_strategy",
            "eval_type": "dist_rollback_strategy",
        }
        bad_response = "Simply delete the bad RPM from the repository directory and re-run createrepo_c."
        passed, msg = evaluate_cross_distribution_scenario(scenario, bad_response)
        self.assertFalse(passed)
        self.assertTrue("delet" in msg.lower() or "cache" in msg.lower() or "epoch" in msg.lower())

    def test_rejection_of_bundled_libraries_in_fedora(self):
        """Evaluator must reject leaving bundled third-party libraries in Fedora spec files."""
        scenario = {
            "id": "eval_fed_03_unbundling_enforcement",
            "eval_type": "fed_unbundling_enforcement",
        }
        bad_response = "Keep the bundled sqlite3 and zlib in vendor/ because it makes the build simpler."
        passed, msg = evaluate_cross_distribution_scenario(scenario, bad_response)
        self.assertFalse(passed)
        self.assertTrue("buildrequires" in msg.lower() or "unbundl" in msg.lower())

    def test_rejection_of_proceed_on_test_failure_in_release_gate(self):
        """Evaluator must reject approving a release candidate when tests fail on any supported architecture."""
        scenario = {
            "id": "eval_rel_06_release_readiness_gate",
            "eval_type": "rel_release_readiness_gate",
        }
        bad_response = "The arm64 test failure is intermittent so we can ignore it and approve the release immediately."
        passed, msg = evaluate_cross_distribution_scenario(scenario, bad_response)
        self.assertFalse(passed)
        self.assertTrue("block" in msg.lower() or "gate" in msg.lower() or "decision" in msg.lower())

    def test_rejection_of_volatile_timestamps_in_reproducible_builds(self):
        """Evaluator must reject ignoring __DATE__ and SOURCE_DATE_EPOCH in reproducibility diagnoses."""
        scenario = {
            "id": "eval_repro_01_timestamp_diagnosis",
            "eval_type": "repro_timestamp_diagnosis",
        }
        bad_response = "Diffoscope shows differences, but that is fine because timestamps always change between builds."
        passed, msg = evaluate_cross_distribution_scenario(scenario, bad_response)
        self.assertFalse(passed)
        self.assertTrue("source_date_epoch" in msg.lower() or "timestamp" in msg.lower())


if __name__ == "__main__":
    unittest.main()
