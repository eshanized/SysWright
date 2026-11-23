#!/usr/bin/env python3
"""
Master Test Runner
Part of Syswright (Phase 1)

Discovers and runs all automated unit and integration tests across:
- Skill directory validation
- Reference integrity checking
- Packaging determinism and path traversal guards
- Environment discovery fixtures
- Routing evaluation scenarios
- Research evaluation scenarios
"""

import sys
import unittest
from pathlib import Path


def main():
    test_dir = Path(__file__).resolve().parent
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(test_dir),
        pattern="test_*.py",
        top_level_dir=str(test_dir.parent),
    )

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    print(f"Total Tests Run : {result.testsRun}")
    print(f"Failures        : {len(result.failures)}")
    print(f"Errors          : {len(result.errors)}")
    print("=" * 60)

    if result.wasSuccessful():
        print("OVERALL VERDICT: PASS (All tests passed cleanly)")
        sys.exit(0)
    else:
        print("OVERALL VERDICT: FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
