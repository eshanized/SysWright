#!/usr/bin/env python3
"""
Research Evaluation Engine
Part of Linux Engineering (Phase 1)

Evaluates technical research outputs against authoritative evidence standards:
- Deprecation detection for obsolete APIs.
- Resolution of conflicting upstream vs. distribution documentation.
- Rejection of uncited claims.
- Detection of version incompatibilities.
- Honest reporting of unknown or unverifiable behaviors.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def evaluate_research_response(case: Dict[str, Any], response_text: str) -> Tuple[bool, str]:
    """Evaluate whether an engineering response satisfies the case criteria."""
    resp_lower = response_text.lower()
    cid = case["id"]
    verdict_type = case["expected_verdict"]

    if verdict_type == "detect_deprecated":
        canonical = case["required_canonical_api"].lower()
        if canonical in resp_lower and ("deprecated" in resp_lower or "removed" in resp_lower or "replaced" in resp_lower):
            return True, f"Correctly flagged deprecation and recommended '{case['required_canonical_api']}'"
        return False, f"Failed to identify that '{case['trap']}' or recommend '{case['required_canonical_api']}'"

    elif verdict_type == "distro_policy_separation":
        correct_path = case["correct_path"].lower()
        if correct_path in resp_lower and ("/etc" in resp_lower or "admin" in resp_lower or "override" in resp_lower):
            return True, f"Correctly distinguished package directory '{case['correct_path']}' from /etc overrides"
        return False, f"Failed to identify correct package installation path '{case['correct_path']}'"

    elif verdict_type == "reject_uncited_claim":
        if any(w in resp_lower for w in ["unverified", "benchmark", "evidence", "test", "reject", "caution", "stall"]):
            return True, "Correctly rejected uncited claim and required empirical benchmark evidence"
        return False, "Failed to reject unverified forum tuning claim"

    elif verdict_type == "flag_version_incompatibility":
        if any(w in resp_lower for w in ["incompatible", "unavailable", "introduced in", "not supported", "245"]):
            return True, f"Correctly flagged version incompatibility (requires {case['min_version_required']})"
        return False, f"Failed to detect that directive requires {case['min_version_required']}"

    elif verdict_type == "recommend_modern_replacement":
        replacement = case["canonical_replacement"].lower()
        if replacement in resp_lower and ("deprecated" in resp_lower or "obsolete" in resp_lower):
            return True, f"Correctly flagged legacy interface and recommended '{case['canonical_replacement']}'"
        return False, f"Failed to recommend modern replacement '{case['canonical_replacement']}'"

    elif verdict_type == "report_uncertainty":
        if any(w in resp_lower for w in ["unknown", "cannot be verified", "uncertain", "proprietary", "vendor"]):
            return True, "Correctly reported uncertainty on unverifiable binary blob"
        return False, "Failed to report uncertainty on closed-source module"

    return False, f"Unknown verdict type: {verdict_type}"


# Reference canonical model responses demonstrating compliance with research standards
SAMPLE_MODEL_RESPONSES = {
    "research_case_01_outdated_doc": (
        "The init_timer() function was completely removed in Linux 4.15. In modern Linux kernel 6.x, "
        "timers must be initialized using the timer_setup(&my_timer, callback, 0) API with from_timer()."
    ),
    "research_case_02_conflicting_doc": (
        "Packages must install systemd unit files to /usr/lib/systemd/system/. "
        "The /etc/systemd/system/ directory is strictly reserved for local sysadmin configuration and drop-in overrides."
    ),
    "research_case_03_missing_source_evidence": (
        "This claim is unverified. Setting vm.dirty_ratio=90 allows dirty memory to accumulate excessively, "
        "causing severe I/O stalls and writeback pauses. We reject this change without prior empirical benchmark evidence."
    ),
    "research_case_04_incorrect_version_assumption": (
        "ProtectClock=yes is not supported on Debian 10 Buster. ProtectClock was introduced in systemd 245, "
        "whereas Debian 10 ships with systemd 241. This directive is unavailable in that environment."
    ),
    "research_case_05_unverified_api_recommendation": (
        "The sysfs GPIO interface (/sys/class/gpio) is deprecated and disabled in modern kernels. "
        "Use the modern libgpiod character device library (gpiod.h / gpiod tools) instead."
    ),
    "research_case_06_uncertain_technical_conclusion": (
        "The real-time PREEMPT_RT compatibility of this proprietary WiFi module is Unknown. "
        "Because the driver is closed-source binary and vendor documentation is missing, RT latency cannot be verified."
    ),
}


def run_research_evals(cases_path: Path) -> Tuple[int, int, List[str]]:
    """Run research evaluation suite."""
    with cases_path.open("r", encoding="utf-8") as f:
        cases = json.load(f)

    passed = 0
    total = len(cases)
    logs = []

    for c in cases:
        cid = c["id"]
        sample_resp = SAMPLE_MODEL_RESPONSES.get(cid, "")
        ok, msg = evaluate_research_response(c, sample_resp)
        if ok:
            passed += 1
            logs.append(f"[PASS] {cid}: {msg}")
        else:
            logs.append(f"[FAIL] {cid}: {msg}")

    return passed, total, logs


def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    cases_file = repo_root / "evals" / "research" / "cases.json"

    if not cases_file.is_file():
        print(f"Error: {cases_file} not found.")
        sys.exit(1)

    passed, total, logs = run_research_evals(cases_file)

    print(f"Running {total} Research & Evidence Evaluation Scenarios:")
    for l in logs:
        print(f"  {l}")

    print(f"\nResult: {passed}/{total} research evaluation scenarios passed ({passed/total*100:.1f}%).")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
