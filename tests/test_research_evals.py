#!/usr/bin/env python3
"""
Unit tests for research evaluations
Part of Syswright (Phase 1)
"""

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "evals" / "research"))
from eval_research import run_research_evals


class TestResearchEvals(unittest.TestCase):

    def test_all_6_research_scenarios_pass(self):
        """All 6 research evaluation scenarios must pass with 100% accuracy."""
        repo_root = Path(__file__).resolve().parent.parent
        cases_file = repo_root / "evals" / "research" / "cases.json"
        passed, total, logs = run_research_evals(cases_file)
        self.assertEqual(total, 6)
        self.assertEqual(passed, total, f"Research evals failed: {logs}")


if __name__ == "__main__":
    unittest.main()
