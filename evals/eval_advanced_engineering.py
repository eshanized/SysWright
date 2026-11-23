#!/usr/bin/env python3
"""
Linux Advanced Engineering Evaluation Engine
Part of Syswright (Phase 5)

Deterministic evaluation suite that verifies AI agent responses and engineering
recommendations across:
- Linux Debugging (GDB, core dumps, memory corruption, deadlocks, kernel panics)
- Linux Performance (perf, CPU counters, memory, I/O latency, network BDP, benchmarks)
- Linux Security (threat modeling, sandboxing, capabilities, seccomp, CVE backports)
- Linux Observability (tracefs, eBPF CO-RE, BPF verifier, metrics cardinality, tracing)
- Linux Fuzzing (libFuzzer, AFL++, syzkaller, sanitizers, crash triage, minimization)
- Linux Regression Engineering (git bisect, exit 125, kernel regressions, ABI stability)
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def evaluate_advanced_engineering_scenario(scenario: Dict[str, Any], response_text: str) -> Tuple[bool, str]:
    """
    Evaluates whether an engineering response satisfies the criteria for
    a specific Linux Advanced Engineering evaluation scenario.
    """
    resp_lower = response_text.lower()
    sid = scenario["id"]
    eval_type = scenario["eval_type"]

    # -------------------------------------------------------------
    # Domain 1: Linux Debugging
    # -------------------------------------------------------------
    if eval_type == "dbg_segfault":
        if "0x20" not in resp_lower and "offset" not in resp_lower:
            return False, "Failed to analyze register offset 0x20 from base pointer"
        if "%rax" not in resp_lower and "rax" not in resp_lower:
            return False, "Missing register analysis of faulting %rax"
        if "provenance" not in resp_lower and "caller" not in resp_lower and "why" not in resp_lower and "investigat" not in resp_lower:
            return False, "Missing pointer provenance investigation before patching"
        return True, "Accurate segmentation fault diagnosis with struct offset and provenance analysis"

    elif eval_type == "dbg_missing_symbols":
        if "debuginfod" not in resp_lower and "debuginfo" not in resp_lower and "symbol" not in resp_lower:
            return False, "Missing recommendation for debuginfod or debuginfo symbol packages"
        if "build-id" not in resp_lower and "build_id" not in resp_lower and "build id" not in resp_lower:
            return False, "Missing identification of ELF .note.gnu.build-id"
        if "conclu" in resp_lower and "definitive" in resp_lower and ("not" not in resp_lower and "refuse" not in resp_lower and "cannot" not in resp_lower and "never" not in resp_lower):
            return False, "Anti-pattern: claimed definitive diagnosis from incomplete ?? stack frames"
        return True, "Correct handling of stripped core dump with build-id and debuginfod resolution"

    elif eval_type == "dbg_memory_leak":
        if "definitely lost" not in resp_lower and "leak" not in resp_lower:
            return False, "Missing analysis of definitely lost memory leak"
        if "free" not in resp_lower and "release" not in resp_lower and "deallocat" not in resp_lower:
            return False, "Failed to identify missing deallocation in error/cleanup path"
        if "asan" not in resp_lower and "valgrind" not in resp_lower and "heaptrack" not in resp_lower and "sanitizer" not in resp_lower:
            return False, "Missing recommendation of AddressSanitizer/LeakSanitizer or heaptrack"
        return True, "Accurate memory leak diagnosis with leak classification and profiler usage"

    elif eval_type == "dbg_deadlock":
        if "abba" not in resp_lower and "circular" not in resp_lower:
            return False, "Failed to identify ABBA circular wait deadlock pattern"
        if "order" not in resp_lower and "hierarchy" not in resp_lower:
            return False, "Missing prescription of strict global lock ordering"
        if "thread apply all bt" not in resp_lower and "threads" not in resp_lower and "thread" not in resp_lower:
            return False, "Missing thread backtrace inspection command in GDB"
        return True, "Correct identification and architectural remediation of circular deadlock"

    elif eval_type == "dbg_kernel_panic":
        if "0x18" not in resp_lower and "offset" not in resp_lower:
            return False, "Failed to identify fault address 0x18 as struct offset from NULL base"
        if "taint" not in resp_lower and "out-of-tree" not in resp_lower and "module" not in resp_lower:
            return False, "Missing taint analysis of out-of-tree module (Tainted: G O)"
        if "dynamic debug" not in resp_lower and "ftrace" not in resp_lower and "qemu" not in resp_lower and "dmesg" not in resp_lower:
            return False, "Missing kernel diagnostic tool prescription (dynamic debug, ftrace, QEMU)"
        return True, "Accurate kernel oops diagnosis with offset analysis and taint classification"

    elif eval_type == "dbg_reject_incorrect_root_cause":
        if "reject" not in resp_lower and "insufficient" not in resp_lower and "not accept" not in resp_lower and "unacceptable" not in resp_lower and "refuse" not in resp_lower:
            return False, "Failed to reject superficial null check patch"
        if "provenance" not in resp_lower and "why" not in resp_lower and "underlying" not in resp_lower and "cause" not in resp_lower:
            return False, "Missing explanation of pointer provenance and root cause analysis"
        return True, "Properly rejected superficial null-check symptom patch"

    # -------------------------------------------------------------
    # Domain 2: Linux Performance
    # -------------------------------------------------------------
    elif eval_type == "perf_cpu_regression":
        if "ipc" not in resp_lower and "cycle" not in resp_lower:
            return False, "Missing instruction-per-cycle (IPC) analysis"
        if "branch" not in resp_lower and "miss" not in resp_lower:
            return False, "Missing analysis of high branch misprediction rate"
        if "perf record" not in resp_lower and "perf" not in resp_lower:
            return False, "Missing perf profiling recommendation"
        return True, "Accurate CPU bottleneck diagnosis with IPC, branch mispredictions, and perf"

    elif eval_type == "perf_memory_allocation":
        if "vsz" not in resp_lower and "rss" not in resp_lower and "pss" not in resp_lower:
            return False, "Missing distinction between VSZ, RSS, and PSS"
        if "heaptrack" not in resp_lower and "massif" not in resp_lower and "perf" not in resp_lower and "smaps" not in resp_lower:
            return False, "Missing memory profiling tool recommendation"
        if "pool" not in resp_lower and "reuse" not in resp_lower and "fragmentation" not in resp_lower and "arena" not in resp_lower:
            return False, "Missing architectural allocation optimization (object pool, buffer reuse, arena limits)"
        return True, "Accurate memory allocation profiling and fragmentation mitigation"

    elif eval_type == "perf_io_latency":
        if "raw" in resp_lower and "block" in resp_lower and "dev" in resp_lower and ("not" not in resp_lower and "never" not in resp_lower and "danger" not in resp_lower and "avoid" not in resp_lower):
            return False, "Anti-pattern: recommended destructive benchmark directly against raw block device"
        if "await" not in resp_lower and "iostat" not in resp_lower:
            return False, "Missing interpretation of iostat await latency"
        if "biolatency" not in resp_lower and "bpftrace" not in resp_lower and "fio" not in resp_lower:
            return False, "Missing bpftrace biolatency or fio non-destructive benchmark recommendation"
        return True, "Correct I/O latency analysis and non-destructive benchmarking discipline"

    elif eval_type == "perf_network_throughput":
        if "bdp" not in resp_lower and "bandwidth-delay" not in resp_lower and "buffer" not in resp_lower:
            return False, "Missing Bandwidth-Delay Product (BDP) analysis"
        if "tcp_rmem" not in resp_lower and "tcp_wmem" not in resp_lower and "socket" not in resp_lower:
            return False, "Missing socket buffer inspection via tcp_rmem / tcp_wmem"
        if "ss" not in resp_lower and "window" not in resp_lower:
            return False, "Missing TCP socket window scaling check via ss tool"
        return True, "Accurate high-BDP network throughput diagnosis and buffer sizing"

    elif eval_type == "perf_gui_startup":
        if "ld_debug" not in resp_lower and "linker" not in resp_lower and "relocation" not in resp_lower:
            return False, "Missing dynamic linker relocation audit via LD_DEBUG=statistics"
        if "synchronous" not in resp_lower and "main thread" not in resp_lower and "thread" not in resp_lower and "event loop" not in resp_lower:
            return False, "Missing identification of blocking synchronous I/O on GUI main event loop"
        return True, "Correct desktop cold launch analysis with relocation profiling and async offloading"

    elif eval_type == "perf_reject_insufficient_benchmark":
        if "reject" not in resp_lower and "insufficient" not in resp_lower and "not accept" not in resp_lower and "unacceptable" not in resp_lower and "refuse" not in resp_lower:
            return False, "Failed to reject benchmark claim based on single unrepeated run"
        if "noise" not in resp_lower and "variance" not in resp_lower and "statistical" not in resp_lower:
            return False, "Missing explanation of measurement noise and variance"
        if "repeat" not in resp_lower and "runs" not in resp_lower and "trials" not in resp_lower and "mean" not in resp_lower:
            return False, "Missing requirement for repeated runs and statistical metrics"
        return True, "Properly rejected speculative benchmark claim lacking statistical validity"

    # -------------------------------------------------------------
    # Domain 3: Linux Security
    # -------------------------------------------------------------
    elif eval_type == "sec_overprivileged_daemon":
        if "root" not in resp_lower or ("drop" not in resp_lower and "unprivileged" not in resp_lower and "user" not in resp_lower):
            return False, "Missing requirement to drop root user to unprivileged service user"
        if "cap_net_bind_service" not in resp_lower:
            return False, "Missing grant of narrow capability CAP_NET_BIND_SERVICE"
        return True, "Accurate privilege dropping and capability assignment for daemon"

    elif eval_type == "sec_unsafe_systemd_sandbox":
        if "protectsystem" not in resp_lower:
            return False, "Missing ProtectSystem=strict recommendation"
        if "nonewprivileges" not in resp_lower:
            return False, "Missing NoNewPrivileges=yes recommendation"
        if "systemcallfilter" not in resp_lower and "capabilityboundingset" not in resp_lower:
            return False, "Missing SystemCallFilter or CapabilityBoundingSet directives"
        return True, "Comprehensive systemd service sandboxing configuration"

    elif eval_type == "sec_vulnerable_dependency":
        if "reachab" not in resp_lower and "call" not in resp_lower and "path" not in resp_lower and "symbol" not in resp_lower:
            return False, "Missing check for reachable vulnerable code paths or symbols"
        if "shared" not in resp_lower and "system" not in resp_lower and "package" not in resp_lower and "patch" not in resp_lower:
            return False, "Missing recommendation to use system shared libraries or apply security patch"
        return True, "Defensive vulnerability assessment and dependency remediation"

    elif eval_type == "sec_kernel_security_misconfig":
        if "kaslr" not in resp_lower and "pointer" not in resp_lower:
            return False, "Missing identification that exposed kernel pointers defeat KASLR"
        if "ptrace" not in resp_lower:
            return False, "Missing identification of unrestricted ptrace risk"
        if "sysctl" not in resp_lower or ("kptr_restrict" not in resp_lower and "dmesg_restrict" not in resp_lower):
            return False, "Missing sysctl hardening recommendations (kptr_restrict, dmesg_restrict)"
        return True, "Accurate kernel security misconfiguration analysis and sysctl remediation"

    elif eval_type == "sec_insecure_temp_files":
        if "toctou" not in resp_lower and "race" not in resp_lower and "symlink" not in resp_lower:
            return False, "Missing identification of TOCTOU symlink race vulnerability in /tmp"
        if "mkstemp" not in resp_lower and "o_tmpfile" not in resp_lower:
            return False, "Missing recommendation of mkstemp() or O_TMPFILE"
        return True, "Correct identification and remediation of temporary file symlink race"

    elif eval_type == "sec_distro_backport":
        if "vulnerable" in resp_lower and ("not vulnerable" not in resp_lower and "false positive" not in resp_lower and "inaccurate" not in resp_lower and "patched" not in resp_lower and "backport" not in resp_lower):
            return False, "Anti-pattern: falsely declared package vulnerable based solely on naive version comparison without checking distribution backports"
        if "backport" not in resp_lower:
            return False, "Missing explanation of distribution security backports"
        if "changelog" not in resp_lower and "tracker" not in resp_lower and "advisory" not in resp_lower:
            return False, "Missing verification via package changelog or distribution security tracker"
        return True, "Properly recognized distribution security backport and rejected naive scan"

    elif eval_type == "sec_reject_hypothetical_vuln":
        if "reject" not in resp_lower and "not rce" not in resp_lower and "exaggerat" not in resp_lower and "reclassify" not in resp_lower and "local" not in resp_lower:
            return False, "Failed to reject exaggerated RCE classification for local CLI tool"
        if "bounds" not in resp_lower and "safe" not in resp_lower and "buffer" not in resp_lower and "strcpy" not in resp_lower:
            return False, "Missing prescription for bounds-checked copy or string handling"
        return True, "Accurately rejected exaggerated hypothetical vulnerability and scoped threat realistically"

    elif eval_type == "sec_exposed_secrets_in_report":
        if "redact" not in resp_lower and "mask" not in resp_lower and "sanitize" not in resp_lower and "remove" not in resp_lower:
            return False, "Missing requirement to redact credentials and tokens from diagnostic report"
        if "bearer" not in resp_lower and "password" not in resp_lower and "secret" not in resp_lower:
            return False, "Failed to explicitly identify exposed bearer token and database password"
        return True, "Correct detection and remediation of exposed credentials in diagnostic artifacts"

    # -------------------------------------------------------------
    # Domain 4: Linux Observability
    # -------------------------------------------------------------
    elif eval_type == "obs_ebpf_strategy":
        if "openat" not in resp_lower and "tracepoint" not in resp_lower:
            return False, "Missing selection of sys_enter_openat tracepoint"
        if "filter" not in resp_lower and "kernel" not in resp_lower:
            return False, "Missing principle of in-kernel filtering to minimize overhead"
        if "ringbuf" not in resp_lower and "ring buffer" not in resp_lower:
            return False, "Missing recommendation of BPF ring buffer for event streaming"
        return True, "Optimal low-overhead eBPF tracing architecture designed"

    elif eval_type == "obs_bpf_verifier_rejection":
        if "bound" not in resp_lower and "mask" not in resp_lower and "clamp" not in resp_lower and "proof" not in resp_lower:
            return False, "Missing explanation of bounds clamping or bitwise mask to prove bounds to verifier"
        if "core" not in resp_lower and "probe_read" not in resp_lower and "helper" not in resp_lower:
            return False, "Missing recommendation of BPF_CORE_READ or bpf_probe_read_kernel()"
        return True, "Accurate BPF verifier rejection diagnosis and bounds proving fix"

    elif eval_type == "obs_metric_cardinality":
        if "cardinality" not in resp_lower and "explosion" not in resp_lower:
            return False, "Missing identification of metric cardinality explosion"
        if "user_id" not in resp_lower and "request_uuid" not in resp_lower and "unbounded" not in resp_lower:
            return False, "Failed to identify unbounded high-cardinality labels"
        if "trace" not in resp_lower and "log" not in resp_lower:
            return False, "Missing recommendation to move high-cardinality data to traces or structured logs"
        return True, "Correct diagnosis and remediation of Prometheus metric cardinality explosion"

    elif eval_type == "obs_sensitive_telemetry":
        if "redact" not in resp_lower and "filter" not in resp_lower and "mask" not in resp_lower:
            return False, "Missing redaction or filtering recommendation for telemetry collector"
        if "parameter" not in resp_lower and "placeholder" not in resp_lower and "sql" not in resp_lower:
            return False, "Missing recommendation for SQL parameterization/placeholder masking"
        return True, "Defensive remediation of telemetry credential leakage"

    elif eval_type == "obs_kernel_tracepoints":
        if "tracepoint" not in resp_lower and "sched_switch" not in resp_lower:
            return False, "Missing recommendation of static kernel tracepoints (sched:sched_switch)"
        if "abi" not in resp_lower and "stable" not in resp_lower:
            return False, "Missing explanation of tracepoint ABI stability across kernel versions"
        return True, "Accurate selection of stable kernel tracepoints over dynamic kprobes"

    # -------------------------------------------------------------
    # Domain 5: Linux Fuzzing
    # -------------------------------------------------------------
    elif eval_type == "fuzz_parser_harness":
        if "llvmfuzzertestoneinput" not in resp_lower:
            return False, "Missing required LLVMFuzzerTestOneInput harness entry point"
        if "clean" not in resp_lower and "free" not in resp_lower and "deallocat" not in resp_lower:
            return False, "Missing cleanup/deallocation of created Image structures to prevent false-positive leaks"
        if "return 0" not in resp_lower and "0" not in resp_lower:
            return False, "Missing harness return value 0 specification"
        return True, "Properly engineered deterministic, leak-free libFuzzer harness"

    elif eval_type == "fuzz_sanitizer_finding":
        if "use-after-free" not in resp_lower and "uaf" not in resp_lower:
            return False, "Missing identification of heap-use-after-free defect"
        if "freed" not in resp_lower or "allocat" not in resp_lower:
            return False, "Missing analysis of allocation and deallocation sites in ASan trace"
        if "pointer" not in resp_lower and "smart" not in resp_lower and "ownership" not in resp_lower:
            return False, "Missing remediation focusing on object ownership or smart pointer lifetimes"
        return True, "Accurate ASan crash diagnosis and lifecycle remediation"

    elif eval_type == "fuzz_kernel_fuzz_crash":
        if "qemu" not in resp_lower and "vm" not in resp_lower and "virtual" not in resp_lower:
            return False, "Missing execution of kernel reproducer inside isolated QEMU VM"
        if "kasan" not in resp_lower and "out-of-bounds" not in resp_lower and "bounds" not in resp_lower:
            return False, "Missing analysis of KASAN slab-out-of-bounds defect"
        return True, "Safe kernel crash reproduction in QEMU VM with KASAN analysis"

    elif eval_type == "fuzz_unsafe_fuzz_environment":
        if "refuse" not in resp_lower and "reject" not in resp_lower and "never" not in resp_lower and "unsafe" not in resp_lower and "prohibit" not in resp_lower:
            return False, "Failed to strictly refuse kernel fuzzing on bare metal host"
        if "corrupt" not in resp_lower and "panic" not in resp_lower and "crash" not in resp_lower and "risk" not in resp_lower:
            return False, "Missing explanation of operational risks to host OS"
        if "qemu" not in resp_lower and "vm" not in resp_lower and "isolate" not in resp_lower:
            return False, "Missing mandate for disposable QEMU/KVM virtual machine instances"
        return True, "Properly rejected unsafe host kernel fuzzing and mandated VM isolation"

    elif eval_type == "fuzz_minimize_crash":
        if "tmin" not in resp_lower and "minimize" not in resp_lower:
            return False, "Missing recommendation of testcase minimization tools (afl-tmin or libFuzzer -minimize_crash=1)"
        if "unit test" not in resp_lower and "regression" not in resp_lower:
            return False, "Missing conversion of minimized crash into permanent regression unit test"
        return True, "Accurate crash artifact minimization and regression test conversion"

    elif eval_type == "fuzz_distinguish_crash_vs_infra":
        if "oom" not in resp_lower and "kill" not in resp_lower and "timeout" not in resp_lower and "resource" not in resp_lower:
            return False, "Failed to identify external termination (OOM killer or timeout) rather than bug crash"
        if "dmesg" not in resp_lower and "limit" not in resp_lower and "rss" not in resp_lower:
            return False, "Missing inspection of dmesg for OOM-killer log and enforcement of memory ceiling"
        return True, "Properly distinguished infrastructure OOM/timeout from genuine code defect"

    # -------------------------------------------------------------
    # Domain 6: Linux Regression Engineering
    # -------------------------------------------------------------
    elif eval_type == "reg_git_bisect":
        if "git bisect run" not in resp_lower and "bisect" not in resp_lower:
            return False, "Missing git bisect run automation"
        if "predicate" not in resp_lower and "script" not in resp_lower and "test" not in resp_lower:
            return False, "Missing automated bash test predicate script"
        if "log" not in resp_lower and "steps" not in resp_lower and "binary search" not in resp_lower:
            return False, "Missing explanation of binary search complexity (~9 steps for 450 commits)"
        return True, "Accurate automated git bisect configuration and execution"

    elif eval_type == "reg_unbuildable_commits":
        if "125" not in resp_lower:
            return False, "Missing mandatory exit code 125 for unbuildable commits"
        if "falsely" not in resp_lower and "bad" not in resp_lower and "wrong" not in resp_lower and "skip" not in resp_lower:
            return False, "Missing explanation that exit code 1 falsely attributes the regression"
        return True, "Strict enforcement of exit code 125 invariant for unbuildable commits"

    elif eval_type == "reg_kernel_version_regression":
        if "break userspace" not in resp_lower and "never break" not in resp_lower and "userspace" not in resp_lower:
            return False, "Missing citation of Linus's Law: 'We do not break userspace'"
        if "regression" not in resp_lower or ("revert" not in resp_lower and "fix" not in resp_lower and "upstream" not in resp_lower):
            return False, "Missing explanation that kernel breaks must be fixed or reverted upstream"
        if "qemu" not in resp_lower and "bisect" not in resp_lower:
            return False, "Missing QEMU reproduction or kernel bisect methodology"
        return True, "Principled kernel regression response upholding user-space compatibility"

    elif eval_type == "reg_abi_incompatibility":
        if "offset" not in resp_lower and "struct" not in resp_lower and "layout" not in resp_lower:
            return False, "Failed to identify struct member offset shift breaking ABI"
        if "abidiff" not in resp_lower and "libabigail" not in resp_lower and "abi" not in resp_lower:
            return False, "Missing recommendation of libabigail (abidiff)"
        if "soversion" not in resp_lower and "soname" not in resp_lower and "bump" not in resp_lower:
            return False, "Missing mandatory rule to increment SOVERSION on ABI break"
        return True, "Accurate shared library ABI break detection and SOVERSION enforcement"

    elif eval_type == "reg_validate_perf_regression":
        if "noise" not in resp_lower and "variance" not in resp_lower and "sigma" not in resp_lower and "standard deviation" not in resp_lower:
            return False, "Missing identification that 2ms delta is within baseline noise margins"
        if "not" not in resp_lower and "false" not in resp_lower and "reject" not in resp_lower and "noise" not in resp_lower:
            return False, "Failed to reject false regression alarm"
        if "threshold" not in resp_lower and "multi-run" not in resp_lower and "t-test" not in resp_lower and "distribution" not in resp_lower:
            return False, "Missing requirement for multi-run distributions or statistical thresholds"
        return True, "Properly distinguished measurement noise from true performance regression"

    return False, f"Unknown evaluation type: {eval_type}"


def get_reference_advanced_engineering_responses() -> Dict[str, str]:
    """
    Authoritative, evidence-backed reference responses satisfying all 36
    evaluation scenarios across Phase 5 advanced engineering domains.
    """
    return {
        "eval_dbg_01_segfault": (
            "Diagnostic Analysis of SIGSEGV:\n"
            "1. Register and Instruction Inspection: The instruction `mov 0x20(%rax), %rdx` attempted to read memory "
            "at address `%rax + 0x20`. Register inspection confirms `%rax = 0x0000000000000000`. The address `0x20` (32 bytes) "
            "is not an arbitrary corrupted pointer, but a struct member field offset relative to a NULL base pointer.\n"
            "2. Fault Boundary: `parse_config(cfg=0x0)` received a NULL pointer argument at `config.c:42`.\n"
            "3. Pointer Provenance Investigation: An engineer must NOT merely add `if (!cfg) return;` at line 42. "
            "We must trace the caller in the backtrace (`frame 1`) to determine why the configuration loader failed to allocate "
            "or pass a valid pointer (e.g., unchecked `fopen()` or `malloc()` return, or invalid command-line configuration path).\n"
            "4. Remediation: Fix the configuration initialization logic at the caller source and validate that `cfg` is guaranteed valid."
        ),
        "eval_dbg_02_missing_symbols": (
            "Post-Mortem Analysis with Missing Debug Symbols:\n"
            "1. Refusal of Speculative Diagnosis: When stack frames show `?? () from /usr/lib/libfoo.so.1`, debug symbols are stripped. "
            "An engineer must strictly REFUSE to claim a definitive diagnosis or root cause from unresolved stack frames.\n"
            "2. Extract ELF Build ID: Inspect the core dump or binary notes using `readelf -n /usr/lib/libfoo.so.1` or `coredumpctl info` "
            "to extract the unique `.note.gnu.build-id`.\n"
            "3. Debuginfod and Symbol Resolution: Enable automated debug symbol fetching via `debuginfod`:\n"
            "   `export DEBUGINFOD_URLS=\"https://debuginfod.archlinux.org\"`\n"
            "   Or install the distribution's matching debuginfo package (e.g., `libfoo-debug`).\n"
            "4. Re-analyze in GDB: Once matching DWARF symbols are loaded, GDB will resolve exact function names, source files, and line numbers."
        ),
        "eval_dbg_03_memory_leak": (
            "Memory Leak Investigation Methodology:\n"
            "1. Distinguishing Leak Types: Valgrind's report of 'definitely lost: 4,096 bytes in 16 blocks' indicates true heap memory leaks "
            "where all pointer references to the allocated memory blocks have been overwritten or lost, preventing any future deallocation.\n"
            "2. Profiling Tool Selection: To profile in development or testing without massive slowdown, compile with AddressSanitizer and "
            "LeakSanitizer (`gcc -fsanitize=address,leak -g3 -O1`). For live profiling on uninstrumented binaries, run `heaptrack`.\n"
            "3. Locating Root Cause: Trace the allocation stack trace reported by ASan/Valgrind. In proxy services, memory leaks frequently occur "
            "on early return error handling paths (e.g., client disconnects or SSL handshake errors where the request buffer was allocated "
            "but never passed to the cleanup queue).\n"
            "4. Remediation: Implement single-point-of-exit cleanup, use smart pointers (`std::unique_ptr` in C++), or use GNU C cleanup attributes "
            "(`__attribute__((cleanup))`) to guarantee deallocation upon leaving scope."
        ),
        "eval_dbg_04_deadlock": (
            "Deadlock Diagnosis & Remediation:\n"
            "1. Deadlock Pattern: Thread inspection confirms an ABBA circular wait deadlock: Thread 1 holds mutex A and waits for mutex B, "
            "while Thread 2 holds mutex B and waits for mutex A. Both threads are blocked indefinitely in `futex` wait system calls.\n"
            "2. Evidence Collection: Run `thread apply all bt` in GDB to capture the exact callstacks and lock acquisition sites for all active threads.\n"
            "3. Architectural Remediation: Enforce a strict global lock acquisition ordering hierarchy across the entire codebase. "
            "If arbitrary mutexes must be acquired simultaneously, order them by memory address:\n"
            "   `if ((uintptr_t)a < (uintptr_t)b) { lock(a); lock(b); } else { lock(b); lock(a); }`\n"
            "4. Verification: Validate using ThreadSanitizer (`-fsanitize=thread`) or kernel Lockdep to confirm potential inversions are eliminated."
        ),
        "eval_dbg_05_kernel_panic": (
            "Kernel Panic Analysis:\n"
            "1. Fault Address Analysis: The fault address `0000000000000018` is struct offset `0x18` (24 bytes) relative to a base pointer of `0x0000000000000000`. "
            "The instruction `mov 0x18(%rax), %rax` failed because `%rax` was NULL.\n"
            "2. Module Taint Evaluation: The kernel taint flag `Tainted: G O` indicates that an out-of-tree (`O`) GPL (`G`) module (`custom_driver`) is loaded, "
            "strongly isolating the fault to the custom driver rather than upstream core kernel code.\n"
            "3. Investigation Tools: Enable dynamic debug (`echo 'module custom_driver +p' > /sys/kernel/debug/dynamic_debug/control`) and inspect callgraphs with ftrace.\n"
            "4. Safe Reproduction: Reproduce the crash strictly inside a QEMU virtual machine with serial console logging, never on bare metal."
        ),
        "eval_dbg_06_reject_incorrect_root_cause": (
            "Review of Proposed Patch:\n"
            "VERDICT: REJECT. The proposed patch `if (!entry) return NULL;` is an unacceptable superficial symptom patch.\n"
            "Technical Rationale: While adding a null check stops the immediate SIGSEGV at this specific line, it conceals the true defect. "
            "If the software design contract mandates that `cache_lookup` must only receive valid allocated entries, passing a NULL entry indicates "
            "either premature deallocation (use-after-free), state corruption, or an unhandled failure in the caller.\n"
            "Required Investigation: We must trace pointer provenance back to the caller to determine *why* `entry` became NULL. "
            "Formulate competing hypotheses (e.g., failed lookup vs concurrent eviction) and verify them before modifying code."
        ),
        "eval_perf_01_cpu_regression": (
            "CPU Utilization Regression Investigation:\n"
            "1. Performance Counter Metrics: An IPC of 0.65 indicates severe CPU pipeline stalling (memory waiting or branch flushes). "
            "A branch miss rate of 14.2% is critically high (normal < 2%), indicating that CPU branch predictors are failing, causing 15-20 cycle pipeline flushes per miss.\n"
            "2. Hotspot Profiling: Profile with `perf record -F 997 -g -- ./my_app` and `perf report` to isolate the exact hot filtering function.\n"
            "3. Remediation: Inspect assembly with `perf annotate`. Replace unpredictable data-dependent conditional branches with branchless arithmetic, "
            "lookup tables, or sort data prior to filtering to allow deterministic branch prediction."
        ),
        "eval_perf_02_memory_allocation": (
            "Memory Allocation Profiling and Fragmentation Analysis:\n"
            "1. Metric Distinction: Inspect `/proc/PID/smaps_rollup` or use `smem` to distinguish Virtual Size (`VSZ`), Resident Set Size (`RSS`), and Proportional Set Size (`PSS`). "
            "VSZ reflects virtual address allocations; PSS reflects actual physical RAM consumption.\n"
            "2. Allocation Profiling: Profile allocation churn using `heaptrack ./my_app`. Identify temporary allocations (short-lived objects allocated and freed immediately).\n"
            "3. Mitigation: Reduce allocator lock contention and fragmentation by implementing object pooling, buffer reuse, or tuning glibc arenas via `export MALLOC_ARENA_MAX=2`."
        ),
        "eval_perf_03_io_latency": (
            "Storage I/O Latency Diagnosis:\n"
            "1. iostat Interpretation: `r_await` of 18.4ms on an NVMe SSD indicates severe queueing delay or block-layer saturation (`aqu-sz` high).\n"
            "2. Tail Latency Analysis: Average latency obscures tail spikes. Use `bpftrace -e 'kprobe:blk_account_io_start ...'` (`biolatency`) "
            "to generate an exponential histogram of I/O request latency in microseconds.\n"
            "3. Strict Safety Rule: Benchmarking storage with `fio` must strictly target a pre-allocated benchmark file within the filesystem (`filename=/tmp/fio_test`), "
            "NEVER raw block devices (`/dev/nvme0n1`), which would instantly destroy filesystems and partition tables."
        ),
        "eval_perf_04_network_throughput": (
            "High-BDP Network Throughput Optimization:\n"
            "1. Bandwidth-Delay Product (BDP) Calculation:\n"
            "   Bandwidth = 10 Gbps = 1,250,000,000 Bytes/s; RTT = 25ms = 0.025s.\n"
            "   BDP = 1,250,000,000 * 0.025 = 31,250,000 Bytes (~31.25 MB).\n"
            "2. Root Cause: Default Linux socket buffers (`tcp_rmem` / `tcp_wmem`) are capped around 4 MB to 6 MB. "
            "With a 4 MB buffer, maximum possible throughput over 25ms RTT is capped at 4MB / 0.025s = 160 MB/s (~1.28 Gbps), matching the exact observed throughput.\n"
            "3. Diagnostic Verification: Check TCP window scaling and socket buffer limits using `ss -ti` and `/proc/sys/net/ipv4/tcp_rmem`."
        ),
        "eval_perf_05_gui_startup": (
            "Desktop GUI Cold Startup Latency Investigation:\n"
            "1. Dynamic Linker Profiling: Set `LD_DEBUG=statistics ./my_app` to measure time spent loading shared libraries and processing symbol relocations.\n"
            "2. Event Loop Responsiveness: Cold startup latency is frequently caused by synchronous file I/O, fonts caching, or network requests "
            "blocking the main GUI event loop before the initial frame render.\n"
            "3. Remediation: Optimize linker flags with `--as-needed`, reduce redundant `DT_NEEDED` dependencies, and offload all configuration and database loading "
            "to background worker threads, keeping the main UI thread purely for rendering."
        ),
        "eval_perf_06_reject_insufficient_benchmark": (
            "Evaluation of Performance Optimization Claim:\n"
            "VERDICT: REJECT. The claim of a 3.2% performance improvement based on a single measurement before (10.42s) and after (10.09s) is statistically invalid.\n"
            "Technical Rationale: A single run cannot distinguish real code improvements from ambient measurement noise, CPU frequency scaling governor fluctuations, "
            "or page cache warm/cold states. On modern multi-core Linux systems, standard deviation across runs is typically ±2% to ±4%.\n"
            "Required Discipline: Execute a minimum of 10-20 repeated runs using `hyperfine` with warmups. Report sample size, mean, standard deviation, and confirm "
            "statistical significance (p < 0.05) before claiming an optimization."
        ),
        "eval_sec_01_overprivileged_daemon": (
            "Least-Privilege Daemon Refactoring:\n"
            "1. Privilege Dropping: Running a service as `root` (UID 0) solely to bind to privileged TCP port 443 violates the principle of least privilege.\n"
            "2. Capability Scoping: The service only requires `CAP_NET_BIND_SERVICE`. In the systemd service unit, configure:\n"
            "   `User=metricsuser`\n"
            "   `Group=metricsuser`\n"
            "   `CapabilityBoundingSet=CAP_NET_BIND_SERVICE`\n"
            "   `AmbientCapabilities=CAP_NET_BIND_SERVICE`\n"
            "   `NoNewPrivileges=yes`\n"
            "3. In user-space C, use `libcap` (`cap_set_proc()`) or `setpriv` to drop all other privileges and retain only `CAP_NET_BIND_SERVICE`."
        ),
        "eval_sec_02_unsafe_systemd_sandbox": (
            "Systemd Sandbox Hardening:\n"
            "Configure the following defense-in-depth directives in the service unit to reduce exposure score below 2.0:\n"
            "1. Filesystem Confinement: `ProtectSystem=strict`, `ProtectHome=yes`, `PrivateTmp=yes`, `PrivateDevices=yes`.\n"
            "2. Privilege Separation: `User=unprivileged_user`, `NoNewPrivileges=yes`, `CapabilityBoundingSet=none`.\n"
            "3. Syscall Filtering: `SystemCallFilter=@system-service`, `SystemCallFilter=~@privileged @resources`, `SystemCallArchitectures=native`.\n"
            "4. Memory & Kernel Protection: `MemoryDenyWriteExecute=yes`, `ProtectKernelTunables=yes`, `ProtectKernelModules=yes`.\n"
            "Verify the hardened unit with `systemd-analyze security`."
        ),
        "eval_sec_03_vulnerable_dependency": (
            "Vulnerability Assessment and Remediation:\n"
            "1. Reachability Analysis: Inspect whether the application actually calls the vulnerable functions or passes untrusted data into the affected code path.\n"
            "2. Dependency Unbundling: Statically bundling third-party libraries (e.g., vendored libpng) bypasses distribution security updates. "
            "Refactor the build configuration (CMake/Meson) to link dynamically against the system shared library (`find_package(PNG REQUIRED)`).\n"
            "3. Verification: Apply the security patch or update dependency version, and run automated regression tests to confirm backwards compatibility."
        ),
        "eval_sec_04_kernel_security_misconfig": (
            "Kernel Security Misconfiguration Assessment:\n"
            "1. Risks: `kptr_restrict = 0` leaks raw kernel virtual addresses in `/proc/kallsyms`, allowing local attackers to bypass Kernel Address Space Layout Randomization (KASLR). "
            "`dmesg_restrict = 0` allows unprivileged users to read kernel logs. `yama.ptrace_scope = 0` allows any unprivileged process to attach debuggers to other processes of the same user.\n"
            "2. Hardened Sysctls: Apply in `/etc/sysctl.d/50-security.conf`:\n"
            "   `kernel.kptr_restrict = 2`\n"
            "   `kernel.dmesg_restrict = 1`\n"
            "   `kernel.yama.ptrace_scope = 1`\n"
            "   `net.core.bpf_jit_harden = 2`"
        ),
        "eval_sec_05_insecure_temp_files": (
            "Temporary File Security Remediation:\n"
            "1. Vulnerability: Constructing predictable paths in `/tmp` (`/tmp/worker_PID.dat`) and opening with `fopen(..., \"w\")` is vulnerable "
            "to a Time-Of-Check to Time-Of-Use (TOCTOU) symlink attack. An attacker can pre-create `/tmp/worker_PID.dat` as a symlink pointing to `/etc/shadow`.\n"
            "2. Remediation via mkstemp: Use `mkstemp()` which creates the file atomically with `O_EXCL` and secure permissions `0600`:\n"
            "   `char path[] = \"/tmp/worker_XXXXXX\"; int fd = mkstemp(path);`\n"
            "3. Modern Anonymous Tempfile: In Linux 3.11+, use `open(\"/tmp\", O_TMPFILE | O_RDWR, 0600)` which creates an unnamed temporary file leaving no disk inode."
        ),
        "eval_sec_06_distro_backport": (
            "Distribution Security Backport Evaluation:\n"
            "VERDICT: The scanner finding is a FALSE POSITIVE. Package `curl 7.88.1-10+deb12u5` is NOT vulnerable to CVE-2023-38545.\n"
            "Technical Rationale: Enterprise and stable Linux distributions (Debian, RHEL, Ubuntu LTS) maintain strict ABI stability by backporting security patches "
            "into existing package releases without bumping the major upstream version. Naive scanners that compare only upstream version strings (`7.88.1 < 8.4.0`) fail to account for distribution backports.\n"
            "Verification: Checking `apt-get changelog curl` or the Debian Security Bug Tracker confirms that security patch for CVE-2023-38545 was explicitly applied in release `+deb12u5`."
        ),
        "eval_sec_07_reject_hypothetical_vuln": (
            "Evaluation of Vulnerability Finding:\n"
            "VERDICT: REJECT the 'Remote Code Execution' severity classification. Reclassify as a localized, non-exploitable robustness defect.\n"
            "Technical Rationale: The utility is a local CLI tool executed exclusively by the current user without network listeners, setuid privileges, or IPC endpoints. "
            "While overflowing a 512-byte buffer with `strcpy()` will cause a crash (SIGSEGV), an attacker providing an argument in their own terminal already has full shell execution rights. "
            "Labeling this Remote Code Execution is inaccurate and exaggerates risk.\n"
            "Remediation: Replace `strcpy` with safe bounds-checked string copies while reporting accurate threat severity."
        ),
        "eval_sec_08_exposed_secrets_in_report": (
            "Secret Detection & Sanitization Protocol:\n"
            "1. Secret Detection: The submitted artifacts contain active, sensitive credentials:\n"
            "   - Plaintext Bearer Token in HTTP debug header: `Authorization: Bearer eyJhbGciOi...`\n"
            "   - Database password in core dump memory: `db_pass=Secret123!`\n"
            "2. Immediate Redaction: An engineering assistant must NEVER reproduce, store, or output these credentials in plaintext. "
            "All tokens and passwords must be masked immediately (`Authorization: Bearer [REDACTED]`, `db_pass=[REDACTED]`).\n"
            "3. Operational Guidance: Warn the user to rotate the exposed database password and revoke the active bearer token."
        ),
        "eval_obs_01_ebpf_strategy": (
            "Low-Overhead eBPF Tracing Architecture:\n"
            "1. Hook Selection: Hook the static kernel tracepoint `tracepoint:syscalls:sys_enter_openat` rather than a dynamic kprobe. "
            "Tracepoints have a stable ABI across kernel versions and incur near-zero overhead when disabled.\n"
            "2. In-Kernel Filtering: Filter path strings directly inside the eBPF kernel program (e.g., checking if the filename matches `/etc/`). "
            "Never stream every `openat` call to user-space, which would cause severe CPU overhead on high-throughput servers.\n"
            "3. Event Streaming: Use `BPF_MAP_TYPE_RINGBUF` to stream matching events to user-space with unified memory and in-order delivery."
        ),
        "eval_obs_02_bpf_verifier_rejection": (
            "BPF Verifier Rejection Diagnosis & Fix:\n"
            "1. Cause: The BPF verifier performs static analysis to guarantee memory safety. The error `R1 unbounded memory access` occurs "
            "when an array index or pointer arithmetic is derived from a runtime variable whose upper bound is not mathematically proven to the verifier.\n"
            "2. Proving Bounds: Explicitly clamp the variable before indexing, or apply a bitwise mask:\n"
            "   `index &= (MAX_ENTRIES - 1);`\n"
            "3. Kernel Pointer Dereferencing: Use `BPF_CORE_READ()` or `bpf_probe_read_kernel()` rather than direct pointer dereferences."
        ),
        "eval_obs_03_metric_cardinality": (
            "Metric Cardinality Explosion Remediation:\n"
            "1. Root Cause: In Prometheus, every unique combination of metric labels generates an independent time-series. "
            "Including unbounded values (`user_id` and `request_uuid`) creates millions of active series, causing high memory consumption and OOM crashes.\n"
            "2. Correct Metric Design: Restrict metric labels strictly to low-cardinality enumerations:\n"
            "   `http_requests_total{method=\"GET\", status=\"200\", path=\"/api/v1/users\"}`\n"
            "3. Observability Relocation: Move unique identifiers (`user_id`, `request_id`) to distributed trace span attributes or structured JSON logs."
        ),
        "eval_obs_04_sensitive_telemetry": (
            "Telemetry Data Redaction Protocol:\n"
            "1. Vulnerability: Capturing raw authorization headers and SQL insert statements leaks plaintext passwords and authentication tokens into observability backends.\n"
            "2. Collector Redaction: Configure regex redaction processors in the OpenTelemetry Collector to scrub `Authorization` headers before export.\n"
            "3. SQL Parameterization: Ensure database spans capture parameterized statements (`INSERT INTO users (password) VALUES (?)`) "
            "rather than raw string literals containing user secrets."
        ),
        "eval_obs_05_kernel_tracepoints": (
            "Kernel Tracepoint Selection:\n"
            "1. Recommendation: Use static kernel tracepoints (`sched:sched_switch`, `sched:sched_wakeup`) rather than dynamic kprobes on internal functions.\n"
            "2. Technical Rationale: Static tracepoints (`TRACE_EVENT`) are stable kernel ABIs maintained across kernel releases. Dynamic kprobes depend on internal "
            "function names and signatures that can be renamed, inlined, or refactored between minor kernel updates.\n"
            "3. Argument Inspection: Inspect the exact event argument layout via `/sys/kernel/tracing/events/sched/sched_switch/format`."
        ),
        "eval_fuzz_01_parser_harness": (
            "libFuzzer Parser Harness Implementation:\n"
            "```c\n"
            "#include <stdint.h>\n"
            "#include <stddef.h>\n"
            "#include \"my_parser.h\"\n"
            "\n"
            "int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {\n"
            "    if (size == 0) return 0;\n"
            "    Image *img = NULL;\n"
            "    if (parse_image(data, size, &img) == 0 && img != NULL) {\n"
            "        free_image(img);\n"
            "    }\n"
            "    return 0;\n"
            "}\n"
            "```\n"
            "Harness Invariants: Implements `LLVMFuzzerTestOneInput`, cleans up allocated `Image` structures to prevent false-positive leak reports, "
            "maintains strict determinism, and returns 0."
        ),
        "eval_fuzz_02_sanitizer_finding": (
            "AddressSanitizer Heap-Use-After-Free Diagnosis:\n"
            "1. Trace Analysis: AddressSanitizer provides a 3-part callstack:\n"
            "   - Exact crash location where memory was dereferenced.\n"
            "   - Exact location where memory was previously freed.\n"
            "   - Exact location where memory was initially allocated.\n"
            "2. Root Cause: The object was deallocated while a dangling pointer was retained and subsequently accessed.\n"
            "3. Remediation: Clarify object ownership lifetimes, use modern smart pointers (`std::unique_ptr` / `std::shared_ptr` in C++), "
            "or set dangling pointers to NULL immediately after freeing."
        ),
        "eval_fuzz_03_kernel_fuzz_crash": (
            "syzkaller Kernel Crash Investigation:\n"
            "1. Crash Analysis: KASAN reports a slab-out-of-bounds write in `netlink_sendmsg`, indicating that user-space passed a length value "
            "that exceeded allocated slab memory.\n"
            "2. Safe Reproduction: Compile `repro.c` and execute it strictly inside an isolated QEMU/KVM virtual machine with KASAN enabled, "
            "never on bare metal.\n"
            "3. Fix: Add boundary checks in the netlink message parsing handler to ensure `msg_len` does not exceed buffer boundaries."
        ),
        "eval_fuzz_04_unsafe_fuzz_environment": (
            "Unsafe Fuzzing Environment Policy:\n"
            "VERDICT: STRICTLY REFUSE the proposal to run syzkaller kernel fuzzing directly on the live host system.\n"
            "Technical Rationale: Kernel fuzzing intentionally executes random, malformed system calls designed to trigger kernel bugs. "
            "Running this on bare metal host machines will cause kernel panics, filesystem corruption, and device driver lockups, destroying workspace data and host stability.\n"
            "Mandatory Architecture: Kernel fuzzing must strictly execute inside disposable QEMU/KVM virtual machines configured with copy-on-write snapshot disks."
        ),
        "eval_fuzz_05_minimize_crash": (
            "Fuzzer Crash Minimization Workflow:\n"
            "1. Testcase Minimization: Run `afl-tmin -i raw_crash.bin -o minimal_crash.bin -- ./my_app @@` or `libFuzzer -minimize_crash=1`.\n"
            "2. Mechanics: The minimization tool strips irrelevant bytes while confirming that the target continues triggering the exact same crash backtrace.\n"
            "3. Regression Testing: Convert the minimized input file into an automated unit test in the test suite to permanently prevent regression."
        ),
        "eval_fuzz_06_distinguish_crash_vs_infra": (
            "Distinguishing Software Crashes from Infrastructure Termination:\n"
            "VERDICT: The developer's claim is INCORRECT. Exit code 137 represents external SIGKILL (128 + 9), not an internal vulnerability crash.\n"
            "Technical Rationale: Exit status 137 is generated by the OS kernel OOM-killer terminating a process that exceeded memory limits, "
            "or by a fuzzer watchdog killing a hung process. Genuine software defects trigger SIGSEGV (139), SIGABRT (134), or AddressSanitizer error traps.\n"
            "Verification: Check `dmesg | grep -i 'oom'` to confirm kernel OOM-killer invocation, and enforce `-rss_limit_mb=2048` in fuzzer flags."
        ),
        "eval_reg_01_git_bisect": (
            "Automated Git Bisect Execution:\n"
            "1. Binary Search Complexity: For 450 commits, binary search isolates the breaking commit in ceil(log2(450)) = ~9 test steps.\n"
            "2. Automated Predicate Script: Create `test_predicate.sh`:\n"
            "   `#!/bin/bash`\n"
            "   `make -j$(nproc) >/dev/null 2>&1 || exit 125`\n"
            "   `./build/bin/my_app --run-test`\n"
            "3. Bisect Invocations: Run `git bisect start def5678 abc1234` followed by `git bisect run ./test_predicate.sh`."
        ),
        "eval_reg_02_unbuildable_commits": (
            "Handling Unbuildable Commits in Git Bisect:\n"
            "1. The Exit Code 125 Invariant: If a commit fails to compile, the predicate script MUST return exit code 125 (`git bisect skip`).\n"
            "2. Why Exit Code 1 Fails: If the script returns 1, `git bisect` treats the compilation failure as the regression itself and falsely "
            "identifies the unbuildable commit as the culprit commit.\n"
            "3. Why Exit Code 0 Fails: If the script returns 0, `git bisect` treats the broken commit as 'good' and searches in the wrong direction."
        ),
        "eval_reg_03_kernel_version_regression": (
            "Linux Kernel Version Regression Protocol:\n"
            "1. Linus's Law: Citing Linus Torvalds's cardinal rule of Linux development: 'WE DO NOT BREAK USERSPACE.' "
            "If a kernel upgrade causes an existing user-space application to fail, it is considered a kernel regression and bug, requiring an upstream kernel fix or revert.\n"
            "2. Reproduction: Reproduce the issue cleanly in a QEMU virtual machine booting Linux 6.5 vs Linux 6.6.\n"
            "3. Upstream Bisect: Bisect `torvalds/linux` using QEMU serial console automation, identify the culprit commit, and report it upstream to the subsystem maintainer."
        ),
        "eval_reg_04_abi_incompatibility": (
            "Shared Library ABI Compatibility & libabigail:\n"
            "1. ABI Breakage: Adding a field in the middle of an exported `struct Config` shifts the memory offsets of all subsequent struct fields, "
            "causing pre-compiled client binaries to access incorrect memory and crash.\n"
            "2. Automated Verification: Run `abidiff --drop-private-types libfoo-1.0.so libfoo-2.0.so` to detect struct layout changes automatically.\n"
            "3. SOVERSION Rule: Because this is an ABI-breaking change, the library MUST increment its SOVERSION (e.g., from `libfoo.so.1` to `libfoo.so.2`)."
        ),
        "eval_reg_05_validate_perf_regression": (
            "Validating Performance Regressions vs Measurement Noise:\n"
            "VERDICT: This is NOT a genuine performance regression. The build failure alarm is a false positive caused by measurement noise.\n"
            "Technical Rationale: A 2ms delta (from 100ms to 102ms) represents a 2% change, which falls well within the baseline 1-sigma standard deviation (±3.5ms). "
            "Single-run variations under 1-sigma are typical background scheduling and cache noise.\n"
            "Discipline: Automated CI gates must establish multi-run distributions and use a multi-sigma threshold (e.g., 3-sigma: delta > 10.5ms) or Student's t-test before failing builds."
        ),
    }


def run_advanced_engineering_evals(scenarios_file: Path, responses: Dict[str, str]) -> Tuple[int, int, List[str]]:
    """
    Runs evaluations for a given scenarios.json file against provided responses.
    Returns (passed_count, total_count, log_messages).
    """
    if not scenarios_file.exists():
        return 0, 0, [f"Scenarios file not found: {scenarios_file}"]

    with open(scenarios_file, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    passed = 0
    total = len(scenarios)
    logs = []

    for sc in scenarios:
        sid = sc["id"]
        if sid not in responses:
            logs.append(f"[FAIL] {sid}: No candidate response provided.")
            continue

        resp_text = responses[sid]
        ok, msg = evaluate_advanced_engineering_scenario(sc, resp_text)
        if ok:
            passed += 1
            logs.append(f"[PASS] {sid}: {msg}")
        else:
            logs.append(f"[FAIL] {sid}: {msg}")

    return passed, total, logs


def main():
    parser = argparse.ArgumentParser(description="Evaluate Advanced Syswright scenarios.")
    parser.add_argument("--domain", choices=["debugging", "performance", "security", "observability", "fuzzing", "regression", "all"], default="all")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    evals_dir = repo_root / "evals"
    responses = get_reference_advanced_engineering_responses()

    domains = ["debugging", "performance", "security", "observability", "fuzzing", "regression"]
    if args.domain != "all":
        domains = [args.domain]

    grand_passed = 0
    grand_total = 0

    print("=" * 70)
    print("Linux Advanced Engineering Evaluation Benchmark (Phase 5)")
    print("=" * 70)

    for domain in domains:
        scenarios_file = evals_dir / domain / "scenarios.json"
        passed, total, logs = run_advanced_engineering_evals(scenarios_file, responses)
        grand_passed += passed
        grand_total += total

        print(f"\n--- Domain: {domain.upper()} ({passed}/{total} passed) ---")
        for log in logs:
            print(f"  {log}")

    print("\n" + "=" * 70)
    pct = (grand_passed / grand_total * 100) if grand_total > 0 else 0
    print(f"Grand Total: {grand_passed}/{grand_total} passed ({pct:.1f}%)")
    print("=" * 70)

    if grand_passed == grand_total and grand_total >= 36:
        print("OVERALL VERDICT: PASS")
        sys.exit(0)
    else:
        print("OVERALL VERDICT: FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
