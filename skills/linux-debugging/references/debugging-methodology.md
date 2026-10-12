# Systematic Linux Debugging Methodology

A disciplined, evidence-driven approach to diagnosing software and system defects on Linux.

---

## 1. The Core Scientific Debugging Cycle

Debugging is not a trial-and-error guessing game; it is an empirical investigation based on the scientific method:

```
Observed Symptom
       │
       ▼
Formulate Competing Hypotheses
       │
       ▼
Design Discriminating Experiment
       │
       ▼
Execute & Observe Result
       │
       ├─► [Hypothesis Falsified] ──► Formulate New Hypothesis
       │
       └─► [Hypothesis Confirmed] ──► Root Cause Isolated ──► Minimal Fix ──► Regression Test
```

### Critical Distinctions:
- **Symptom**: The observable failure (e.g., HTTP 500 error, SIGSEGV crash, exit status 139, sluggish response).
- **Immediate Mechanism**: The direct trigger of failure (e.g., dereferencing pointer `0x0000000000000028`).
- **Contributing Factor**: Environmental or configuration condition enabling the bug (e.g., memory pressure, high concurrency, unbuffered I/O).
- **Root Cause**: The underlying violation of a software invariant or design contract (e.g., failure to check return value of `realloc()` when resizing dynamic array, or missing lock on shared queue).

---

## 2. The 14-Step Diagnostic Protocol

1. **Understand Reported Symptom**: Capture exact error output, exit codes, and timestamps without speculation.
2. **Identify Affected Component**: Trace process boundaries (client, daemon, helper library, kernel syscall).
3. **Capture Environment Baseline**: Note OS distribution, kernel version (`uname -r`), glibc version, and compiler flags.
4. **Reproduce Defect**: Build a minimal, reproducible example (reproducer script or unit test).
5. **Collect Diagnostic Evidence**: Inspect logs (`journalctl -xe`), core dumps, and syscall traces.
6. **Identify Failure Boundary**: Find exact instruction pointer (`rip`), function symbol, and source file line.
7. **Inspect Source Code**: Read relevant source files, context lines, and type definitions.
8. **Form Competing Hypotheses**: Develop at least two distinct, plausible technical hypotheses.
9. **Test Hypotheses Independently**: Use breakpoints, watchpoints, tracepoints, or print statements to evaluate each hypothesis.
10. **Identify Root Cause**: State why the invariant broke and why previous executions might have succeeded.
11. **Propose Smallest Justified Fix**: Write a patch addressing only the defect, avoiding unrelated reformatting.
12. **Validate Fix**: Prove the reproducer no longer crashes and valid test cases continue passing.
13. **Check for Regressions**: Run test suite, verify ABI/API backwards compatibility, and check static analysis.
14. **Document Remaining Uncertainty**: Explicitly state any unverified edge cases or hardware-specific behaviors.

---

## 3. Premature Conclusion Anti-Patterns

| Anti-Pattern | Description | Engineering Remedy |
|---|---|---|
| **Symptom Patching** | Adding a `NULL` check before a crash without understanding why the pointer was `NULL`. | Trace pointer provenance backwards to find where valid initialization or assignment failed. |
| **Shotgun Debugging** | Randomly changing code, adding sleeps, or reordering statements hoping it stops failing. | Stop and establish an observable hypothesis before changing a single line of code. |
| **Silent Swallowing** | Wrapping problematic calls in `try/catch` or ignoring return codes. | Handle errors explicitly; log diagnostics with failure context or fail fast. |
| **Blaming the Tool** | Assuming the compiler, kernel, or OS has a bug before thoroughly inspecting application logic. | Statistically, >99.9% of defects reside in application code or misuse of platform contracts. |

---

## 4. Structured Debugging Report Template

Every formal diagnostic report must follow this structure:

```markdown
### 1. Problem Statement
- Component: [Name and version]
- Observed Symptom: [Exact error message, signal, or behavior]

### 2. Environment & Reproduction
- Environment: [OS, Kernel, Architecture, Compiler]
- Reproduction Command: [Exact CLI command or script]

### 3. Diagnostic Evidence
- Backtrace / Syscall Log: [GDB bt full or strace excerpt]
- Failure Location: [File:Line, function, instruction pointer]

### 4. Competing Hypotheses & Evaluation
- Hypothesis A: [Mechanism] -> [Falsified: Evidence]
- Hypothesis B: [Mechanism] -> [Confirmed: Evidence]

### 5. Root Cause Analysis
- Invariant Violated: [Description of broken contract]
- Root Cause: [Underlying explanation]

### 6. Remediation & Verification
- Patch: [Minimal diff]
- Verification Result: [Reproducer execution output confirming fix]
- Remaining Uncertainty: [Any edge cases or untested platforms]
```
