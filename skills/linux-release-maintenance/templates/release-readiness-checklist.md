# Release Readiness Checklist (Go / No-Go Gate)

**Release Target**: [e.g., myapp 1.3.0]  
**Release Lead**: [Name / Agent ID]  
**Target Date**: [YYYY-MM-DD]  

---

## 1. Source & Git Cleanliness
- [ ] Upstream Git tag created, signed, and pushed (`git tag -s v1.3.0 -m "Release 1.3.0"`).
- [ ] No untracked, uncommitted, or temporary files present in repository tree.
- [ ] All CI builds passing on main branch.

---

## 2. Compilation & Isolated Builds
- [ ] Clean build in isolated chroot/container for x86_64:
  - [ ] Arch Linux (`extra-x86_64-build`)
  - [ ] Debian Bookworm (`sbuild`)
  - [ ] Ubuntu Noble (`sbuild` / PPA)
  - [ ] Fedora 40 (`mock`)
  - [ ] openSUSE Tumbleweed (`osc build`)
- [ ] Multi-architecture builds verified (arm64, s390x, ppc64le where applicable).

---

## 3. Testing & Quality Assurance
- [ ] 100% unit test pass rate (`ctest` / `cargo test` / `make check`).
- [ ] Integration smoke tests executed against running daemons.
- [ ] Upgrade test from version [prior version] verified without conffile prompts or data corruption.
- [ ] Package linters passed with 0 errors:
  - [ ] `namcap` (Arch)
  - [ ] `lintian` (Debian/Ubuntu)
  - [ ] `rpmlint` (Fedora/openSUSE)

---

## 4. Supply Chain & Reproducibility
- [ ] `SOURCE_DATE_EPOCH` exported and verified.
- [ ] `diffoscope` comparison shows bit-for-bit identity or justified variance.
- [ ] SPDX 2.3 SBOM generated and archived with release artifacts.
- [ ] SLSA provenance in-toto attestation generated and signed.

---

## 5. Final Go / No-Go Decision
- [ ] **GO**: All verification checks passed. Proceed with repository publication.
- [ ] **NO-GO**: Release blocked due to: _________________________.
