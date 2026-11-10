# Bodhi: Fedora Update Management & Quality Gating

Technical reference for filing package updates, automated testing, karma thresholds, and promotion to stable.

---

## 1. What is Bodhi?

Bodhi (`bodhi.fedoraproject.org`) manages package updates for released Fedora versions (`f40`, `f39`, `epel9`):
- Unlike Rawhide (where Koji builds enter the development tree immediately), builds for stable releases must pass through Bodhi.
- Updates enter the `updates-testing` repository first.
- Community testing, automated gating tests (openQA, CI), and karma votes validate the update before it is pushed to the `updates` repository.

---

## 2. Creating Bodhi Updates with fedpkg

```bash
# Create update in Bodhi after Koji build finishes
fedpkg update
```

### Update Metadata Fields:
- **Type**: `bugfix`, `security`, `enhancement`, `newpackage`.
- **Severity**: `low`, `medium`, `high`, `urgent`.
- **Notes**: Markdown changelog explaining user impact and bug references (`Fixes: rhbz#123456`).
- **Autokarma**:
  - Stable request threshold: Default is `+3` karma (or 7-14 days without negative karma).
  - Unstable threshold: Default is `-3` karma (automatically unpushes broken update from testing).
