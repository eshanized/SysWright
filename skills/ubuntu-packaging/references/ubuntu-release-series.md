# Ubuntu Release Series: LTS vs Interim, Pockets, and Migration

Technical reference for Ubuntu release lifecycles, archive pockets, and package promotion rules.

---

## 1. Release Classification & Support Lifecycles

Ubuntu maintains two distinct release models:

| Release Type | Cadence & Versioning | Support Duration | Target Use Case |
|---|---|---|---|
| **LTS (Long Term Support)** | Released in April of even years (e.g., 20.04 focal, 22.04 jammy, 24.04 noble). | 5 years standard security updates; up to 10-12 years with Ubuntu Pro. | Enterprise servers, production clouds, stable workstations. |
| **Interim Releases** | Released every 6 months in October (e.g., 24.10 oracular) and April of odd years (e.g., 23.04 lunar). | 9 months total. | Early adoption of new kernels, GCC, GNOME, and software stacks. |

---

## 2. Archive Pockets Architecture

Every Ubuntu release series contains multiple archive pockets:

- **`<series>` (Release Pocket)**: The frozen, read-only snapshot created on release day. Never modified after release.
- **`<series>-updates`**: General bug fixes and stable updates that passed SRU verification.
- **`<series>-security`**: Critical security vulnerability fixes (CVEs) vetted by the Ubuntu Security Team.
- **`<series>-proposed`**: Testing pocket where candidate updates undergo automated validation and user verification before being promoted to `-updates`.
- **`<series>-backports`**: Selective backports of newer software from newer Ubuntu series.

---

## 3. The Proposed Migration Pipeline

When a package is uploaded to development or stable updates:
1. Package enters `<series>-proposed`.
2. Binary packages are compiled across all architectures.
3. Automated `autopkgtest` runs against the package and all its reverse dependencies.
4. If tests pass without regressions across all architectures, the package migrates to the release archive.
