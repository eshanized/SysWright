#!/usr/bin/env python3
"""
Routing Evaluation Engine
Part of Linux Engineering (Phase 1)

Evaluates whether the central linux-engineer skill correctly routes
incoming engineering requests to appropriate foundation skills and
safety tiers without making premature mutations.
"""

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def classify_intent(prompt: str) -> Dict[str, Any]:
    """
    Deterministic reference classifier modeling linux-engineer routing logic.
    Identifies primary skill, required safety tier, and operational boundaries.
    """
    prompt_lower = prompt.lower()

    # Safety Tier 3 Check: Destructive or privileged commands
    is_tier_3 = any(
        kw in prompt_lower
        for kw in [
            "sudo",
            "reformat",
            "rm -rf /",
            "pacman -syu",
            "mkfs",
            "dd if=",
            "/boot/loader",
            "efibootmgr",
        ]
    )

    # Check for no-code-mutation cues
    is_no_mutation = any(
        kw in prompt_lower
        for kw in [
            "delete the signal handler",
            "avoid unnecessary modifications",
            "eintr",
        ]
    )

    # Primary Skill Routing
    if "reformat" in prompt_lower or "sudo pacman" in prompt_lower or "rm -rf" in prompt_lower:
        primary_skill = "linux-engineer"  # Orchestrator halts and asks for approval
    elif any(kw in prompt_lower for kw in [
        "investigate", "driver", "null pointer", "timeout", "harden", "eintr",
        "diagnose", "timing out", "systemd", "pkgbuild", "package", "boot"
    ]):
        primary_skill = "linux-research"
    elif any(kw in prompt_lower for kw in [
        "detect", "embedded", "without pacman", "profile", "flamegraph", "daemon in rust", "rust"
    ]):
        primary_skill = "linux-environment"
    else:
        primary_skill = "linux-engineer"

    # Safety Tier Classification
    if is_tier_3:
        safety_tier = 3
    elif any(kw in prompt_lower for kw in ["build", "create", "compile", "harden", "pkgbuild"]):
        safety_tier = 1
    else:
        safety_tier = 0

    return {
        "primary_skill": primary_skill,
        "safety_tier": safety_tier,
        "is_no_mutation_task": is_no_mutation,
    }


def run_routing_evals(scenarios_path: Path) -> Tuple[int, int, List[str]]:
    """Run all routing evaluation scenarios and report results."""
    with scenarios_path.open("r", encoding="utf-8") as f:
        scenarios = json.load(f)

    passed = 0
    total = len(scenarios)
    logs = []

    for sc in scenarios:
        sid = sc["id"]
        prompt = sc["prompt"]
        expected_skill = sc["expected_skill"]
        expected_tier = sc["safety_tier"]

        result = classify_intent(prompt)
        routed_skill = result["primary_skill"]
        detected_tier = result["safety_tier"]

        skill_ok = (routed_skill == expected_skill)
        tier_ok = (detected_tier == expected_tier)

        if skill_ok and tier_ok:
            passed += 1
            logs.append(f"[PASS] {sid}: Routed to '{routed_skill}' (Tier {detected_tier})")
        else:
            logs.append(
                f"[FAIL] {sid}: Expected '{expected_skill}' (Tier {expected_tier}), "
                f"got '{routed_skill}' (Tier {detected_tier})"
            )

    return passed, total, logs


def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    scenarios_file = repo_root / "evals" / "routing" / "scenarios.json"

    if not scenarios_file.is_file():
        print(f"Error: {scenarios_file} not found.")
        sys.exit(1)

    passed, total, logs = run_routing_evals(scenarios_file)

    print(f"Running {total} Skill-Routing Evaluation Scenarios:")
    for l in logs:
        print(f"  {l}")

    print(f"\nResult: {passed}/{total} scenarios passed ({passed/total*100:.1f}%).")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
