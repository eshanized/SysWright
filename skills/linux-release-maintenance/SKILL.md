---
name: linux-release-maintenance
description: Linux upstream release maintenance and multi-distribution lifecycle specialist. Covers monitoring upstream releases via uscan and Anitya, patch queue management (rebasing, forwarding, dropping applied patches), multi-distribution package synchronization (Arch, Debian, Ubuntu, Fedora, openSUSE), shared library ABI transitions and soname bumps, backporting CVE security fixes to LTS releases, and formal release readiness gating.
license: Apache-2.0
compatibility: Requires Linux environment and git.
metadata:
  author: Linux Engineering Contributors
  version: "0.1.0"
---

# Linux Release Maintenance Specialist

The `linux-release-maintenance` skill guides AI agents through the end-to-end lifecycle of tracking upstream software, managing downstream patch queues, synchronizing releases across multiple Linux distributions, coordinating shared library ABI transitions, and executing security backports for Long Term Support (LTS) releases.

---

## 1. Multi-Distribution Release Maintenance Lifecycle

```mermaid
flowchart TD
    MONITOR["1. Upstream Monitoring\n(uscan watch, Anitya, Git tags)"] --> INGEST["2. Ingest New Upstream Release\n(Tarball checksums, signature verify)"]
    INGEST --> PATCH_AUDIT["3. Audit Downstream Patch Queue\n(Rebase, drop merged patches, forward new)"]
    PATCH_AUDIT --> ABI_CHECK["4. Assess ABI / API Compatibility\n(abi-compliance-checker, soname bump?)"]
    ABI_CHECK --> MULTI_SYNC["5. Synchronize Multi-Distro Packaging\n(PKGBUILD, debian/, fedora.spec, opensuse.spec)"]
    MULTI_SYNC --> MATRIX_BUILD["6. Matrix Builds & Smoke Testing\n(Arch, Debian, Ubuntu, Fedora, openSUSE)"]
    MATRIX_BUILD --> GATE["7. Release Readiness Checklist Signoff\n(QA, regression test, CVE audit)"]
    GATE --> PUBLISH["8. Coordinated Publication & Maintenance Logging"]
```

### The 8-Step Release Maintenance Discipline:
1. **Automate Upstream Tracking**: Monitor upstream release feeds, GitHub/GitLab releases, and registry indices using tools like Debian `uscan` or release-monitoring.org.
2. **Verify Upstream Integrity**: Validate cryptographic signatures (GPG/Cosign) and release hashes before unpacking new tarballs.
3. **Audit and Prune Downstream Patches**: Evaluate every downstream patch against the new release; drop patches accepted upstream, rebase necessary local deltas, and document reasons.
4. **Enforce Semantic ABI Tracking**: Check for breaking library ABI/API changes using `abi-dumper` and `abi-compliance-checker`; coordinate soname bumps and transitional packages when needed.
5. **Harmonize Multi-Distribution Metadata**: Keep package metadata, license expressions, and build dependencies aligned across Arch Linux, Debian, Ubuntu, Fedora, and openSUSE.
6. **Execute Matrix Smoke Testing**: Compile and run test suites across target distributions using containers or VMs prior to committing changes.
7. **Complete Release Readiness Review**: Verify changelogs, upgrade paths, bug fix verifications, and security impact before tagging or uploading.
8. **Document Maintenance History**: Maintain clean, distribution-compliant changelogs and forward all bug fixes upstream with DEP-3 or upstream Git PRs.

---

## 2. Multi-Distribution Packaging Layout Comparison

| Distribution | Packaging Directory / File | Patch Management System | Changelog Format |
|---|---|---|---|
| **Arch Linux** | `PKGBUILD` | In-tree `source=(...)` + `prepare()` | Git commit history or `.INSTALL` |
| **Debian / Ubuntu** | `debian/` (`control`, `rules`) | Quilt (`debian/patches/series`) | `debian/changelog` (strict format) |
| **Fedora** | `<name>.spec` | Git / `Patch0: ...` / `%autosetup -p1` | `%changelog` or `%autochangelog` |
| **openSUSE** | `<name>.spec` + `<name>.changes` | `Patch0: ...` / `%autosetup -p1` | `<name>.changes` (RFC 822 format) |

---

## 3. Operational Safety Boundaries

- **Tier 0 (Diagnostics)**: Checking upstream watch status (`uscan --dry-run`), comparing git tags, auditing patch series, and analyzing ABI compatibility reports is fully autonomous.
- **Tier 1 (Workspace Builds)**: Rebasing patch queues, updating spec/PKGBUILD files in workspace branches, and executing test builds runs autonomously.
- **Tier 3 (Host Mutating / Upstream Releasing)**: Pushing tags to upstream remotes, uploading packages to distribution archives (Mentors, Launchpad, Koji, OBS), or filing official SRUs strictly requires explicit human authorization.

---

## 4. Reference Library

- [upstream-tracking.md](references/upstream-tracking.md) — Release monitoring tools, `debian/watch`, Anitya, and Git tag verification.
- [patch-maintenance.md](references/patch-maintenance.md) — Patch lifecycle, DEP-3 headers, rebasing strategies, and upstream forwarding.
- [multi-distro-maintenance.md](references/multi-distro-maintenance.md) — Maintaining unified software across Arch, Debian, Ubuntu, Fedora, and openSUSE.
- [abi-transitions.md](references/abi-transitions.md) — Soname bumps, ABI compliance tooling, and transitional library packaging.
- [security-maintenance.md](references/security-maintenance.md) — CVE tracking, CVSS scoring, minimal backporting, and security advisories.
- [release-readiness.md](references/release-readiness.md) — Formal Go/No-Go checklists, regression testing, and signoff criteria.
- [lifecycle-management.md](references/lifecycle-management.md) — Long Term Support (LTS) policies, End of Life (EOL) tracking, and sunsetting.