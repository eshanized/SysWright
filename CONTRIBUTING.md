# Contributing to Linux Engineering

Thank you for your interest in contributing to **Linux Engineering**! This project provides a research-first engineering intelligence system for AI coding agents working on Linux systems development.

---

## 1. Core Contribution Philosophy

Every contribution must honor the foundational principle:
> **Research before implementation. Evidence before assumptions. Verification before completion.**

1. **Evidence-Based Changes**: Do not propose or alter skills, packaging rules, or references based on unverified assumptions or search snippets. Ground every technical claim in Tier 1/2 authoritative sources.
2. **Minimal Blast Radius**: Keep changes focused and surgical. Do not reformat unrelated files or reorder lines unnecessarily.
3. **Open Standards Compliance**: All skills must strictly adhere to the vendor-neutral **Agent Skills specification** (`agentskills.io`).

---

## 2. Skill Authoring Guidelines

When creating or updating skills under `skills/`:
1. **Directory Naming**: Must match the skill `name` field exactly. Use only lowercase alphanumeric characters and single hyphens (`^[a-z0-9]+(-[a-z0-9]+)*$`).
2. **SKILL.md Frontmatter**:
   - `name`: 1–64 characters, lowercase.
   - `description`: 1–1024 characters, clear triggers and keywords.
   - `compatibility`: Max 500 characters, specifying Linux prerequisites.
   - `metadata`: Key-value mapping for platform extension hints (e.g. `claude_context: fork`).
3. **Progressive Disclosure**:
   - Keep the main `SKILL.md` under 500 lines (<5,000 tokens).
   - Place exhaustive registers, syntax guides, and tables into `references/` or skill-local `references/`.
   - Place reusable templates into `templates/` and deterministic utilities into `scripts/`.

---

## 3. Source Citation & Research Standards

When contributing engineering knowledge or reference documents:
1. Adhere to the **7-Tier Authority Hierarchy** defined in [references/source-authority.md](references/source-authority.md).
2. Prioritize:
   - Tier 1: Upstream documentation (`docs.kernel.org`, `freedesktop.org`, `man7.org`, POSIX).
   - Tier 2: Upstream source code (`git.kernel.org`, `systemd` git).
   - Tier 3: Maintainer mailing lists (`lore.kernel.org`).
   - Tier 4: Distribution policies (`wiki.archlinux.org`, Debian Policy).
3. **Disqualified**: Never cite unverified blog posts, Reddit, StackOverflow, or AI summaries as primary authority.

---

## 4. Pre-Commit Validation & Testing

Before submitting a pull request, verify that all local checks pass:

```bash
# 1. Validate all skill directories against the Agent Skills standard:
python3 scripts/validate-skills.py

# 2. Verify all internal relative markdown links:
python3 scripts/check-references.py

# 3. Run the complete automated test suite (55+ unit and integration tests):
python3 tests/run_all_tests.py

# 4. Run application, systems, and advanced engineering evaluation suites:
python3 evals/eval_advanced_engineering.py
python3 evals/eval_native_apps.py
python3 evals/eval_systems.py
```

All 55+ automated tests and benchmark evaluations must pass with exit code `0`.

---

## 5. Adding and Reviewing Application-Oriented Skills

When contributing to application, desktop, or build engineering skills:
- **Desktop Standards**: Verify Desktop Entries via `desktop-file-validate` and AppStream metadata via `appstreamcli validate --strict`.
- **Accessibility Invariant**: Treat AT-SPI accessibility as an inviolable engineering requirement. Never approve interfaces that lack accessible labels or keyboard focus paths.
- **Build Reproducibility**: Ensure build recommendations respect `SOURCE_DATE_EPOCH` and strip non-deterministic host paths (`-ffile-prefix-map`).
- **No Unsanctioned Privileges**: Never recommend running desktop applications as root. Enforce unprivileged execution and narrow polkit-gated D-Bus interfaces.

---

## 5. Security & Safety Reviews

If your contribution touches scripts, commands, or execution boundaries:
- Ensure no commands require root privileges or invoke `sudo`.
- Ensure scripts run safely in unprivileged user mode.
- Avoid introducing external Python dependencies; rely exclusively on the Python 3 standard library.
