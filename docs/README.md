# Syswright Documentation

Welcome to the **Syswright** engineering documentation portal. Syswright is a research-first, evidence-driven Linux systems engineering intelligence system and specialist skill catalog designed for AI coding agents.

---

## Architecture Specifications

Syswright follows a single-source canonical architecture with platform-specific distribution adapters. The architectural subsystems are documented below:

| Subsystem Specification | Core Disciplines Covered | Primary Components |
|---|---|---|
| [**Canonical & Adapter Architecture**](architecture/canonical-and-adapter-architecture.md) | Multi-agent runtime abstraction, packaging format generation, zero runtime dependencies. | Claude Code (`.claude-plugin`), OpenAI Codex, Agent Skills (`agentskills.io`). |
| [**Linux Systems Engineering**](architecture/linux-systems-engineering.md) | Core operating system, kernel subsystems, hardware devices, and early userspace. | `kernel-engineering`, `driver-engineering`, `systemd-engineering`, `boot-engineering`, `linux-networking`, `linux-storage`. |
| [**Native Application Engineering**](architecture/native-application-engineering.md) | Native desktop integration, GUI toolkits, system daemons, and modern build generators. | `linux-application-engineering`, `qt-qml-engineering`, `gtk-engineering`, `desktop-integration`, `linux-build-engineering`. |
| [**Advanced Linux Engineering**](architecture/advanced-linux-engineering.md) | Root-cause debugging, runtime performance analysis, defensive hardening, kernel observability, and regression hunting. | `linux-debugging`, `linux-performance`, `linux-security`, `linux-observability`, `linux-fuzzing`, `linux-regression-engineering`. |
| [**Arch Packaging Engineering**](architecture/arch-packaging.md) | Clean chroot builds, static PKGBUILD analysis, namcap verification, and AUR workflows. | `arch-packaging`. |
| [**Cross-Distribution & Supply-Chain**](architecture/cross-distribution-engineering.md) | Multi-distribution packaging, repository operations, reproducible builds, and release lifecycle. | `debian-packaging`, `ubuntu-packaging`, `rpm-packaging`, `fedora-packaging`, `opensuse-packaging`, `linux-distribution-engineering`, `reproducible-builds`, `linux-release-maintenance`. |

---

## Development & Testing

- [**Validation and Testing Guide**](development/validation-and-testing.md): Detailed specifications for running the automated unit test suite, deterministic benchmark evaluations across all 29 skills, and reference integrity checks.

---

## Core Engineering Invariants

1. **Research Before Implementation**: Query authoritative upstream sources (kernel.org, freedesktop.org, POSIX, Debian Policy, Fedora Guidelines) before authoring or modifying code.
2. **Evidence Before Assumptions**: Never claim a bug fix or performance optimization without reproducible, deterministic evidence.
3. **Operational Safety Tiers**: Autonomous execution is permitted for diagnostics and workspace builds; privileged or host-mutating operations strictly require human authorization.
