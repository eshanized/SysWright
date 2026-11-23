# Syswright — Phase 6 Architecture: Cross-Distribution, Release and Supply-Chain Engineering

## 1. Executive Summary

Phase 6 expands **Syswright** from single-distribution packaging (Arch Linux) and systems programming into a comprehensive multi-distribution, release maintenance, and software supply-chain ecosystem.

In professional Linux engineering, software rarely targets a single platform. An application or system service must be reliably packaged, distributed, and maintained across **Debian, Ubuntu, Fedora, openSUSE, Arch Linux, and Enterprise Linux (RHEL/SLE)** without confusing their conflicting policies, macro conventions, directory layouts, or release workflows.

Phase 6 equips AI agents with the capabilities and discipline of senior distribution maintainers and supply-chain security architects:
- **Distribution Policy Fidelity**: Never confuse Debian policy with Fedora guidelines or openSUSE conventions. Enforce exact macro standards, license formats (SPDX), and scriptlet rules.
- **Repository Integrity & Key Separation**: Separate offline master GPG keys from online signing subkeys; eliminate mirror synchronization race conditions via two-stage rsync and `by-hash` metadata; prevent broken client caches using fast-forward epoch reverts rather than naive package deletion.
- **Bit-for-Bit Reproducibility**: Eliminate build non-determinism via `SOURCE_DATE_EPOCH`, `-ffile-prefix-map`, and archive sorting; diagnose variances using `diffoscope` and `reprotest`.
- **Supply-Chain Verification**: Produce standard SPDX 2.3 / CycloneDX 1.5 SBOMs and SLSA Level 3 in-toto build provenance attestations; verify upstream tarball integrity against signed Git tags.
- **Upstream & Multi-Distro Lifecycle**: Automate release discovery (`debian/watch`, Anitya); manage patch queues (DEP-3, quilt, rebasing, pruning); coordinate shared library ABI transitions (`abi-compliance-checker`); backport minimal security fixes without breaking LTS ABIs.

---

## 2. Specialist Domain Architecture

Phase 6 introduces eight specialist engineering capabilities that coordinate through the central orchestrator:

```text
                                         ┌────────────────────────┐
                                         │     linux-engineer     │
                                         │  (Master Orchestrator) │
                                         └───────────┬────────────┘
         ┌───────────────────┬───────────────────────┼───────────────────────┬───────────────────┐
         ▼                   ▼                       ▼                       ▼                   ▼
┌──────────────────┐ ┌────────────────┐    ┌──────────────────┐    ┌─────────────────┐ ┌─────────────────┐
│ debian-packaging │ │ubuntu-packaging│    │  rpm-packaging   │    │fedora-packaging │ │opensuse-packag. │
│(debhelper, quilt)│ │ (PPA, SRU bug) │    │(core spec, $1=0) │    │ (mock, Koji)    │ │  (OBS, osc CLI) │
└────────┬─────────┘ └───────┬────────┘    └────────┬─────────┘    └────────┬────────┘ └────────┬────────┘
         │                   │                      │                       │                   │
         └───────────────────┼──────────────────────┴───────────────────────┴───────────────────┘
                             ▼
         ┌───────────────────────────────────────┬───────────────────────────────────────┐
         ▼                                       ▼                                       ▼
┌─────────────────────────────────┐ ┌─────────────────────────────────┐ ┌─────────────────────────────────┐
│  linux-distribution-engineering │ │       reproducible-builds       │ │    linux-release-maintenance   │
│(Repo layouts, GPG, promotion)   │ │  (SOURCE_DATE_EPOCH, SBOM, SLSA)│ │ (uscan, ABI bumps, LTS CVEs)    │
└─────────────────────────────────┘ └─────────────────────────────────┘ └─────────────────────────────────┘
```

### Responsibility Demarcation:

| Specialist Skill | Primary Responsibility | Distinguishing Boundary |
|---|---|---|
| [`debian-packaging`](../../skills/debian-packaging/SKILL.md) | Debian source and binary package maintenance. | Focuses on Debian Policy, debhelper 13+, DEP-3 quilt patches, sbuild clean chroots, lintian, and autopkgtest. |
| [`ubuntu-packaging`](../../skills/ubuntu-packaging/SKILL.md) | Ubuntu-specific packaging and Launchpad workflows. | Focuses on Ubuntu delta over Debian, Launchpad PPAs, source-only uploads, LTS vs Interim series, and formal SRU test plans. |
| [`rpm-packaging`](../../skills/rpm-packaging/SKILL.md) | Core RPM package anatomy and macros. | Focuses on spec preambles, scriptlets ($1=0 upgrade trap), file triggers, directory macros, and automatic soname provides/requires. |
| [`fedora-packaging`](../../skills/fedora-packaging/SKILL.md) | Fedora and Enterprise Linux guidelines. | Focuses on Fedora Packaging Guidelines, SPDX licensing, strict unbundling, mock chroots, fedpkg dist-git, Koji, Bodhi, and EPEL. |
| [`opensuse-packaging`](../../skills/opensuse-packaging/SKILL.md) | openSUSE and Open Build Service (OBS) engineering. | Focuses on openSUSE spec conventions, `%service_add_post`, OBS project architecture, `osc` CLI, and Tumbleweed vs Leap. |
| [`linux-distribution-engineering`](../../skills/linux-distribution-engineering/SKILL.md) | Repository architecture and distribution pipelines. | Focuses on APT, DNF repomd, Zypper, and Pacman repo layouts; GPG signing; staged promotion; SAT solver validation; and rollbacks. |
| [`reproducible-builds`](../../skills/reproducible-builds/SKILL.md) | Deterministic compilation and supply-chain verification. | Focuses on bit-for-bit identity, `SOURCE_DATE_EPOCH`, `diffoscope`, `reprotest`, SPDX/CycloneDX SBOMs, and SLSA Level 3 attestations. |
| [`linux-release-maintenance`](../../skills/linux-release-maintenance/SKILL.md) | Upstream tracking and cross-distro lifecycle. | Focuses on upstream release monitoring (`debian/watch`, Anitya), patch queues, ABI transitions, CVE backporting, and Go/No-Go gates. |

---

## 3. Core Architectural Subsystems

### 3.1 Debian & Ubuntu Packaging Ecosystem
- **Modern debhelper Sequencer**: Enforce debhelper-compat 13 with `dh $@` and structured override targets (`override_dh_auto_configure`, `override_dh_auto_test`), eliminating legacy manual helper calls.
- **Multi-Arch & Dynamic Dependencies**: Declare `Architecture: any` and `Multi-Arch: same` on compiled shared libraries. Rely strictly on `${shlibs:Depends}` and `${misc:Depends}` computed by `dpkg-shlibdeps` rather than hardcoding library names.
- **DEP-3 Patch Metadata**: All downstream patches in `debian/patches/` must include structured DEP-3 headers (`Description`, `Author`, `Origin`, `Bug-Debian`, `Forwarded`).
- **Ubuntu Delta & PPA Discipline**: Inspect deltas using `debdiff` and minimize packaging divergence by upstreaming patches to Debian Salsa. Upload only source packages (`debuild -S`) signed with registered GPG keys to Launchpad.
- **Stable Release Updates (SRU)**: Enforce formal Launchpad bug templates with mandatory sections: `[Impact]`, `[Test Plan]`, and `[Where problems could occur]`, with required 7-day aging in `-proposed`.

### 3.2 RPM Family Packaging: Core, Fedora & openSUSE
- **Macro Standards & Scriptlet Hygiene**: Use built-in directory macros (`%{_bindir}`, `%{_sysconfdir}`, `%{_libdir}`) and standard build wrappers (`%cmake_build`, `%make_build`). Protect service scriptlets with `$1 == 0` checks or modern systemd macros (`%systemd_preun`) to prevent stopping newly upgraded services.
- **Automatic Dependencies**: Leverage `find-requires` and `find-provides` ELF scanning; remove redundant manual soname `Requires:`.
- **Fedora Guidelines**: Mandate `Release: %autorelease`, `%changelog \n %autochangelog`, and valid SPDX license identifiers. Strictly forbid bundled third-party libraries; strip vendored sources in `%prep` and link against system shared libraries.
- **openSUSE & Open Build Service**: Adhere to openSUSE shared library policy requiring packages to be named strictly matching their soname (`libfoo1`), separate from `libfoo-devel`. Use `osc` for local chroot builds (`osc build`) and Submit Requests (`osc sr`).

### 3.3 Distribution & Repository Infrastructure
- **Cryptographic Key Separation**: Keep the root master GPG key strictly offline on air-gapped storage. Issue dedicated signing subkeys for build servers with 1-year expiration and periodic rotation without altering client root trust.
- **Two-Stage Mirror Synchronization**: Synchronize package pools (`pool/`) before metadata indices (`dists/` or `repodata/`) to prevent `404 Not Found` or hash sum mismatch races on edge mirrors. Adopt `by-hash` layouts for immutable client requests.
- **Staged Promotion & Atomic Swaps**: Promote identical binary packages through `dev` $\to$ `staging` $\to$ `production` without recompilation. Atomically replace active repository metadata directories using symlink swaps (`ln -sfn`) or directory renames.
- **Emergency Rollback via Epoch Bumps**: Never delete packages from production pools. Deploy fast-forward rollback packages with incremented epochs or releases (`netfoo 1:2.9.0-1`), enabling client package managers to cleanly downgrade during routine updates.
- **SAT Solver Validation**: Verify repository co-installability and detect broken leaves prior to publication using `dose-distcheck` (Debian) and `dnf repoquery --unsolved` (RPM).

### 3.4 Reproducible Builds & Software Supply Chain
- **Clock & Path Normalization**: Export `SOURCE_DATE_EPOCH` tied to the latest Git commit or changelog timestamp. Strip build paths from DWARF debug symbols using `-ffile-prefix-map=${PWD}=.` and `--remap-path-prefix`.
- **Archive Determinism**: Normalize tar archives using `--sort=name`, `--mtime="@${SOURCE_DATE_EPOCH}"`, `--owner=0 --group=0 --numeric-owner`, and pass `-n` to gzip.
- **Perturbation Testing & Diffing**: Validate builds under altered conditions with `reprotest` and inspect binary divergences with `diffoscope`.
- **Standardized SBOMs & Attestations**: Generate machine-readable SPDX 2.3 and CycloneDX 1.5 JSON inventories containing package URLs (`purl`) and cryptographic hashes. Generate SLSA Level 3 in-toto build provenance statements and verify via Sigstore Cosign/Rekor.

### 3.5 Upstream Release Tracking & Multi-Distro Lifecycle
- **Automated Tracking**: Scan upstream release tags and tarballs via `debian/watch` version 4 and Anitya (release-monitoring.org), automating cryptographic signature validation (`pgpmode=auto`).
- **Patch Queue Lifecycle**: Audit downstream patch series on every new release: drop patches merged upstream, rebase remaining deltas, and forward newly written fixes upstream.
- **Shared Library ABI Transitions**: Verify ABI compatibility before releases using `abi-compliance-checker` or `libabigail` (`abidiff`). On breaking changes, bump the SONAME, create a co-installable package (`libfoo2`), and schedule coordinated rebuilds for reverse dependencies.
- **LTS Security Backporting**: Isolate minimal patch deltas for CVE fixes without introducing new features, refactorings, or ABI breaks.
- **Formal Go/No-Go Readiness Review**: Prohibit releases on unhandled build or test failures on any supported architecture.

---

## 4. Operational Safety Tier Enforcement

Phase 6 enforces the four-tier operational safety policy:
- **Tier 0 (Diagnostics & Auditing)**: Autonomous execution. Inspecting repository metadata, checking GPG signature status, running `diffoscope` diffs, auditing patch series, checking `uscan --dry-run`, and reading build logs (`osc results`, `mock` logs, Koji tasks).
- **Tier 1 (Workspace Builds)**: Autonomous execution. Compiling packages in local workspace directories, rebasing quilt patch queues, updating spec/PKGBUILD files in workspace branches, and generating SBOMs.
- **Tier 2 (Isolated Chroots & Containers)**: Autonomous execution after container/chroot verification. Running isolated builds via `sbuild`, `mock`, `extra-x86_64-build`, `osc build`, or `reprotest`.
- **Tier 3 (Host Mutating & Production Releases)**: **Strictly requires explicit human authorization**. Uploading packages to public production archives (Debian Mentors/FTP, Launchpad PPAs, Fedora Koji/Bodhi, openSUSE Factory), rotating production repository signing keys, executing repository revocations, and filing official Ubuntu SRUs.

---

## 5. Verification & Evaluation Framework

Phase 6 introduces **48 deterministic evaluation scenarios** across eight domains in `evals/`:
- `evals/debian-packaging/scenarios.json` (6 scenarios)
- `evals/ubuntu-packaging/scenarios.json` (6 scenarios)
- `evals/rpm-packaging/scenarios.json` (6 scenarios)
- `evals/fedora-packaging/scenarios.json` (6 scenarios)
- `evals/opensuse-packaging/scenarios.json` (6 scenarios)
- `evals/distribution-engineering/scenarios.json` (6 scenarios)
- `evals/reproducible-builds/scenarios.json` (6 scenarios)
- `evals/release-maintenance/scenarios.json` (6 scenarios)

The evaluation engine `evals/eval_cross_distribution.py` and test suite `tests/test_cross_distribution_evals.py` verify 100% pass rates across all 48 scenarios and test explicit rejection of common packaging anti-patterns (unchecked scriptlets, direct binary PPA uploads, naive package deletions during rollbacks, bundled libraries in Fedora, and volatile timestamps in builds). All tests are integrated into `tests/run_all_tests.py` (62 passing tests total).
