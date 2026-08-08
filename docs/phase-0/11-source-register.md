# Authoritative Source Register: Linux Engineering

## 1. Register Overview & Governance

This source register documents all authoritative technical sources, standards specifications, upstream repositories, and maintainer manuals inspected during **Phase 0**.

Every source recorded here has been directly evaluated for technical veracity, software version applicability, and architectural relevance to the Linux Engineering system.

- **Inspection Date**: November 23, 2026
- **Auditor**: Principal Linux Systems Architect & AI Agent Skills Architect
- **Citing Standard**: 7-Tier Source Authority Hierarchy (defined in `05-research-methodology.md`).

---

## 2. Master Bibliographic Ledger

| ID | Title & URL | Authority Tier | Software / Spec Version | Research Area | Technical Finding & Architectural Implication |
|:---:|:---|:---:|:---:|:---:|:---|
| **SRC-01** | **Agent Skills Specification**<br>`https://agentskills.io/specification` | **Tier 1**<br>(Open Standard) | Spec v1.0 | Agent Standards | Establishes the vendor-neutral format for `SKILL.md` (directory name match, frontmatter rules: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`). Mandates progressive disclosure and validation via `skills-ref`. Forms our canonical skill baseline. |
| **SRC-02** | **Claude Code: Extend Claude with Skills**<br>`https://code.claude.com/docs/en/skills` | **Tier 1**<br>(Vendor Official) | Claude Code v2.1.300+ | Platform Compatibility | Documents Claude's adoption of the Agent Skills standard and its rich frontmatter extensions (`when_to_use`, `paths`, `context: fork`, `agent`, `model`, `effort`, `hooks`, `arguments`). Establishes how subagents and background tasks execute. |
| **SRC-03** | **Claude Code: Plugins Overview & Specification**<br>`https://code.claude.com/docs/en/plugins` | **Tier 1**<br>(Vendor Official) | Claude Code v2.1.300+ | Packaging & Plugins | Documents multi-skill packaging using `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`. Governs how Linux Engineering bundles skills, hooks, and agents for Claude Code users. |
| **SRC-04** | **OpenAI Codex: Skills Concept Guide**<br>`https://developers.openai.com/plugins/concepts/skills` | **Tier 1**<br>(Vendor Official) | Codex / GPT-6 Astra | Platform Compatibility | Documents OpenAI's skill implementation using `SKILL.md` folders, frontmatter, and complementary MCP server tooling. Governs how skills teach models repeatable workflows without baking in live state. |
| **SRC-05** | **OpenAI Cookbook: Iterating Development Workflows with Codex**<br>`https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex` | **Tier 1**<br>(Vendor Official) | Codex 2026 | Platform Compatibility | Documents the official role of `AGENTS.md` as durable, persistent repository-level guidance read before tool calls. Validates generating root `AGENTS.md` for Codex support. |
| **SRC-06** | **The Linux Kernel Documentation**<br>`https://docs.kernel.org/` | **Tier 1**<br>(Upstream Official) | Linux 6.18+ LTS / Mainline | Kernel Engineering | Authoritative upstream documentation covering Kbuild, Kconfig, device drivers, synchronization primitives, memory management, and subsystem architectures. |
| **SRC-07** | **Submitting Patches: The Essential Guide to Getting Your Code Into the Kernel**<br>`https://docs.kernel.org/process/submitting-patches.html` | **Tier 1**<br>(Upstream Official) | Linux 6.x | Kernel / Upstream | Establishes patch formatting rules, imperative commit logs, `Signed-off-by` trailers, subsystem prefixes, and strict verification with `scripts/checkpatch.pl`. |
| **SRC-08** | **KUnit — Linux Kernel Unit Testing Framework**<br>`https://docs.kernel.org/dev-tools/kunit/` | **Tier 1**<br>(Upstream Official) | Linux 6.x | Kernel Verification | Documents in-tree unit testing for kernel subsystems without requiring userspace test harnesses. Informs the `kernel-engineering` acceptance validator. |
| **SRC-09** | **Sparse — Semantic Parser for C**<br>`https://docs.kernel.org/dev-tools/sparse.html` | **Tier 1**<br>(Upstream Official) | v0.6.4+ | Kernel Static Analysis | Documents static semantic checking for kernel C (`__user`, `__kernel`, `__iomem`, `__bitwise`, lock context checking). Enforced via `make C=1`. |
| **SRC-10** | **Arch Linux Package Guidelines**<br>`https://wiki.archlinux.org/title/Arch_package_guidelines` | **Tier 4**<br>(Distribution Policy) | Arch Rolling | Packaging | Canonical rules for Arch packaging, directory standards (`/usr/bin`, `/usr/lib`, `/usr/share`), library naming, and license placement. |
| **SRC-11** | **PKGBUILD Specification & Variables**<br>`https://wiki.archlinux.org/title/PKGBUILD` | **Tier 4**<br>(Distribution Policy) | Pacman v6.1+ | Packaging | Exhaustive reference for `PKGBUILD` bash syntax, variables (`pkgname`, `pkgver`, `pkgrel`, `arch`, `depends`, `makedepends`, `source`, `sha256sums`), and lifecycle functions (`prepare`, `build`, `check`, `package`). |
| **SRC-12** | **Arch Linux devtools(7) Manual**<br>`https://man.archlinux.org/man/devtools.7` | **Tier 4**<br>(Distribution Policy) | devtools v1.2+ | Clean Chroot Builds | Authoritative manual for `pkgctl`, `mkarchroot`, and `arch-nspawn`. Governs isolated clean chroot builds for reproducibility and zero host pollution. |
| **SRC-13** | **Namcap Packaging Static Analyzer**<br>`https://wiki.archlinux.org/title/namcap` | **Tier 4**<br>(Distribution Policy) | namcap v3.5+ | Packaging Verification | Documents rule-based static analysis of `PKGBUILD` and compiled packages. Forms the core deterministic gate for `arch-packaging`. |
| **SRC-14** | **systemd.service & systemd.exec Documentation**<br>`https://www.freedesktop.org/software/systemd/man/latest/` | **Tier 1**<br>(Upstream Official) | systemd v256+ | Systemd Engineering | Exhaustive manual for service types (`Type=exec`, `Type=notify`), dependencies (`Wants`, `Requires`, `After`), and sandboxing (`ProtectSystem=strict`, `DynamicUser=yes`, `NoNewPrivileges=yes`, `CapabilityBoundingSet=`). |
| **SRC-15** | **systemd-analyze Security & Verification Manual**<br>`https://www.freedesktop.org/software/systemd/man/latest/systemd-analyze.html` | **Tier 1**<br>(Upstream Official) | systemd v256+ | Systemd Verification | Documents `systemd-analyze verify` (static unit linting) and `systemd-analyze security` (exposure score calculator). Primary validator for `systemd-engineering`. |
| **SRC-16** | **B4 Tools: Kernel Patch Workflow Automation**<br>`https://b4.docs.kernel.org/` | **Tier 3**<br>(Maintainer Tooling) | b4 v0.14+ | Upstream Release | Authoritative tooling for lore.kernel.org patch series management (`b4 prep`, `b4 send`, `b4 trailers`). Forms the foundation for `linux-release-maintenance`. |
| **SRC-17** | **kworkflow (kw) Architecture & Manual**<br>`https://github.com/kworkflow/kworkflow` | **Tier 5**<br>(Open Source Project) | kw v0.8+ | Kernel Workflow | Informs rapid kernel compilation and QEMU microVM testbed automation (`kw vm`). |
| **SRC-18** | **heydamir/unslop Skill & Plugin Repository**<br>`https://github.com/heydamir/unslop` | **Tier 5**<br>(Reference Project) | Git commit 620163e | Skill Architecture | Reference architecture for Agent Skills: progressive disclosure (`references/`), phased passes, deterministic scripts, and Claude plugin packaging. License: CC-BY-4.0. |
| **SRC-19** | **Syzkaller Kernel Fuzzer & Syzbot Architecture**<br>`https://github.com/google/syzkaller` | **Tier 5**<br>(Open Source Project) | Syzkaller 2026 | Kernel Testing | Informs kernel oops, KASAN, and lockdep crash pattern matching and reproducer isolation. |
| **SRC-20** | **bpftrace Reference Guide & BCC Tools**<br>`https://github.com/bpftrace/bpftrace` | **Tier 1**<br>(IOVisor / Linux Foundation) | bpftrace v0.21+ | Dynamic Observability | Authoritative syntax and safety invariants for eBPF-based dynamic kernel and userspace tracing without service interruption. |
| **SRC-21** | **FreeDesktop Specifications**<br>`https://specifications.freedesktop.org/` | **Tier 1**<br>(Freedesktop Standards) | Current Specs | Desktop Integration | Standards for Desktop Entry (`.desktop`), Basedir (`$XDG_CONFIG_HOME`), Icon Theme, and AppStream metadata. |
| **SRC-22** | **POSIX.1-2024 (IEEE Std 1003.1-2024)**<br>`https://pubs.opengroup.org/onlinepubs/9799919799/` | **Tier 1**<br>(International Standard) | Issue 8 (2024) | Systems Programming | Canonical standard for Linux/UNIX system interfaces, signals, file descriptors, and process lifecycles. |
| **SRC-23** | **Gravitas Reliability Runtime**<br>`https://github.com/udaysharmadev/Gravitas` | **Tier 5**<br>(Local Repository Runtime) | Git commit e0d22cd | Agent Reliability | Local reliability framework enforcing the 6 core invariants, decision records, and contract-gated verification. |

---

## 3. Disclosures & Unresolved Technical Discrepancies

1. **Agent Skills `allowed-tools` Portability**:
   While the `agentskills.io` standard includes `allowed-tools` as an experimental frontmatter field, support varies significantly across runtimes. Claude Code supports `allowed-tools` during the turn the skill is invoked, whereas standard OpenAI Codex plugins manage tool access via MCP manifests in `agents/openai.yaml`. Linux Engineering relies on standard OS tool invocations and treats `allowed-tools` as an advisory hint.
2. **`systemd-analyze security` Scoring Thresholds**:
   The numeric score calculated by `systemd-analyze security` is derived from weighted heuristics that change across systemd releases (e.g., v252 vs v256). Linux Engineering defines the threshold dynamically based on the active systemd version reported by `linux-environment`.
3. **Host Tool Availability vs. Clean Chroot**:
   The host machine currently has `makepkg` and `namcap`, but lacks `pkgctl` in user PATH. Phase 1 will support clean chroot builds via direct `arch-nspawn` or guide unprivileged users to user-mode container alternatives.
