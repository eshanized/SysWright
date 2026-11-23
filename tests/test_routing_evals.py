#!/usr/bin/env python3
"""
Unit tests for routing evaluations
Part of Syswright (Phase 1)
"""

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "evals" / "routing"))
from eval_router import run_routing_evals


class TestRoutingEvals(unittest.TestCase):

    def test_all_10_routing_scenarios_pass(self):
        """All 10 routing evaluation scenarios must pass with 100% accuracy."""
        repo_root = Path(__file__).resolve().parent.parent
        scenarios_file = repo_root / "evals" / "routing" / "scenarios.json"
        passed, total, logs = run_routing_evals(scenarios_file)
        self.assertEqual(total, 10)
        self.assertEqual(passed, total, f"Routing evals failed: {logs}")


if __name__ == "__main__":
    unittest.main()
