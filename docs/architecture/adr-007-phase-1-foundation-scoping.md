# ADR-007: Phase 1 Foundation Scoping & Specialist Deferral

## Context
During Phase 0, the initial high-level roadmap (`docs/phase-0/10-roadmap-and-phase-1.md`) contemplated implementing `arch-packaging` and `systemd-engineering` in Phase 1 alongside the three foundation skills (`linux-engineer`, `linux-research`, `linux-environment`).

Upon entering Phase 1 implementation, the engineering charter and requirements explicitly refined the scope boundaries:
1. Establish the operational foundation of Syswright.
2. Deliver the three foundation skills:
   - `linux-engineer` (Master orchestrator and router)
   - `linux-research` (Authoritative upstream evidence engine)
   - `linux-environment` (Safe, unprivileged system discovery)
3. Deliver shared global engineering references, multi-agent distribution tooling, validation tooling, and evaluation fixtures.
4. **Strictly defer** all domain specialists (kernel, driver, packaging, systemd, boot, application, desktop, performance, security, and distribution engineering) to subsequent phases. Empty placeholder skills are strictly forbidden.

## Decision
We formally adopt the refined Phase 1 scope:
- **In Scope for Phase 1**:
  - Tri-skill foundation: `linux-engineer`, `linux-research`, `linux-environment`.
  - Global engineering references (`research-methodology.md`, `source-authority.md`, `engineering-principles.md`, `version-awareness.md`, `safety-policy.md`, `testing-philosophy.md`).
  - Multi-agent adapters for Claude Code (`.claude-plugin/`) and OpenAI Codex (`adapters/codex/`, `AGENTS.md`).
  - Zero-dependency Python validation and packaging tools (`validate-skills.py`, `check-references.py`, `package-skills.py`).
  - Initial evaluation framework (routing, research evidence, environment fixtures).
  - Comprehensive automated test suite.
  - Core developer documentation (`README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `SECURITY.md`).
- **Deferred to Phase 2+**:
  - `arch-packaging` and `systemd-engineering` are re-sequenced into Phase 2 (alongside `kernel-engineering`, `driver-engineering`, and `boot-engineering`).
  - No empty directories or stub `SKILL.md` files for deferred skills will be introduced in Phase 1.
  - The `linux-engineer` orchestrator explicitly documents future specialist domains as *planned / currently unavailable in Phase 1*, preventing false-positive routing to non-existent skills.

## Consequences
- **Positive**: Prevents premature, rushed implementations of complex kernel and packaging specialists before the foundational validation and packaging tools are thoroughly tested.
- **Positive**: Keeps Phase 1 100% focused on architectural reliability, multi-agent packaging, and rigorous testing.
- **Neutral**: The Phase 1 test suite validates the 3 foundation skills and router dispatching, preparing clean testbeds for Phase 2 specialists.
