# Syswright: Persistent Repository Guidance for AI Agents

Welcome to **Syswright**. When working inside this repository, you must adhere to the core engineering philosophy:
> **Research before implementation. Evidence before assumptions. Verification before completion.**

---

## 1. Non-Negotiable Invariants

1. **Ground Before Mutating**: Always inspect existing code, directory structures, and git history before proposing or executing changes. Never guess file contents or API contracts.
2. **Stay in Declared Scope**: Modify only the specific files required for the task. Do not touch unrelated files or reformat working code.
3. **Completion Needs Observable Evidence**: Never declare a task complete based on conversational self-review. Run the relevant test suite, compiler, or validator and cite the exact command output.
4. **Safety Tier Enforcement**:
   - Tier 0 (Diagnostics) and Tier 1 (Workspace builds) may run automatically.
   - Tier 3 operations (`sudo`, package installations on host, bootloader edits, kernel module loading) **strictly require explicit human authorization**. Never run `sudo` autonomously.
5. **Report Actual Test Outcomes**: If a test or validation check fails, report the failing output honestly. Never suppress or explain away test failures.

---

## 2. Mandatory Workflow Sequence

Whenever assigned a task in this repository:
1. **Read Architecture & Decisions**: Consult `docs/architecture/` and relevant Phase 0 records before architectural changes.
2. **Research Authoritative Sources**: Query official upstream documentation (kernel.org, freedesktop.org, POSIX) following [references/source-authority.md](references/source-authority.md).
3. **Follow Dependency Discipline**: Avoid adding third-party dependencies or external Python libraries. Use the Python 3 standard library.
4. **Validate Skills & References**: After editing skills or documentation, execute:
   ```bash
   python3 scripts/validate-skills.py
   python3 scripts/check-references.py
   ```
5. **Run the Full Test Suite**:
   ```bash
   python3 tests/run_all_tests.py
   ```
6. **Inspect Git Diffs**: Run `git diff` to ensure zero unintended whitespace, debugging statements, or extraneous files were touched.

---

## 3. Foundation Skills Overview

- **`linux-engineer`** (`skills/linux-engineer/`): Primary orchestrator and router for all Linux engineering requests.
- **`linux-research`** (`skills/linux-research/`): 10-step upstream investigation and evidence engine.
- **`linux-environment`** (`skills/linux-environment/`): Safe, unprivileged host and target reconnaissance.
