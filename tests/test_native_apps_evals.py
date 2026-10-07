#!/usr/bin/env python3
"""
Unit and Integration Tests for Linux Native Application Engineering Evaluations
Part of Linux Engineering (Phase 4)
"""

import json
import sys
import unittest
from pathlib import Path

# Add evals directory to import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "evals"))
from eval_native_apps import (
    evaluate_native_apps_scenario,
    get_reference_native_apps_responses,
    run_native_apps_evals,
)


class TestNativeAppsEvals(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parent.parent
        cls.evals_dir = cls.repo_root / "evals"
        cls.responses = get_reference_native_apps_responses()
        cls.domains = ["applications", "qt", "gtk", "desktop-integration", "build-engineering"]

    def test_all_34_native_apps_scenarios_pass_with_100_percent_accuracy(self):
        """All 34 native application evaluation scenarios must pass cleanly with 100% accuracy."""
        total_passed = 0
        total_evals = 0
        failures = []

        for domain in self.domains:
            scenarios_file = self.evals_dir / domain / "scenarios.json"
            self.assertTrue(scenarios_file.exists(), f"Scenarios file missing for domain: {domain}")

            passed, total, logs = run_native_apps_evals(scenarios_file, self.responses)
            total_passed += passed
            total_evals += total

            for log in logs:
                if "FAIL" in log:
                    failures.append(log)

        self.assertEqual(total_evals, 34, f"Expected 34 total scenarios, found {total_evals}")
        self.assertEqual(
            total_passed,
            34,
            f"Expected 34 passed scenarios, got {total_passed}. Failures: {failures}",
        )

    def test_rejection_of_unnecessary_tokio_for_cli(self):
        """Evaluator must reject unnecessary Tokio runtime recommendations for simple CLI file hashing."""
        scenario = {
            "id": "eval_app_01_rust_cli",
            "eval_type": "app_rust_cli",
        }
        bad_response = "You should definitely use Tokio async runtime for this CLI tool to hash files."
        passed, reason = evaluate_native_apps_scenario(scenario, bad_response)
        self.assertFalse(passed)
        self.assertIn("tokio", reason.lower())

    def test_rejection_of_c_resource_leaks(self):
        """Evaluator must flag resource leaks on early returns in C utilities."""
        scenario = {
            "id": "eval_app_02_c_systems_utility",
            "eval_type": "app_c_utility",
        }
        bad_response = "The C code looks fine. It handles errors by returning 1 on error."
        passed, reason = evaluate_native_apps_scenario(scenario, bad_response)
        self.assertFalse(passed)
        self.assertIn("leak", reason.lower())

    def test_rejection_of_unjoined_thread_crash(self):
        """Evaluator must flag std::terminate risk on unjoined std::thread."""
        scenario = {
            "id": "eval_app_03_cpp_modern_app",
            "eval_type": "app_cpp_modern",
        }
        bad_response = "The class correctly frees raw_buffer. The thread will run in background."
        passed, reason = evaluate_native_apps_scenario(scenario, bad_response)
        self.assertFalse(passed)
        self.assertIn("delete", reason.lower())

    def test_rejection_of_double_fork_daemonize(self):
        """Evaluator must reject obsolete double-fork daemonize anti-pattern."""
        scenario = {
            "id": "eval_app_04_system_daemon",
            "eval_type": "app_system_daemon",
        }
        bad_response = "Yes, use double-fork daemonize() with setsid() so the daemon detaches from the shell."
        passed, reason = evaluate_native_apps_scenario(scenario, bad_response)
        self.assertFalse(passed)
        self.assertIn("double-fork", reason.lower())

    def test_rejection_of_local_tcp_microservices(self):
        """Evaluator must reject bloated local TCP microservices for a single-host CLI tool."""
        scenario = {
            "id": "eval_app_05_inappropriate_microservices",
            "eval_type": "app_microservices_critique",
        }
        bad_response = "This 4-container microservice proposal is great! It decouples all components."
        passed, reason = evaluate_native_apps_scenario(scenario, bad_response)
        self.assertFalse(passed)
        self.assertIn("microservice", reason.lower())

    def test_rejection_of_unrestricted_dbus_command_execution(self):
        """Evaluator must reject D-Bus system bus methods exposing arbitrary command execution."""
        scenario = {
            "id": "eval_desktop_03_dbus_authorization",
            "eval_type": "desktop_dbus_authorization",
        }
        bad_response = "The D-Bus interface is valid and allows client apps to easily run commands as root."
        passed, reason = evaluate_native_apps_scenario(scenario, bad_response)
        self.assertFalse(passed)
        self.assertIn("polkit", reason.lower())

    def test_rejection_of_vtable_shift_without_soversion_bump(self):
        """Evaluator must flag C++ vtable ABI shifts without SOVERSION bump."""
        scenario = {
            "id": "eval_build_04_abi_compatibility",
            "eval_type": "build_abi_compatibility",
        }
        bad_response = "Adding a virtual function is backwards-compatible. SOVERSION 1 can be kept."
        passed, reason = evaluate_native_apps_scenario(scenario, bad_response)
        self.assertFalse(passed)
        self.assertIn("soversion", reason.lower())


if __name__ == "__main__":
    unittest.main()
