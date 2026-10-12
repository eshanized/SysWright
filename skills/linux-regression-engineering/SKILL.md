---
name: linux-regression-engineering
description: Linux regression investigation, isolation, and prevention specialist. Establishes automated predicates for git bisect, isolates unbuildable commits (exit code 125), investigates Linux kernel version regressions, detects shared library ABI/API breaks (libabigail), diagnoses performance regressions, and constructs regression test suites.
license: Apache-2.0
compatibility: Requires Linux environment, git, and build toolchains.
metadata:
  author: Linux Engineering Contributors
  version: "0.1.0"
---

# Linux Regression Engineering Specialist

The `linux-regression-engineering` skill guides AI agents through identifying, isolating, and preventing regressions across Linux kernel patches, drivers, system services, native applications, and shared libraries.

---

## 1. Regression Engineering Workflow

```mermaid
flowchart TD
    REPORT["1. Regression Intake\n(Previously working, now failing)"] --> BASE["2. Define Baseline Good & Bad Revisions"]
    BASE --> TEST["3. Author Automated Test Predicate Script\n(0 = good, 1 = bad, 125 = skip unbuildable)"]
    TEST --> BISECT["4. Execute Automated Git Bisect\n(git bisect run ./predicate.sh)"]
    BISECT --> CULPRIT["5. Isolate Culprit Commit\n(Commit SHA, Author, Diff)"]
    CULPRIT --> ROOT["6. Root Cause Analysis\n(Why did this specific change break contract?)"]
    ROOT --> FIX["7. Formulate Surgical Fix or Revert"]
    FIX --> PREVENT["8. Regression Prevention\n(Commit permanent regression test fixture)"]
```

### The 8-Step Regression Isolation Process:
1. **Define Baseline State**: Establish known good commit/version and known bad commit/version.
2. **Confirm Clean Reproducibility**: Verify failure is deterministic rather than a flaky test or timing race.
3. **Write Automated Predicate**: Create a standalone bash script that builds the commit and evaluates the behavior.
4. **Handle Build Failures Correctly**: Crucial invariant: if a commit fails to compile during bisect, return exit code 125 (`git bisect skip`), NEVER return 1 (which falsely flags it as bad) or 0 (which falsely flags it as good).
5. **Execute Binary Search**: Run `git bisect run ./predicate.sh` to isolate the culprit commit in $O(\log N)$ steps.
6. **Analyze Culprit Diff**: Inspect commit message and exact code delta to understand intended vs accidental side-effects.
7. **Remediate**: Propose a targeted patch or revert that restores compatibility.
8. **Lock In Prevention**: Add permanent regression test cases to the project test suite.

---

## 2. Regression Classification Matrix

| Regression Class | Primary Symptoms | Diagnostic & Isolation Tool |
|---|---|---|
| **Functional Logic** | Feature previously worked; now returns incorrect data or error | `git bisect`, unit tests, minimal reproducers |
| **Crash / Panic** | Previously stable code crashes with SIGSEGV or kernel panic | `git bisect`, GDB core analysis, KASAN |
| **Performance** | Throughput dropped by >10% or latency spiked | `hyperfine`, `perf stat`, benchmark history |
| **ABI / API Incompatibility** | Existing client binaries fail to run with dynamic linker error | `abidiff` (libabigail), `readelf` |
| **Kernel Subsystem** | Hardware driver fails to probe or suspend/resume breaks across kernel update | QEMU kernel bisect, `git bisect` on torvalds/linux |

---

## 3. Operational Safety Boundaries

- **Tier 0 (Diagnostics)**: Running `git log`, `git blame`, inspecting diffs, and checking ABI with `abidiff` is fully autonomous.
- **Tier 1 (Workspace Builds)**: Running automated bisect scripts in workspace copies or git worktrees runs autonomously.
- **Tier 3 (Host Mutating / Privileged)**: Replacing running host kernel packages or host glibc to test regressions requires explicit human authorization. Use isolated VMs or chroots for regression verification.

---

## 4. Reference Library

- [regression-methodology.md](references/regression-methodology.md) — Defining regressions, establishing baselines, and isolating causes.
- [git-bisect.md](references/git-bisect.md) — Automated predicates, handling unbuildable commits (125), and worktrees.
- [kernel-regressions.md](references/kernel-regressions.md) — Bisecting the Linux kernel, QEMU boot testing, and Linus's "Never break userspace" rule.
- [application-regressions.md](references/application-regressions.md) — Behavioral regressions, configuration migration, and unit test preservation.
- [performance-regressions.md](references/performance-regressions.md) — Statistical regression thresholds, noise handling, and automated benchmark gates.
- [abi-compatibility.md](references/abi-compatibility.md) — Shared library ABI stability, SONAME rules, vtables, and libabigail (`abidiff`).
- [regression-prevention.md](references/regression-prevention.md) — Golden test fixtures, CI regression matrices, and regression corpora.
