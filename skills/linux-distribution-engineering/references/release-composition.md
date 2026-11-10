# Release Composition, Lockfiles & Solver Validation

A Linux release composition represents an immutable, mutually consistent collection of packages that satisfy all dependency constraints without conflict.

---

## 1. Composition Manifests & Package Pinning

Production distributions and appliances require deterministic builds. Leaving dependency resolution unbound creates drift where two nodes deployed on different days receive different package versions.

### Manifest Elements:
1. **Repository Commit/Snapshot ID**: Exact timestamp or snapshot URL.
2. **Package Name, Architecture, and Explicit Version**:
   - `systemd=255.4-1ubuntu8.4`
   - `openssl=3.0.13-0ubuntu3.4`
3. **Cryptographic Checksum**: SHA-256 hash of the `.deb` or `.rpm` binary artifact.

### APT Snapshot Pinning (`sources.list`):
```text
deb [signed-by=/usr/share/keyrings/corp.gpg] https://snapshot.debian.org/archive/debian/20260401T000000Z/ bookworm main
```

---

## 2. Solver Validation with Dose3 and SAT Checkers

Before releasing a repository update, run formal constraint solvers across the package database to detect:
- Broken dependencies (packages depending on missing packages or versions).
- Conflicts (mutually exclusive packages forced into installation sets).
- Co-installability regressions.

### Using `dose-distcheck` for Debian/APT:
```bash
dose-distcheck --deb dists/stable/main/binary-amd64/Packages.gz
```
If output contains:
```text
broken-packages: 2
  package-a depends on package-b (>= 2.0) but package-b is 1.9
```
The repository composition is invalid and promotion must be aborted immediately.

### Using `dnf repoquery` for RPM Repositories:
```bash
dnf repoquery --repofrompath=test,/srv/repo/x86_64 --repo=test --unsolved
```
Any returned package indicates a missing dependency.