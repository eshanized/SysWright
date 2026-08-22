# Validation, Testing & Verification Guide: Linux Engineering

## 1. Overview

Linux Engineering enforces strict automated verification across all skills, references, scripts, and evaluation scenarios.

Every component must pass:
1. **Skill Specification Validation** (`scripts/validate-skills.py`)
2. **Internal Reference Integrity** (`scripts/check-references.py`)
3. **Packaging Safety & Determinism** (`scripts/package-skills.py`)
4. **Automated Unit & Integration Test Suites** (`tests/run_all_tests.py`)

---

## 2. Running the Tooling

### 2.1 Skill Validation (`scripts/validate-skills.py`)
Validates that every skill directory adheres to the `agentskills.io` open standard:
```bash
python3 scripts/validate-skills.py
```
Checks performed:
- `SKILL.md` exists and starts with `---`.
- Frontmatter parses cleanly without third-party dependencies.
- `name` matches parent directory, is 1–64 characters, lowercase alphanumeric and hyphens only, no consecutive hyphens.
- `description` is non-empty, 1–1024 characters.
- `compatibility` is $\le 500$ characters if present.
- `metadata` is a valid string-to-string mapping.
- All internal file references exist on disk.

### 2.2 Reference Link Checking (`scripts/check-references.py`)
Scans all Markdown files in `skills/`, `references/`, and `docs/` for broken relative links:
```bash
python3 scripts/check-references.py
```
Options:
- `--external`: Optionally checks external HTTP/HTTPS URLs with a 5-second timeout (flags broken links without failing CI on network timeouts).

### 2.3 Deterministic Packaging (`scripts/package-skills.py`)
Packages skills for target platforms:
```bash
# Package standard release archive:
python3 scripts/package-skills.py --target archive --output dist/

# Package for Claude Code:
python3 scripts/package-skills.py --target claude-code --output dist/claude/

# Package for OpenAI Codex:
python3 scripts/package-skills.py --target codex --output dist/codex/
```
Safety guarantees:
- Path traversal protection (prevents symlinks or malicious relative paths from escaping destination).
- Excludes `.git`, `__pycache__`, `.env`, secrets, and temporary files.
- Fully deterministic archive generation (`SOURCE_DATE_EPOCH` support).

---

## 3. Running Automated Tests

The test suite is located under `tests/` and uses Python's standard `unittest` framework:

```bash
# Run the complete test suite:
python3 tests/run_all_tests.py

# Or run individual test modules:
python3 -m unittest tests/test_validate_skills.py
python3 -m unittest tests/test_check_references.py
python3 -m unittest tests/test_package_skills.py
python3 -m unittest tests/test_discover_environment.py
python3 -m unittest tests/test_routing_evals.py
```

All tests are completely unprivileged and execute using temporary directories.
