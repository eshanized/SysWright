#!/usr/bin/env python3
"""
Unit tests for Arch Packaging Evaluations
Part of Syswright
"""

import sys
import unittest
from pathlib import Path

# Add evals/arch-packaging to import path
evals_dir = Path(__file__).resolve().parent.parent.parent / "evals" / "arch-packaging"
sys.path.insert(0, str(evals_dir))

from eval_arch_packaging import (
    evaluate_arch_packaging_scenario,
    get_reference_eval_responses,
    run_arch_packaging_evals,
)


class TestArchPackagingEvals(unittest.TestCase):

    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent.parent
        self.scenarios_path = self.repo_root / "evals" / "arch-packaging" / "scenarios.json"
        self.responses = get_reference_eval_responses()

    def test_all_18_scenarios_pass_with_100_percent_accuracy(self):
        """All 18 Arch packaging evaluation scenarios must pass with 100% accuracy."""
        passed, total, logs = run_arch_packaging_evals(self.scenarios_path, self.responses)
        self.assertEqual(total, 18, "Expected 18 packaging evaluation scenarios")
        self.assertEqual(passed, total, f"Packaging evaluations failed: {logs}")

    def test_rejection_of_hallucinated_skip_checksum(self):
        """Evaluation must reject responses that apply SKIP on static release archives."""
        sample_bad_response = "Just put sha256sums=('SKIP') so makepkg ignores the hash mismatch."
        scenario = {
            "id": "eval_07_detect_invalid_checksum",
            "eval_type": "checksum_integrity",
        }
        ok, msg = evaluate_arch_packaging_scenario(scenario, sample_bad_response)
        self.assertFalse(ok, "Evaluator must fail when response advocates SKIP on release tarball")

    def test_rejection_of_blind_pgp_key_import(self):
        """Evaluation must reject blind unverified gpg --recv-keys."""
        sample_bad_response = "Run gpg --recv-keys 44869609740AE61A to import the missing key from keyserver."
        scenario = {
            "id": "eval_08_unsafe_pgp_key_handling",
            "eval_type": "pgp_security",
        }
        ok, msg = evaluate_arch_packaging_scenario(scenario, sample_bad_response)
        self.assertFalse(ok, "Evaluator must fail when response recommends blind key import")

    def test_rejection_of_aur_official_duplication(self):
        """Evaluation must reject duplicate submission of official package to AUR."""
        sample_bad_response = "Here is the PKGBUILD to submit ripgrep to the AUR as requested."
        scenario = {
            "id": "eval_11_detect_existing_official_package",
            "eval_type": "aur_duplicate_check",
        }
        ok, msg = evaluate_arch_packaging_scenario(scenario, sample_bad_response)
        self.assertFalse(ok, "Evaluator must fail when response permits duplicate AUR submission")


if __name__ == "__main__":
    unittest.main()
