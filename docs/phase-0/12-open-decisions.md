# Open Decisions, Licensing & Technical Uncertainties: Syswright

## 1. Governance & Purpose

This document formally records all unresolved architectural questions, licensing evaluations, technical uncertainties, and operational trade-offs identified during **Phase 0**.

In accordance with Phase 0 directives, **no final decision on these items has been unilaterally implemented**. These items are documented with detailed trade-off analyses and recommendations for the **Project Owner's explicit review and approval** prior to initiating Phase 1.

---

## 2. Decision Record 1: Project Licensing Model

### 2.1 The Problem
Syswright produces both **executable code** (Python generators, verification scripts, evaluation harnesses) and **extensive engineering knowledge** (Agent Skills, technical references, architecture guides). We must select a license that maximizes open-source adoption, protects contributors with patent grants, and respects third-party intellectual property.

### 2.2 Comparison of Licensing Options

| License Option | Permissiveness | Patent Protection | Commercial Redistribution | Documentation Fit | Notes / Compatibility |
|:---|:---:|:---:|:---:|:---:|:---|
| **Option A: MIT License** | Maximum | None (Silent on patents) | Allowed | Acceptable | Highly recognizable; used by many agent skill repos. Lacks express patent retaliation. |
| **Option B: Apache-2.0** | High | **Express Grant & Retaliation** | Allowed | Excellent | Section 3 provides robust patent protection. Standard for Linux Foundation & modern systems projects. |
| **Option C: Dual License**<br>(Apache-2.0 + CC-BY-4.0) | High | Robust on Code | Allowed with attribution | Optimal | Apache-2.0 covers `scripts/`, `evals/`, `tests/`; CC-BY-4.0 covers `skills/`, `references/`, `docs/`. |
| **Option D: GPL-2.0 / GPL-3.0** | Copyleft | Mixed | Restrictive | Complex | Standard in Linux kernel and Arch devtools, but restricts adoption in commercial AI coding runtimes. |

### 2.3 Non-Infringement & Separation from Reference Project (`unslop`)
- The reference project (`heydamir/unslop`) is licensed under **CC-BY-4.0**.
- Syswright has **not copied** any text, phrasing, or code from `unslop`.
- Syswright does **not automatically inherit** `unslop`'s license.

### 2.4 Recommendation for Project Owner
> **Recommendation: Option B (Apache-2.0) or Option C (Dual License Apache-2.0 / CC-BY-4.0).**
> Apache-2.0 provides critical patent protection for systems engineering scripts and compiler tools, while remaining completely friendly to upstream kernel and open-source contributors.
> 
> *Status*: **Awaiting Project Owner Approval.**

---

## 3. Decision Record 2: Subagent Execution Model Across Agent Platforms

### 3.1 The Problem
- **Claude Code** supports `context: fork`, which spawns an asynchronous background subagent with independent token context and custom effort levels.
- **OpenAI Codex** and generic Agent Skills platforms execute skills sequentially in the primary conversation thread.
- If skills assume background subagent execution, they will fail or pollute context when executed on platforms that do not support forking.

### 3.2 Evaluation of Alternatives
- **Alternative 1 (Strict Common Denominator)**: Prohibit subagent forks entirely; run everything in-turn. (Sacrifices Claude Code's superior token management during heavy compilation/eval runs).
- **Alternative 2 (Platform-Adaptive Execution)**: Store `claude_context: fork` inside the skill's standard `metadata:` block. The platform build compiler (`scripts/build_distribution.py`) enables background subagents when targeting Claude Code plugins, while generating sequential in-turn instructions for Codex and standard runners.

### 3.3 Recommendation for Project Owner
> **Recommendation: Alternative 2 (Platform-Adaptive Execution).**
> This preserves the single canonical source of truth in `skills/` while extracting maximum performance on platforms with native subagent delegation.
>
> *Status*: **Awaiting Project Owner Approval.**

---

## 4. Decision Record 3: Kernel Testbed Isolation (QEMU MicroVM vs. Local Host)

### 4.1 The Problem
Testing Linux kernel patches and device drivers requires running `insmod` or booting a kernel image. As established in `07-safety-and-verification.md`, testing on the developer's host machine carries unacceptable risk of kernel panics or data corruption. Standard containers cannot test kernel modules because they share the host kernel.

### 4.2 Evaluation of Alternatives
- **Alternative 1 (Host KVM QEMU MicroVM)**: Automate a headless microVM via `virtme-ng` or a lightweight QEMU script passing the compiled kernel and workspace via 9p/virtio-fs. Requires hardware virtualization (`/dev/kvm`).
- **Alternative 2 (Emulated TCG QEMU)**: Fallback to software emulation if `/dev/kvm` is inaccessible (e.g., inside restricted cloud CI). Slow boot times (30–60 seconds vs 1.5 seconds on KVM).
- **Alternative 3 (Static Verification Only)**: Restrict kernel evaluation to static analysis (`sparse`, `checkpatch`, `KUnit` user-mode) when VM virtualization is unavailable.

### 4.3 Recommendation for Project Owner
> **Recommendation: Tiered MicroVM Harness.**
> 1. Use hardware-accelerated KVM microVM when `/dev/kvm` is present.
> 2. Gracefully degrade to static analysis and KUnit (`ARCH=um` User Mode Linux) when virtualization is unavailable, explicitly flagging unverified runtime status.
>
> *Status*: **Awaiting Project Owner Approval.**

---

## 5. Decision Record 4: Distribution Expansion Priority for Phase 4

### 5.1 The Problem
While Phase 1 through 3 target Arch Linux, Phase 4 expands to additional distributions. We must prioritize which major enterprise / desktop distribution ecosystem to integrate first.

### 5.2 Trade-Off Analysis

| Ecosystem | Candidate Distributions | Packaging Tech | Init / Sandboxing | Pros & Cons for Syswright |
|:---|:---|:---|:---|:---|
| **Debian / Ubuntu Family** | Debian 12 (Bookworm),<br>Ubuntu 24.04 LTS | `dpkg`, `debhelper`,<br>`sbuild`, APT | systemd,<br>AppArmor default | **Pros**: Enormous server and developer install base; strict packaging standards (`lintian`).<br>**Cons**: Older LTS kernel versions require backport awareness. |
| **Fedora / RHEL Family** | Fedora 41,<br>RHEL 9 / 10 | RPM, `spec`,<br>`mock`, DNF | systemd,<br>SELinux default | **Pros**: Upstream-aligned rolling/rapid kernel updates; native SELinux integration.<br>**Cons**: Complex spec macro syntax. |

### 5.3 Recommendation for Project Owner
> **Recommendation: Prioritize Debian/Ubuntu first in Phase 4**, followed immediately by Fedora. Debian's strict policy rules and isolated `sbuild` chroots mirror Arch's `devtools` architecture closely.
>
> *Status*: **Awaiting Project Owner Guidance.**

---

## 6. Technical Uncertainties & Environmental Constraints

1. **Host `pkgctl` Installation**:
   - *Observation*: The current host environment lacks `pkgctl` in user PATH (requires `devtools` package).
   - *Mitigation*: In Phase 1, `scripts/namcap_gate.sh` and packaging evals will either check for `devtools` availability or invoke rootless containerized chroots (`podman` or `systemd-nspawn` where permitted) without altering the host OS.
2. **LLM Context Window Pressure During Kernel Analysis**:
   - *Observation*: Kernel source files (e.g., `drivers/net/ethernet/...`) can exceed 10,000 lines, far beyond efficient agent context budgets.
   - *Mitigation*: Skills must enforce strict localized reconnaissance (using `grep`, `cscope`, `sparse`, and AST parsers) rather than reading full C files into prompt context.

---

## 7. Cross-Reference Index

For deep technical context supporting these decisions, refer to:
- Executive Summary & Major Decisions: [00-executive-summary.md](file:///home/snigdha/Desktop/LinuxEngineering/docs/phase-0/00-executive-summary.md)
- Existing Repository State: [01-repository-assessment.md](file:///home/snigdha/Desktop/LinuxEngineering/docs/phase-0/01-repository-assessment.md)
- Comparative Analysis: [02-competitive-analysis.md](file:///home/snigdha/Desktop/LinuxEngineering/docs/phase-0/02-competitive-analysis.md)
- Platform Compatibility & Build Adapters: [03-platform-compatibility.md](file:///home/snigdha/Desktop/LinuxEngineering/docs/phase-0/03-platform-compatibility.md)
- Skill Catalog & Hierarchies: [04-skill-taxonomy.md](file:///home/snigdha/Desktop/LinuxEngineering/docs/phase-0/04-skill-taxonomy.md)
- Research Standards & Authority: [05-research-methodology.md](file:///home/snigdha/Desktop/LinuxEngineering/docs/phase-0/05-research-methodology.md)
- Arch Packaging Architecture: [06-arch-first-engineering.md](file:///home/snigdha/Desktop/LinuxEngineering/docs/phase-0/06-arch-first-engineering.md)
- Safety Model & MicroVM Mandate: [07-safety-and-verification.md](file:///home/snigdha/Desktop/LinuxEngineering/docs/phase-0/07-safety-and-verification.md)
- Repository Blueprint & ADRs: [08-technical-architecture.md](file:///home/snigdha/Desktop/LinuxEngineering/docs/phase-0/08-technical-architecture.md)
- Evaluation Scenarios: [09-evaluation-strategy.md](file:///home/snigdha/Desktop/LinuxEngineering/docs/phase-0/09-evaluation-strategy.md)
- Phase 1 Implementation Plan: [10-roadmap-and-phase-1.md](file:///home/snigdha/Desktop/LinuxEngineering/docs/phase-0/10-roadmap-and-phase-1.md)
- Authoritative Bibliography: [11-source-register.md](file:///home/snigdha/Desktop/LinuxEngineering/docs/phase-0/11-source-register.md)
