#!/usr/bin/env python3
"""
Linux Cross-Distribution, Release and Supply-Chain Engineering Evaluation Engine
Part of Syswright (Phase 6)

Deterministic evaluation suite that verifies AI agent responses and engineering
recommendations across:
- Debian Packaging (debhelper 13+, DEP-3 quilt patches, sbuild, lintian, autopkgtest)
- Ubuntu Packaging (Launchpad PPAs, Ubuntu delta over Debian, SRU bug workflows, dput)
- RPM Packaging (spec anatomy, scriptlet traps $1=0, file triggers, find-requires/provides)
- Fedora Packaging (Fedora guidelines, SPDX licensing, strict unbundling, mock, Koji, Bodhi)
- openSUSE Packaging (openSUSE spec conventions, Open Build Service, osc CLI, Tumbleweed vs Leap)
- Distribution Engineering (repository layouts, GPG signing, package promotion, atomic rollbacks)
- Reproducible Builds (SOURCE_DATE_EPOCH, diffoscope, reprotest, SPDX/CycloneDX SBOMs, SLSA)
- Release Maintenance (upstream tracking uscan/Anitya, patch lifecycle, ABI transitions, CVE backports)
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def evaluate_cross_distribution_scenario(scenario: Dict[str, Any], response_text: str) -> Tuple[bool, str]:
    """
    Evaluates whether an engineering response satisfies the criteria for
    a specific Linux Cross-Distribution evaluation scenario.
    """
    resp_lower = response_text.lower()
    sid = scenario["id"]
    eval_type = scenario["eval_type"]

    # -------------------------------------------------------------
    # Domain 1: Debian Packaging
    # -------------------------------------------------------------
    if eval_type == "deb_debhelper_compat":
        if "dh $@" not in resp_lower and "dh %" not in resp_lower and "dh " not in resp_lower:
            return False, "Missing recommendation for modern dh $@ sequencer"
        if "debhelper-compat" not in resp_lower and "compat" not in resp_lower and "13" not in resp_lower:
            return False, "Missing debhelper-compat (= 13) declaration"
        if "override_dh_" not in resp_lower:
            return False, "Missing override_dh_* pattern for build customizations"
        return True, "Accurate debhelper 13+ modernization with dh sequencer and overrides"

    elif eval_type == "deb_control_review":
        if "any" not in resp_lower and "architecture: any" not in resp_lower:
            return False, "Missing correction to Architecture: any for compiled shared library"
        if "multi-arch" not in resp_lower or "same" not in resp_lower:
            return False, "Missing Multi-Arch: same declaration for co-installable shared library"
        if "${shlibs:depends}" not in resp_lower and "shlibs:depends" not in resp_lower:
            return False, "Missing dynamic ${shlibs:Depends} substitution variable"
        return True, "Accurate debian/control audit with Multi-Arch and dynamic dependencies"

    elif eval_type == "deb_missing_build_deps":
        if "build-depends" not in resp_lower and "build_depends" not in resp_lower:
            return False, "Missing identification of debian/control Build-Depends requirement"
        if "cmake" not in resp_lower or "ninja" not in resp_lower:
            return False, "Failed to identify missing cmake and ninja-build packages"
        if "chroot" not in resp_lower and "sbuild" not in resp_lower and "clean" not in resp_lower:
            return False, "Missing reference to clean chroot isolation"
        return True, "Accurate diagnosis of missing Build-Depends in clean chroot build"

    elif eval_type == "deb_quilt_dep3_patch":
        if "debian/patches" not in resp_lower and "series" not in resp_lower:
            return False, "Missing debian/patches/series registration"
        if "dep-3" not in resp_lower and "dep3" not in resp_lower and "description" not in resp_lower:
            return False, "Missing DEP-3 patch metadata headers"
        if "quilt" not in resp_lower:
            return False, "Missing quilt patch management tool workflow"
        return True, "Accurate DEP-3 quilt patch authoring and registration"

    elif eval_type == "deb_sbuild_failure":
        if "dbus" not in resp_lower:
            return False, "Missing diagnosis of missing D-Bus session bus"
        if "dbus-run-session" not in resp_lower and "xvfb" not in resp_lower and "session" not in resp_lower:
            return False, "Missing dbus-run-session wrapper recommendation"
        if "override_dh_auto_test" not in resp_lower and "dh_auto_test" not in resp_lower:
            return False, "Missing override_dh_auto_test customization"
        return True, "Accurate sbuild test failure diagnosis with dbus-run-session"

    elif eval_type == "deb_autopkgtest":
        if "debian/tests/control" not in resp_lower and "tests/control" not in resp_lower:
            return False, "Missing debian/tests/control configuration file"
        if "depends: @" not in resp_lower and "@" not in resp_lower and "test" not in resp_lower:
            return False, "Missing Depends: @ test dependency declaration"
        if "install" not in resp_lower and "clean" not in resp_lower and "testbed" not in resp_lower:
            return False, "Missing explanation of testing the installed binary in a clean environment"
        return True, "Accurate autopkgtest configuration and installed binary verification"

    # -------------------------------------------------------------
    # Domain 2: Ubuntu Packaging
    # -------------------------------------------------------------
    elif eval_type == "ubu_ppa_preparation":
        if "source" not in resp_lower and "debuild -s" not in resp_lower and "-s" not in resp_lower:
            return False, "Missing source-only build instruction (debuild -S or dpkg-buildpackage -S)"
        if "sign" not in resp_lower and "gpg" not in resp_lower:
            return False, "Missing GPG signing step for Launchpad source changes"
        if "dput" not in resp_lower or "ppa:" not in resp_lower:
            return False, "Missing dput ppa upload command"
        return True, "Accurate Launchpad PPA source preparation, signing, and dput upload"

    elif eval_type == "ubu_delta_review":
        if "ubuntu-diff" not in resp_lower and "debdiff" not in resp_lower and "diff" not in resp_lower:
            return False, "Missing debdiff / ubuntu-diff delta inspection tool"
        if "ubuntu1" not in resp_lower and "version" not in resp_lower:
            return False, "Missing Ubuntu versioning convention (e.g., 2.1.0-2ubuntu1)"
        if "minimize" not in resp_lower and "upstream" not in resp_lower and "sync" not in resp_lower:
            return False, "Missing principle of minimizing delta and upstreaming fixes"
        return True, "Accurate Ubuntu delta audit, versioning, and synchronization review"

    elif eval_type == "ubu_sru_bug_template":
        if "[impact]" not in resp_lower and "impact" not in resp_lower:
            return False, "Missing mandatory [Impact] SRU section"
        if "[test plan]" not in resp_lower and "test plan" not in resp_lower:
            return False, "Missing mandatory [Test Plan] SRU section"
        if "[where problems could occur]" not in resp_lower and "where problems could occur" not in resp_lower:
            return False, "Missing mandatory [Where problems could occur] SRU section"
        if "proposed" not in resp_lower and "7" not in resp_lower and "aging" not in resp_lower:
            return False, "Missing reference to proposed pocket verification or aging period"
        return True, "Accurate Stable Release Update (SRU) bug report documentation"

    elif eval_type == "ubu_series_targeting":
        if "unstable" not in resp_lower:
            return False, "Failed to identify that 'unstable' is not a valid Ubuntu target"
        if "noble" not in resp_lower and "jammy" not in resp_lower and "series" not in resp_lower and "codename" not in resp_lower:
            return False, "Missing recommendation to target specific Ubuntu series codename"
        if "changelog" not in resp_lower:
            return False, "Missing debian/changelog correction requirement"
        return True, "Accurate diagnosis of Launchpad suite rejection and series targeting"

    elif eval_type == "ubu_launchpad_multiarch":
        if "time_t" not in resp_lower and "t64" not in resp_lower and "2038" not in resp_lower:
            return False, "Missing identification of 64-bit time_t (t64) Year 2038 transition on 32-bit armhf"
        if "armhf" not in resp_lower and "32-bit" not in resp_lower:
            return False, "Missing reference to 32-bit architecture constraints"
        if "format" not in resp_lower and "cast" not in resp_lower and "specifier" not in resp_lower:
            return False, "Missing code remediation for format string specifier"
        return True, "Accurate diagnosis of armhf 64-bit time_t compiler error"

    elif eval_type == "ubu_sync_merge_conflict":
        if "minimize" not in resp_lower and "upstream" not in resp_lower:
            return False, "Missing obligation to minimize delta and forward patches to Debian"
        if "apparmor" not in resp_lower and "ubuntu" not in resp_lower and "delta" not in resp_lower:
            return False, "Missing identification of genuine Ubuntu-specific requirements"
        if "changelog" not in resp_lower:
            return False, "Missing documentation of merge rationale in debian/changelog"
        return True, "Accurate resolution principles for Debian-Ubuntu merge conflicts"

    # -------------------------------------------------------------
    # Domain 3: RPM Packaging Core
    # -------------------------------------------------------------
    elif eval_type == "rpm_spec_review":
        if "%{_bindir}" not in resp_lower and "_bindir" not in resp_lower:
            return False, "Missing standard RPM directory macro %{_bindir}"
        if "%cmake_build" not in resp_lower and "%make_build" not in resp_lower and "build" not in resp_lower:
            return False, "Missing standard RPM build macro (%make_build or %cmake_build)"
        if "%config(noreplace)" not in resp_lower and "%config" not in resp_lower and "%license" not in resp_lower:
            return False, "Missing %config(noreplace) or %license file attribute in %files"
        return True, "Accurate spec file audit and macro modernization"

    elif eval_type == "rpm_dependency_generation":
        if "find-requires" not in resp_lower and "find-provides" not in resp_lower and "automatic" not in resp_lower:
            return False, "Missing identification of RPM automatic dependency generator"
        if "manual" not in resp_lower and "redundant" not in resp_lower and "anti-pattern" not in resp_lower:
            return False, "Missing recognition that manual library Requires are redundant/anti-patterns"
        if "soname" not in resp_lower and "library" not in resp_lower and "elf" not in resp_lower:
            return False, "Missing explanation of ELF dynamic linker soname scanning"
        return True, "Accurate explanation of automatic RPM dependency generation"

    elif eval_type == "rpm_scriptlet_trap":
        if "$1" not in resp_lower and "argument" not in resp_lower:
            return False, "Missing analysis of scriptlet $1 argument semantics"
        if "upgrade" not in resp_lower or "uninstall" not in resp_lower:
            return False, "Missing explanation of RPM upgrade execution order"
        if "%systemd_preun" not in resp_lower and "0" not in resp_lower and "file trigger" not in resp_lower:
            return False, "Missing remediation using $1 == 0 check or %systemd_preun macro"
        return True, "Accurate diagnosis of RPM scriptlet upgrade trap and remediation"

    elif eval_type == "rpm_split_package":
        if "%package devel" not in resp_lower and "devel" not in resp_lower:
            return False, "Missing %package devel subpackage definition"
        if "%{?_isa}" not in resp_lower and "_isa" not in resp_lower:
            return False, "Missing architecture-bound dependency macro %{?_isa}"
        if ".so" not in resp_lower or ("header" not in resp_lower and ".h" not in resp_lower and "include" not in resp_lower):
            return False, "Missing separation of runtime .so.1* from devel .so symlinks/headers"
        return True, "Accurate split subpackage design with architecture-bound dependencies"

    elif eval_type == "rpm_version_syntax":
        if "~" not in resp_lower and "tilde" not in resp_lower:
            return False, "Missing recommendation for tilde (~) pre-release sorting syntax"
        if "newer" not in resp_lower and "sort" not in resp_lower and "downgrade" not in resp_lower:
            return False, "Missing explanation of alphabetical sorting rules in RPM"
        return True, "Accurate analysis of RPM version sorting and pre-release tilde syntax"

    elif eval_type == "rpm_rpmsign_verification":
        if "rpmsign" not in resp_lower and "rpm --addsign" not in resp_lower:
            return False, "Missing rpmsign --addsign command"
        if "rpm -kv" not in resp_lower and "checksig" not in resp_lower and "verify" not in resp_lower:
            return False, "Missing signature verification command (rpm -Kv or rpm --checksig)"
        if "gpg" not in resp_lower and "key" not in resp_lower:
            return False, "Missing reference to GPG key management"
        return True, "Accurate RPM package signing and verification workflow"

    # -------------------------------------------------------------
    # Domain 4: Fedora Packaging
    # -------------------------------------------------------------
    elif eval_type == "fed_fedora_spec_prep":
        if "%autorelease" not in resp_lower and "autorelease" not in resp_lower:
            return False, "Missing Release: %autorelease macro"
        if "%autochangelog" not in resp_lower and "autochangelog" not in resp_lower:
            return False, "Missing %autochangelog in %changelog section"
        if "spdx" not in resp_lower and "license" not in resp_lower:
            return False, "Missing valid SPDX license identifier"
        return True, "Accurate Fedora spec preparation meeting current packaging guidelines"

    elif eval_type == "fed_mock_failure":
        if "mock" not in resp_lower:
            return False, "Missing mock clean chroot build tool"
        if "build.log" not in resp_lower and "root.log" not in resp_lower and "log" not in resp_lower:
            return False, "Missing inspection of mock build.log or root.log"
        if "buildrequires" not in resp_lower:
            return False, "Missing identification of undeclared BuildRequires"
        return True, "Accurate mock chroot failure diagnosis and BuildRequires resolution"

    elif eval_type == "fed_unbundling_enforcement":
        if "unbundl" not in resp_lower and "bundle" not in resp_lower:
            return False, "Missing reference to Fedora strict unbundling policy"
        if "buildrequires" not in resp_lower:
            return False, "Missing addition of system library BuildRequires"
        if "%prep" not in resp_lower and "rm " not in resp_lower and "delete" not in resp_lower:
            return False, "Missing source stripping in %prep section"
        return True, "Accurate enforcement of Fedora strict unbundling policy"

    elif eval_type == "fed_koji_build":
        if "koji" not in resp_lower and "scratch-build" not in resp_lower:
            return False, "Missing fedpkg scratch-build or koji command"
        if "architecture" not in resp_lower and "arch" not in resp_lower:
            return False, "Missing analysis of multi-architecture builder logs"
        if "task" not in resp_lower and "log" not in resp_lower:
            return False, "Missing task log inspection"
        return True, "Accurate Koji scratch build and multi-arch verification"

    elif eval_type == "fed_bodhi_update":
        if "bodhi" not in resp_lower and "fedpkg update" not in resp_lower:
            return False, "Missing Bodhi update submission command"
        if "testing" not in resp_lower or "updates-testing" not in resp_lower:
            return False, "Missing reference to updates-testing staging repository"
        if "karma" not in resp_lower and "aging" not in resp_lower and "7" not in resp_lower:
            return False, "Missing gating criteria (positive karma or aging days)"
        return True, "Accurate Bodhi update creation and gating verification"

    elif eval_type == "fed_epel_compatibility":
        if "0%{?rhel}" not in resp_lower and "rhel" not in resp_lower:
            return False, "Missing conditional macro 0%{?rhel} for EPEL targeting"
        if "cmake" not in resp_lower and "toolchain" not in resp_lower and "buildrequires" not in resp_lower:
            return False, "Missing accommodation for EPEL toolchain differences"
        return True, "Accurate spec structure for Fedora and EPEL cross-compatibility"

    # -------------------------------------------------------------
    # Domain 5: openSUSE Packaging
    # -------------------------------------------------------------
    elif eval_type == "suse_opensuse_spec":
        if "%cmake_build" not in resp_lower and "%cmake" not in resp_lower:
            return False, "Missing openSUSE %cmake or %cmake_build macro"
        if "%service_add_" not in resp_lower and "%service_" not in resp_lower and "systemd" not in resp_lower:
            return False, "Missing openSUSE systemd macros (%service_add_post, etc.)"
        if "%ctest" not in resp_lower and "%check" not in resp_lower:
            return False, "Missing %ctest macro in %check section"
        return True, "Accurate openSUSE spec authoring with native macros"

    elif eval_type == "suse_obs_failure":
        if "osc results" not in resp_lower and "results" not in resp_lower:
            return False, "Missing osc results status command"
        if "osc buildlog" not in resp_lower and "osc log" not in resp_lower and "buildlog" not in resp_lower:
            return False, "Missing osc buildlog/log command"
        return True, "Accurate OBS build failure diagnosis using osc CLI"

    elif eval_type == "suse_repo_config":
        if "osc meta prj" not in resp_lower and "meta prj" not in resp_lower:
            return False, "Missing osc meta prj project configuration command"
        if "<repository" not in resp_lower and "repository" not in resp_lower:
            return False, "Missing <repository> target definitions in OBS project XML"
        if "tumbleweed" not in resp_lower and "leap" not in resp_lower:
            return False, "Missing reference to openSUSE distribution targets"
        return True, "Accurate multi-distribution project configuration in OBS"

    elif eval_type == "suse_osc_workflow":
        if "osc branch" not in resp_lower:
            return False, "Missing osc branch command"
        if "osc build" not in resp_lower:
            return False, "Missing osc build local chroot test command"
        if "osc sr" not in resp_lower and "submitrequest" not in resp_lower:
            return False, "Missing osc submitrequest / osc sr command"
        return True, "Accurate end-to-end osc package development and submission workflow"

    elif eval_type == "suse_soname_naming":
        if "libxyz2" not in resp_lower:
            return False, "Missing strict package naming libxyz2 matching SONAME"
        if "libxyz-devel" not in resp_lower and "devel" not in resp_lower:
            return False, "Missing separate libxyz-devel subpackage"
        if "parallel" not in resp_lower and "co-install" not in resp_lower and "soname" not in resp_lower:
            return False, "Missing rationale of parallel co-installability of shared library ABIs"
        return True, "Accurate enforcement of openSUSE shared library policy"

    elif eval_type == "suse_tumbleweed_leap":
        if "0%{?suse_version}" not in resp_lower and "suse_version" not in resp_lower:
            return False, "Missing 0%{?suse_version} conditional macro check"
        if "1500" not in resp_lower and "leap" not in resp_lower:
            return False, "Missing version boundary comparison for Leap (<= 1500) vs Tumbleweed (> 1500)"
        return True, "Accurate reconciliation of spec file for Tumbleweed and Leap"

    # -------------------------------------------------------------
    # Domain 6: Linux Distribution Engineering
    # -------------------------------------------------------------
    elif eval_type == "dist_signed_repo_design":
        if "offline" not in resp_lower or "master" not in resp_lower:
            return False, "Missing offline master key security architecture"
        if "inrelease" not in resp_lower and "repomd.xml.asc" not in resp_lower and "sign" not in resp_lower:
            return False, "Missing top-level metadata signature specification"
        if "subkeys" not in resp_lower and "rotation" not in resp_lower and "expir" not in resp_lower:
            return False, "Missing subkey rotation and expiration schedule"
        return True, "Accurate cryptographically signed repository design and key hierarchy"

    elif eval_type == "dist_invalid_metadata":
        if "race" not in resp_lower and "sync" not in resp_lower and "order" not in resp_lower:
            return False, "Missing diagnosis of out-of-order mirror synchronization race condition"
        if "pool" not in resp_lower or "metadata" not in resp_lower or "order" not in resp_lower:
            return False, "Missing two-stage sync order (packages first, metadata second)"
        if "by-hash" not in resp_lower and "hash" not in resp_lower and "rsync" not in resp_lower:
            return False, "Missing recommendation for by-hash layout or rsync sequencing"
        return True, "Accurate diagnosis of mirror synchronization race condition and by-hash fix"

    elif eval_type == "dist_staged_promotion":
        if "staging" not in resp_lower and "stage" not in resp_lower and "dev" not in resp_lower:
            return False, "Missing multi-stage promotion pipeline (dev -> staging -> production)"
        if "rebuild" not in resp_lower and "identical" not in resp_lower and "same" not in resp_lower:
            return False, "Missing principle of promoting identical binary artifacts without rebuilding"
        if "atomic" not in resp_lower or "symlink" not in resp_lower and "rename" not in resp_lower:
            return False, "Missing atomic metadata update mechanism (symlink swap or directory rename)"
        return True, "Accurate staged package promotion and atomic metadata replacement"

    elif eval_type == "dist_upgrade_analysis":
        if "conffile" not in resp_lower and "ucf" not in resp_lower and "%config" not in resp_lower:
            return False, "Missing configuration file upgrade management (ucf or %config(noreplace))"
        if "breaks" not in resp_lower and "replaces" not in resp_lower and "obsoletes" not in resp_lower and "conflict" not in resp_lower:
            return False, "Missing file collision resolution (Breaks/Replaces or Obsoletes/Conflicts)"
        return True, "Accurate upgrade failure analysis and conffile collision resolution"

    elif eval_type == "dist_rollback_strategy":
        if ("delet" not in resp_lower and "remov" not in resp_lower) or ("break" not in resp_lower and "fail" not in resp_lower) or "404" not in resp_lower:
            return False, "Missing explanation of why deleting packages breaks client caches"
        if "epoch" not in resp_lower and "fast-forward" not in resp_lower and "revert" not in resp_lower:
            return False, "Missing epoch bump or fast-forward revert package strategy"
        if "snapshot" not in resp_lower and "downgrade" not in resp_lower and "distro-sync" not in resp_lower:
            return False, "Missing repository snapshot rollback or client downgrade command"
        return True, "Accurate emergency repository rollback and client downgrade strategy"

    elif eval_type == "dist_solver_validation":
        if "dose" not in resp_lower and "sat" not in resp_lower and "solver" not in resp_lower:
            return False, "Missing SAT solver dependency tool (e.g., dose-distcheck)"
        if "repoquery" not in resp_lower and "unsolved" not in resp_lower and "check" not in resp_lower:
            return False, "Missing RPM repository solver query (dnf repoquery --unsolved)"
        return True, "Accurate repository dependency validation using formal SAT solvers"

    # -------------------------------------------------------------
    # Domain 7: Reproducible Builds
    # -------------------------------------------------------------
    elif eval_type == "repro_timestamp_diagnosis":
        if "__date__" not in resp_lower and "__time__" not in resp_lower and "timestamp" not in resp_lower:
            return False, "Missing identification of __DATE__/__TIME__ or wall-clock non-determinism"
        if "source_date_epoch" not in resp_lower:
            return False, "Missing SOURCE_DATE_EPOCH environment variable specification"
        return True, "Accurate diagnosis of timestamp non-determinism and SOURCE_DATE_EPOCH remediation"

    elif eval_type == "repro_diffoscope_analysis":
        if "readdir" not in resp_lower and "sort" not in resp_lower and "order" not in resp_lower:
            return False, "Missing diagnosis of filesystem traversal readdir non-determinism"
        if "umask" not in resp_lower and "permission" not in resp_lower:
            return False, "Missing identification of umask permission variances"
        if "--sort=name" not in resp_lower and "sort" not in resp_lower:
            return False, "Missing tar --sort=name normalization flag"
        return True, "Accurate diffoscope analysis and archive normalization flags"

    elif eval_type == "repro_build_path_mapping":
        if "-ffile-prefix-map" not in resp_lower and "-fdebug-prefix-map" not in resp_lower and "prefix-map" not in resp_lower:
            return False, "Missing compiler flag -ffile-prefix-map=${PWD}=."
        if "debug" not in resp_lower and "dwarf" not in resp_lower and "path" not in resp_lower:
            return False, "Missing identification of absolute build paths embedded in DWARF debug symbols"
        return True, "Accurate remediation of build path non-determinism via prefix mapping"

    elif eval_type == "repro_sbom_validation":
        if "spdx" not in resp_lower and "cyclonedx" not in resp_lower:
            return False, "Missing reference to SPDX 2.3/3.0 or CycloneDX 1.5 standard"
        if "purl" not in resp_lower and "hash" not in resp_lower and "sha256" not in resp_lower:
            return False, "Missing requirement for Package URLs (purl) or cryptographic hashes"
        if "syft" not in resp_lower and "spdx-tools" not in resp_lower and "tool" not in resp_lower:
            return False, "Missing SBOM generation or validation tooling"
        return True, "Accurate SBOM structure, generation, and validation specification"

    elif eval_type == "repro_slsa_provenance":
        if "in-toto" not in resp_lower and "slsa" not in resp_lower and "provenance" not in resp_lower:
            return False, "Missing in-toto / SLSA provenance attestation format"
        if "commit" not in resp_lower and "digest" not in resp_lower and "sha" not in resp_lower:
            return False, "Missing cryptographic binding to git commit and artifact digest"
        if "verify" not in resp_lower or "cosign" not in resp_lower and "slsa-verifier" not in resp_lower and "rekor" not in resp_lower:
            return False, "Missing verification mechanism via slsa-verifier, Cosign, or Rekor"
        return True, "Accurate SLSA Level 3 build provenance and verification workflow"

    elif eval_type == "repro_untrusted_env":
        if "lc_all" not in resp_lower and "locale" not in resp_lower:
            return False, "Missing locale normalization (LC_ALL=C.UTF-8)"
        if "tz=" not in resp_lower and "timezone" not in resp_lower and "utc" not in resp_lower:
            return False, "Missing timezone normalization (TZ=UTC)"
        if "umask" not in resp_lower and "random" not in resp_lower:
            return False, "Missing umask or compiler random seed sanitization"
        return True, "Accurate environment sanitization for reproducible compilation"

    # -------------------------------------------------------------
    # Domain 8: Release Maintenance
    # -------------------------------------------------------------
    elif eval_type == "rel_rebase_patch_series":
        if "drop" not in resp_lower and "remove" not in resp_lower:
            return False, "Missing identification to drop already-merged upstream patches"
        if "quilt" not in resp_lower and "git am" not in resp_lower and "rebase" not in resp_lower:
            return False, "Missing patch rebasing workflow using quilt or git"
        if "changelog" not in resp_lower:
            return False, "Missing changelog documentation requirement"
        return True, "Accurate patch queue audit, rebasing, and pruning workflow"

    elif eval_type == "rel_upstream_security_backport":
        if "minimal" not in resp_lower and "isolate" not in resp_lower:
            return False, "Missing principle of isolating minimal patch delta"
        if "abi" not in resp_lower and "api" not in resp_lower and "compatib" not in resp_lower:
            return False, "Missing requirement to preserve binary ABI/API compatibility in LTS"
        if "test" not in resp_lower and "regression" not in resp_lower:
            return False, "Missing addition of regression test verifying exploit mitigation"
        return True, "Accurate security CVE backporting methodology for LTS release"

    elif eval_type == "rel_abi_transition":
        if "abi-compliance-checker" not in resp_lower and "libabigail" not in resp_lower and "abidiff" not in resp_lower:
            return False, "Missing ABI verification tool (abi-compliance-checker or abidiff)"
        if "libdata4" not in resp_lower and "rename" not in resp_lower and "new package" not in resp_lower:
            return False, "Missing creation of new package name matching new SONAME"
        if "rebuild" not in resp_lower or "reverse" not in resp_lower:
            return False, "Missing coordinated rebuild scheduling for reverse dependencies"
        return True, "Accurate shared library ABI transition and rebuild coordination"

    elif eval_type == "rel_multi_distro_coordination":
        if "tag" not in resp_lower and "tarball" not in resp_lower:
            return False, "Missing unified upstream release tag and source tarball"
        if "pkgbuild" not in resp_lower or "debian" not in resp_lower or "spec" not in resp_lower:
            return False, "Missing synchronization across PKGBUILD, debian/, and RPM spec files"
        if "matrix" not in resp_lower and "container" not in resp_lower and "build" not in resp_lower:
            return False, "Missing multi-distribution matrix verification testing"
        return True, "Accurate multi-distribution synchronized release coordination"

    elif eval_type == "rel_upstream_watch":
        if "debian/watch" not in resp_lower and "watch" not in resp_lower:
            return False, "Missing debian/watch file specification"
        if "anitya" not in resp_lower and "release-monitoring" not in resp_lower and "upstream" not in resp_lower:
            return False, "Missing Anitya / release-monitoring.org upstream tracking"
        if "pgpmode" not in resp_lower and "signature" not in resp_lower and "gpg" not in resp_lower:
            return False, "Missing automated upstream cryptographic signature verification"
        return True, "Accurate upstream release watch configuration and signature verification"

    elif eval_type == "rel_release_readiness_gate":
        if "go" not in resp_lower and "gate" not in resp_lower and "decision" not in resp_lower:
            return False, "Missing structured Go/No-Go release readiness gate"
        if "block" not in resp_lower and "abort" not in resp_lower and "fail" not in resp_lower:
            return False, "Missing strict blocking of release on unhandled test failure"
        if "lintian" not in resp_lower and "rpmlint" not in resp_lower and "linter" not in resp_lower:
            return False, "Missing linter compliance requirement prior to release sign-off"
        return True, "Accurate Go/No-Go release readiness evaluation and blocking criteria"

    return False, f"Unhandled evaluation scenario type: {eval_type}"


def get_reference_cross_distribution_responses() -> Dict[str, str]:
    """
    Returns reference engineering responses that satisfy all 48 Phase 6
    cross-distribution evaluation scenarios.
    """
    return {
        # Domain 1: Debian Packaging
        "eval_deb_01_debhelper_compat": (
            "Modernize the legacy debian/rules file by adopting the standard modern debhelper sequencer: "
            "`#!/usr/bin/make -f \n %: \n\t dh $@`. Replace obsolete debian/compat file with "
            "`debhelper-compat (= 13)` in Build-Depends inside debian/control. Replace manual configuration "
            "and test scripts by implementing structured override targets: `override_dh_auto_configure:` "
            "passing custom cmake flags, and `override_dh_auto_test:` to invoke the project test runner."
        ),
        "eval_deb_02_control_review": (
            "Audit findings and corrections for debian/control: \n"
            "1. Architecture Tag: A compiled shared library (.so) must use `Architecture: any` (not 'all', which is strictly for architecture-independent data/scripts). \n"
            "2. Multi-Arch Declaration: Add `Multi-Arch: same` so that 32-bit and 64-bit library packages can be co-installed simultaneously in multiarch paths (`/usr/lib/${DEB_HOST_MULTIARCH}/`). \n"
            "3. Dynamic Dependencies: Remove hardcoded `Depends: libc6, libssl3` anti-pattern. Replace with dynamic substitutions: `Depends: ${shlibs:Depends}, ${misc:Depends}` to let dpkg-shlibdeps compute exact library dependencies automatically."
        ),
        "eval_deb_03_missing_build_deps": (
            "The package failed in sbuild because sbuild compiles inside a clean, minimal chroot that only contains "
            "`build-essential` and packages explicitly declared in Build-Depends. The developer host had cmake and ninja installed globally. \n"
            "Resolution: Add `cmake` and `ninja-build` to `Build-Depends:` in `debian/control`. Verify the fix by executing an isolated `sbuild` chroot build."
        ),
        "eval_deb_04_quilt_dep3_patch": (
            "To backport the upstream fix using quilt: \n"
            "1. Initialize new patch: `quilt new 0001-fix-null-deref-parser.patch`. \n"
            "2. Edit `parser.c` to fix the dereference, then run `quilt refresh`. \n"
            "3. Register the patch in `debian/patches/series`. \n"
            "4. Add mandatory DEP-3 patch metadata headers at the top of the patch file: \n"
            "   Description: Fix NULL pointer dereference in parser.c \n"
            "   Author: Jane Engineer <jane@example.org> \n"
            "   Origin: upstream, https://github.com/example/lib/commit/abc1234 \n"
            "   Bug-Debian: https://bugs.debian.org/123456 \n"
            "   Forwarded: not-needed"
        ),
        "eval_deb_05_sbuild_failure": (
            "The test failure occurred because isolated sbuild chroots run headlessly without a running D-Bus session bus daemon. \n"
            "Remediation: \n"
            "1. Add `dbus` to `Build-Depends` in `debian/control`. \n"
            "2. In `debian/rules`, implement an override target: \n"
            "   `override_dh_auto_test: \n\t dbus-run-session dh_auto_test` \n"
            "`dbus-run-session` automatically spawns an ephemeral session bus for the test suite and terminates cleanly on completion."
        ),
        "eval_deb_06_autopkgtest": (
            "Configure autopkgtest DEP-8 testing by creating `debian/tests/control`: \n"
            "```text\n"
            "Tests: smoke-test\n"
            "Depends: @\n"
            "Restrictions: allow-stderr\n"
            "```\n"
            "The `Depends: @` declaration instructs the runner to install the freshly built binary package from the archive. "
            "Autopkgtest runs tests in a clean testbed VM or container, verifying that the installed binary executes properly and links correctly in a real operating environment rather than testing the local source build tree."
        ),

        # Domain 2: Ubuntu Packaging
        "eval_ubu_01_ppa_preparation": (
            "To distribute an application on Ubuntu via Launchpad PPA: \n"
            "1. Prepare source-only package: Run `debuild -S -sa` or `dpkg-buildpackage -S -sa`. Launchpad strictly requires source-only uploads; binary packages built locally are rejected. \n"
            "2. Sign the generated `.changes` and `.dsc` files with your GPG key registered on Launchpad: `debsign <package>_source.changes`. \n"
            "3. Upload the package to the PPA using dput: `dput ppa:myteam/myppa <package>_source.changes`. Launchpad build daemons will compile the binaries in clean virtualized chroots across all enabled architectures."
        ),
        "eval_ubu_02_delta_review": (
            "Procedure to review Ubuntu delta against new Debian 2.1.0-2: \n"
            "1. Run `debdiff` or `ubuntu-diff` to compare the Ubuntu packaging with the new Debian release. \n"
            "2. Check if the Ubuntu-specific patches were merged upstream into Debian 2.1.0-2. If Debian merged the fix, the delta is eliminated; request a direct sync from Debian. \n"
            "3. If Ubuntu-specific changes must remain (e.g., Ubuntu paths or AppArmor profile), rebase the delta and apply Ubuntu versioning convention: `2.1.0-2ubuntu1`. Minimize delta whenever possible by forwarding remaining patches to Debian Salsa."
        ),
        "eval_ubu_03_sru_bug_template": (
            "A formal Stable Release Update (SRU) requires a Launchpad bug report structured with mandatory sections: \n"
            "- [Impact]: Detailed explanation of the bug, user-visible symptoms, and why this fix qualifies under SRU policy. \n"
            "- [Test Plan]: Step-by-step reproduction instructions detailing how to demonstrate the failure on an unpatched system, and how to verify that the fix resolves the issue. \n"
            "- [Where problems could occur]: Risk analysis detailing potential regressions, affected interfaces, and mitigation strategies. \n"
            "Once uploaded, the package must spend a mandatory 7-day aging period in `noble-proposed` with community testing before being promoted to `noble-updates`."
        ),
        "eval_ubu_04_series_targeting": (
            "Cause: Launchpad rejected the upload because `debian/changelog` targeted Debian suite 'unstable' (Sid). Launchpad only accepts uploads targeting active Ubuntu series codenames. \n"
            "Remediation: Update `debian/changelog` header to target the intended Ubuntu series: change `myapp (1.2.3-1) unstable; urgency=medium` to `myapp (1.2.3-1ubuntu1) noble; urgency=medium`. Rebuild the source package with `debuild -S` and re-upload with `dput`."
        ),
        "eval_ubu_05_launchpad_multiarch": (
            "Cause: In Ubuntu 24.04 LTS (Noble) and Debian Trixie, the 64-bit time_t transition (t64) was implemented to solve the Year 2038 problem on 32-bit architectures. On `armhf`, `time_t` is now a 64-bit `long long int` instead of a 32-bit `long int`. Passing `%ld` to printf causes a compiler format error under `-Werror=format`. \n"
            "Fix: Update code to cast `time_t` or use `intmax_t` with `%jd`, e.g., `printf(\"%jd\", (intmax_t)ts);`."
        ),
        "eval_ubu_06_sync_merge_conflict": (
            "When resolving Debian-Ubuntu merge conflicts: \n"
            "1. Maintainers have an affirmative obligation to minimize delta. Drop any Ubuntu patch that has been adopted or rendered obsolete by Debian. \n"
            "2. Preserve only genuine Ubuntu-specific deltas, such as AppArmor integrations, Ubuntu default configuration overrides, or Launchpad multi-arch transitions. \n"
            "3. Clearly document all kept deltas in `debian/changelog` under the new version header, and submit remaining patches upstream to Debian."
        ),

        # Domain 3: RPM Packaging Core
        "eval_rpm_01_spec_review": (
            "Refactor the spec file to adhere to standard RPM conventions: \n"
            "1. Replace hardcoded filesystem paths with RPM standard path macros: use `%{_bindir}` instead of `/usr/bin`, `%{_sysconfdir}` instead of `/etc`, and `%{_datadir}` instead of `/usr/share`. \n"
            "2. Replace manual compilation commands in `%build` and `%install` with standard build macros: `%cmake_build` (or `%make_build`) and `%cmake_install` (or `%make_install`). \n"
            "3. In the `%files` section, mark configuration files with `%config(noreplace) %{_sysconfdir}/myapp.conf` and license files with `%license LICENSE`."
        ),
        "eval_rpm_02_dependency_generation": (
            "Manual library Requires (`Requires: libc.so.6, libssl.so.3`) are an anti-pattern in RPM packaging. "
            "During the build process, `rpmbuild` automatically runs `find-requires` and `find-provides` on all compiled ELF binaries. "
            "It scans DT_NEEDED dynamic tags and automatically injects accurate, architecture-qualified SONAME requires (`libc.so.6(GLIBC_2.34)(64bit)`). "
            "Manual soname requires should be removed entirely, reserving manual `Requires:` only for package-level or capability requirements."
        ),
        "eval_rpm_03_scriptlet_trap": (
            "RPM scriptlet execution order during package upgrade from version 1.0 to 1.1: \n"
            "1. New package `%pre` (arg 2) \n"
            "2. New package files installed \n"
            "3. New package `%post` (arg 2) \n"
            "4. OLD package `%preun` (arg 1) \n"
            "5. OLD package files removed \n"
            "6. OLD package `%postun` (arg 1) \n"
            "Because the scriptlet ran `systemctl stop` in `%preun` without checking `$1`, when the OLD package uninstalled, it stopped the newly upgraded service! \n"
            "Fix: Add `$1 == 0` check (only stop service on complete package removal, not upgrade): \n"
            "`if [ $1 -eq 0 ]; then systemctl --no-reload disable --now myapp.service; fi` or adopt standard `%systemd_preun myapp.service` macros."
        ),
        "eval_rpm_04_split_package": (
            "Structure the split RPM spec file as follows: \n"
            "```spec\n"
            "Name: libbar\n"
            "...\n"
            "%package devel\n"
            "Summary: Development files for libbar\n"
            "Requires: %{name}%{?_isa} = %{version}-%{release}\n"
            "\n"
            "%files\n"
            "%{_libdir}/libbar.so.1*\n"
            "\n"
            "%files devel\n"
            "%{_includedir}/bar.h\n"
            "%{_libdir}/libbar.so\n"
            "%{_libdir}/pkgconfig/bar.pc\n"
            "```\n"
            "The `%{?_isa}` macro binds the `-devel` subpackage strictly to the exact architecture (e.g. x86_64) and version-release of the base library package, preventing architecture mismatches. "
            "This separates runtime shared libraries in the base package from development headers and .so symlinks in the -devel package."
        ),
        "eval_rpm_05_version_syntax": (
            "In RPM version comparison rules, alphabetic characters sort after nothing. Therefore, `2.0.0alpha1` is evaluated by RPM as NEWER than `2.0.0`, meaning upgrading to the final release would be rejected as a downgrade! \n"
            "Solution: Use the tilde (`~`) operator, which RPM explicitly sorts BEFORE everything (including empty strings): \n"
            "`Version: 2.0.0~alpha1` (or set `Version: 2.0.0` with `Release: 0.1.alpha1%{?dist}`). When `Version: 2.0.0` is released, RPM correctly recognizes `2.0.0 > 2.0.0~alpha1`."
        ),
        "eval_rpm_06_rpmsign_verification": (
            "To sign RPM packages and verify integrity: \n"
            "1. Sign the built RPM artifact using GPG: `rpmsign --addsign --key-id=<KEY_ID> myapp-1.2.3-1.fc40.x86_64.rpm`. \n"
            "2. Verify the cryptographic signature: `rpm -Kv myapp-1.2.3-1.fc40.x86_64.rpm` (or `rpm --checksig`). \n"
            "3. Client verification: Import the public GPG key into the rpmdb with `rpm --import RPM-GPG-KEY-example` so that DNF automatically verifies signatures prior to package installation."
        ),

        # Domain 4: Fedora Packaging
        "eval_fed_01_fedora_spec_prep": (
            "A spec file conforming to modern Fedora Packaging Guidelines must: \n"
            "1. Use rpmautospec macros: `Release: %autorelease` and end with `%changelog \n %autochangelog`. \n"
            "2. Declare a valid SPDX license identifier: e.g., `License: Apache-2.0` (legacy license strings like 'ASL 2.0' are obsolete). \n"
            "3. Omit obsolete tags: Remove `Group:`, `BuildRoot:`, `%clean` section, and `rm -rf %{buildroot}` at the start of `%install`."
        ),
        "eval_fed_02_mock_failure": (
            "Diagnosis workflow using mock: \n"
            "1. Mock builds in an isolated, minimal chroot (`fedora-rawhide-x86_64`). \n"
            "2. Inspect `build.log` in the mock result directory to identify the exact compiler error and missing header. \n"
            "3. Check `root.log` to audit installed packages and verify what dependencies were pulled in. \n"
            "4. Add the missing header package (e.g. `BuildRequires: foo-devel`) to the spec file and re-test with `mock -r fedora-rawhide-x86_64 <package>.src.rpm`."
        ),
        "eval_fed_03_unbundling_enforcement": (
            "Fedora packaging policy strictly prohibits bundled third-party libraries: \n"
            "1. In `%prep`, remove all vendored/bundled source directories: `rm -rf vendor/sqlite3 vendor/cjson vendor/zlib`. \n"
            "2. Add system development libraries to the spec preamble: `BuildRequires: sqlite-devel`, `BuildRequires: cjson-devel`, `BuildRequires: zlib-ng-compat-devel`. \n"
            "3. Pass configuration options (or patch CMake/Meson) to ensure the build links dynamically against system shared libraries."
        ),
        "eval_fed_04_koji_build": (
            "To test across all architectures using Koji before committing to dist-git: \n"
            "1. Submit a scratch build: `fedpkg scratch-build --srpm` or `koji build --scratch rawhide <package>.src.rpm`. \n"
            "2. Monitor task progression and inspect per-architecture build.log files for x86_64, aarch64, s390x, and ppc64le. \n"
            "3. Ensure all architecture task builders succeed before pushing git commits to dist-git."
        ),
        "eval_fed_05_bodhi_update": (
            "Submitting and gating updates in Fedora via Bodhi: \n"
            "1. After successful Koji build, create update: `fedpkg update` (or submit via Bodhi CLI/web UI). \n"
            "2. Specify update type (`bugfix`, `security`, or `enhancement`) and link relevant Red Hat Bugzilla IDs. \n"
            "3. Gating criteria: The update is pushed to `updates-testing`. It must pass automated openQA test suites and reach the required karma threshold (+3 karma from testers) or satisfy the mandatory 7-day testing aging window before pushing to stable."
        ),
        "eval_fed_06_epel_compatibility": (
            "To maintain a single spec file compatible with both Fedora 40 and EPEL 9: \n"
            "1. Use conditional macros: `0%{?rhel}` for Enterprise Linux and `0%{?fedora}` for Fedora. \n"
            "2. Handle toolchain differences: EPEL 9 uses older CMake and GCC; conditionally require `cmake >= 3.20` or enable GCC Toolset where necessary. \n"
            "3. Condition modern build macros: use `%cmake_build` for Fedora and fallback to `%make_build` if necessary for older RHEL environments."
        ),

        # Domain 5: openSUSE Packaging
        "eval_suse_01_opensuse_spec": (
            "Author an openSUSE-compliant spec file: \n"
            "1. Build Macros: Use `%cmake` and `%cmake_build` (or `%make_build`). \n"
            "2. Systemd Scriptlets: Use openSUSE systemd macros: `%service_add_pre myapp.service` in `%pre`, `%service_add_post myapp.service` in `%post`, `%service_del_preun myapp.service` in `%preun`, and `%service_del_postun myapp.service` in `%postun`. \n"
            "3. Test Execution: Use `%ctest` in `%check`. Include appropriate `Group: System/Daemons`."
        ),
        "eval_suse_02_obs_failure": (
            "Diagnose OBS build failure via osc CLI: \n"
            "1. Check build results across repositories and architectures: `osc results`. \n"
            "2. Fetch and inspect the remote build log: `osc buildlog openSUSE_Tumbleweed x86_64` (or `osc log`). \n"
            "3. Search log output for compilation errors, missing dependencies, or rpmlint policy rejections."
        ),
        "eval_suse_03_repo_config": (
            "Configure multi-distribution targets in OBS project: \n"
            "1. Edit project metadata: `osc meta prj -e`. \n"
            "2. Add repository definitions linking to target distributions: \n"
            "   `<repository name=\"openSUSE_Tumbleweed\"><path project=\"openSUSE:Factory\" repository=\"snapshot\"/><arch>x86_64</arch></repository>` \n"
            "   `<repository name=\"openSUSE_Leap_15.6\"><path project=\"openSUSE:Leap:15.6\" repository=\"standard\"/><arch>x86_64</arch></repository>` \n"
            "   `<repository name=\"Fedora_40\"><path project=\"Fedora:40\" repository=\"standard\"/><arch>x86_64</arch></repository>`"
        ),
        "eval_suse_04_osc_workflow": (
            "Complete openSUSE development workflow via osc: \n"
            "1. Branch package from Factory: `osc branch openSUSE:Factory <package>`. \n"
            "2. Check out working directory: `osc co home:<user>:branches:openSUSE:Factory/<package>`. \n"
            "3. Make changes and test build locally in clean chroot: `osc build openSUSE_Tumbleweed x86_64`. \n"
            "4. Record changes in `.changes` file with `osc vc` and commit to OBS: `osc commit -m 'Update package'`. \n"
            "5. Submit changes back to Factory: `osc sr -m 'Update package to 1.2.3'`."
        ),
        "eval_suse_05_soname_naming": (
            "openSUSE Shared Library Policy strictly requires: \n"
            "1. The binary package containing `libxyz.so.2` MUST be named `libxyz2` matching the SONAME. \n"
            "2. Development files (headers, pkg-config, unversioned `.so` symlink) MUST be placed in `libxyz-devel`. \n"
            "3. Rationale: This naming policy ensures that applications compiled against different major ABI versions of the library can be co-installed simultaneously without packaging conflicts."
        ),
        "eval_suse_06_tumbleweed_leap": (
            "Reconcile spec file for both rolling Tumbleweed and stable Leap: \n"
            "Use the `0%{?suse_version}` conditional macro: \n"
            "```spec\n"
            "%if 0%{?suse_version} > 1500\n"
            "# openSUSE Tumbleweed\n"
            "BuildRequires: gcc-c++ >= 14\n"
            "%else\n"
            "# openSUSE Leap 15.x\n"
            "BuildRequires: gcc12-c++\n"
            "%endif\n"
            "```\n"
            "Tumbleweed sets `suse_version` to values greater than 1500, whereas Leap 15.x sets `suse_version` to 1500."
        ),

        # Domain 6: Linux Distribution Engineering
        "eval_dist_01_signed_repo_design": (
            "Design for cryptographically signed repository: \n"
            "1. Key Hierarchy: Keep root/master GPG key strictly offline on air-gapped HSM/smartcard. Generate dedicated signing subkeys for the automated repository build servers. \n"
            "2. Metadata Signing: Sign APT metadata via inline `InRelease` and detached `Release.gpg`; sign DNF metadata via detached `repodata/repomd.xml.asc`. \n"
            "3. Key Rotation: Set explicit expiration dates (e.g. 1 year) on signing subkeys. Rotate subkeys periodically without changing the trusted public root key."
        ),
        "eval_dist_02_invalid_metadata": (
            "Cause: Mirror synchronization race condition where edge mirrors synchronize metadata files (`InRelease`, `repomd.xml`) before the referenced binary packages have finished downloading. Clients downloading newly indexed packages receive 404 or hash sum mismatches. \n"
            "Fix: Enforce two-stage mirror synchronization order: sync package pools (`pool/`) first, then synchronize metadata (`dists/` or `repodata/`). In APT repositories, adopt the `by-hash` directory layout so that metadata queries reference immutable content-addressed paths."
        ),
        "eval_dist_03_staged_promotion": (
            "Staged repository promotion and atomic metadata replacement: \n"
            "1. Pipeline Stages: Ingest packages into `dev`, promote to `staging` after automated smoke tests pass, and promote to `production` after co-installability and integration tests pass. \n"
            "2. Artifact Immutability: Promote identical binary artifacts without recompilation between stages. \n"
            "3. Atomic Metadata Swaps: Generate new repository indices in a temporary staging directory, then atomically replace production metadata using directory renames or symlink swaps (`ln -sfn`) to prevent clients from reading partially written metadata."
        ),
        "eval_dist_04_upgrade_analysis": (
            "Auditing and resolving upgrade failures: \n"
            "1. Conffile Management: Use Debian `ucf` or RPM `%config(noreplace)` for configuration files so user modifications are preserved without interactive upgrade prompts. \n"
            "2. File Collisions: Audit packages for overlapping file paths using linter tools or repository queries. \n"
            "3. File Moves: When files move between packages, declare `Breaks: pkg-old (<< 2.0)` and `Replaces: pkg-old (<< 2.0)` in Debian, or `%obsoletes` and `%conflicts` in RPM to ensure clean package transitions."
        ),
        "eval_dist_05_rollback_strategy": (
            "Emergency rollback strategy: \n"
            "1. Why deleting packages breaks clients: Simply deleting packages from repository pools breaks metadata, causes client package managers to report 404 errors, and does not downgrade clients that already installed the faulty version. \n"
            "2. Preferred Fix - Fast-Forward Revert: Release the previous working version with an incremented epoch or release tag (e.g. `netfoo 1:2.9.0-1` or `2.9.0-2+revert`). Package managers strictly treat higher epochs/versions as newer, automatically downgrading all clients during routine updates. \n"
            "3. Repository Snapshot Reversion: Atomically point production symlink to the previous working repository snapshot and guide affected clients to run `apt-get --allow-downgrades install` or `dnf distro-sync`."
        ),
        "eval_dist_06_solver_validation": (
            "Validate repository co-installability using formal SAT solvers: \n"
            "1. Debian / APT: Execute `dose-distcheck` or `dose-deb-coinstall` against `Packages.gz` to verify that every package has a satisfiable dependency solution across all supported architectures. \n"
            "2. RPM / DNF: Execute `dnf repoquery --repofrompath=test,... --repo=test --unsolved` to discover unresolvable dependencies. \n"
            "3. Automated Gating: Integrate solver checks into CI/CD promotion gates, automatically blocking promotion if broken packages or uninstallable leaves are detected."
        ),

        # Domain 7: Reproducible Builds
        "eval_repro_01_timestamp_diagnosis": (
            "Diagnosis: The binary divergence was caused by compile-time macros `__DATE__` and `__TIME__` or wall-clock calls embedding volatile timestamps into the `.rodata` ELF section. \n"
            "Remediation: \n"
            "1. Export `SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)` in build scripts. GCC and Clang automatically replace `__DATE__` and `__TIME__` with deterministic UTC dates derived from SOURCE_DATE_EPOCH. \n"
            "2. Replace volatile compile-time macros in application source code with static version strings."
        ),
        "eval_repro_02_diffoscope_analysis": (
            "Diagnosis from diffoscope: \n"
            "1. Archive ordering: Non-deterministic filesystem readdir traversal order reordered files inside the archive. Fix: Use `tar --sort=name` to enforce alphabetical file sorting. \n"
            "2. File permissions: Host umask variances caused 0644 vs 0664 permission differences. Fix: Pass `tar --mode=go=rX,u+rw` or run builds under normalized `umask 0022`."
        ),
        "eval_repro_03_build_path_mapping": (
            "Cause: Compilers embed absolute source paths into DWARF `.debug_info` symbols and `__FILE__` macros, causing binary hashes to differ depending on the build directory path. \n"
            "Remediation: \n"
            "1. C/C++: Compile with `-ffile-prefix-map=${PWD}=.` and `-fdebug-prefix-map=${PWD}=.` to strip local build directory paths from binaries. \n"
            "2. Rust: Pass `--remap-path-prefix=${PWD}=.` via RUSTFLAGS."
        ),
        "eval_repro_04_sbom_validation": (
            "Standardized SBOM structure and validation: \n"
            "1. Standards: Generate SPDX 2.3/3.0 JSON or CycloneDX 1.5 JSON manifest. \n"
            "2. Mandatory Data: Document package identity, version, Package URL (`purl:pkg:deb/...`), concluded license, and cryptographic hashes (SHA-256). \n"
            "3. Tooling: Generate SBOMs using `syft` (`syft dir:. -o spdx-json=sbom.json`) and validate document schema using `spdx-tools-cli validate`."
        ),
        "eval_repro_05_slsa_provenance": (
            "SLSA Level 3 build provenance: \n"
            "1. Attestation Format: Generate an in-toto provenance statement binding the compiled artifact's SHA-256 digest to the build definition. \n"
            "2. Parameters: Record immutable source repository URI, git commit SHA, build type, and builder ID from isolated build workers. \n"
            "3. Verification: Verify attestation using `slsa-verifier` or `cosign` against the public Rekor transparency log."
        ),
        "eval_repro_06_untrusted_env": (
            "Build script environment sanitization: \n"
            "1. Locale: Enforce `export LC_ALL=C.UTF-8` and `export LANG=C.UTF-8` to prevent locale-specific sorting differences. \n"
            "2. Timezone: Enforce `export TZ=UTC` to prevent local time offsets. \n"
            "3. Randomness & Concurrency: Pass `-frandom-seed=<hash>` to GCC to eliminate non-deterministic symbol naming, and normalize umask to 0022."
        ),

        # Domain 8: Release Maintenance
        "eval_rel_01_rebase_patch_series": (
            "Engineering workflow for patch queue rebase onto upstream 2.4.0: \n"
            "1. Audit Upstream Changes: Review upstream git commit log to identify patches merged in 2.4.0. Drop those two patches from `debian/patches/series` and Fedora spec. \n"
            "2. Rebase Active Patches: Using `quilt` or `git am`, apply remaining patches sequentially. Resolve the merge conflict on the conflicting patch and refresh line offsets with `quilt refresh`. \n"
            "3. Documentation: Document dropped and refreshed patches in `debian/changelog` and spec changelog, and verify that the package compiles cleanly."
        ),
        "eval_rel_02_upstream_security_backport": (
            "Methodology for CVE security backport to LTS release: \n"
            "1. Isolate Minimal Delta: Extract the specific commit fixing the vulnerability and isolate the minimal code delta. Do NOT pull in upstream API refactorings or new features. \n"
            "2. Preserve Binary ABI: Ensure struct layouts, function signatures, and exported symbols remain completely unchanged to guarantee zero regressions for existing applications. \n"
            "3. Regression Testing: Author a regression test verifying that the exploit is mitigated and run the full test suite."
        ),
        "eval_rel_03_abi_transition": (
            "Coordinating shared library SONAME bump (`libdata.so.3` -> `libdata.so.4`): \n"
            "1. Verify ABI breakage using `abi-compliance-checker` or `libabigail` (`abidiff`). \n"
            "2. Create new binary package `libdata4` ensuring it can be co-installed alongside `libdata3` during the transition period. \n"
            "3. Query reverse dependencies (`apt-cache rdepends` or `dnf repoquery --whatrequires`) and schedule coordinated rebuilds of all dependent packages against the new SONAME."
        ),
        "eval_rel_04_multi_distro_coordination": (
            "Synchronizing multi-distribution release 1.5.0: \n"
            "1. Upstream Source: Create and sign upstream git release tag `v1.5.0` and generate official release tarball with SHA-256 checksums. \n"
            "2. Packaging Synchronization: Update version, source URL, and checksums across Arch `PKGBUILD`, Debian `debian/changelog` and `debian/rules`, Fedora `.spec`, and openSUSE `.spec` and `.changes`. \n"
            "3. Matrix Verification: Execute automated matrix builds inside clean containers for Arch, Debian, Ubuntu, Fedora, and openSUSE to verify clean compilation across all targets before announcing release."
        ),
        "eval_rel_05_upstream_watch": (
            "Configure automated upstream release tracking: \n"
            "1. Debian uscan: Author `debian/watch` version 4 matching upstream release tags and tarballs, configuring `pgpmode=auto` to automatically fetch and verify upstream GPG signatures. \n"
            "2. Anitya (release-monitoring.org): Register the project mapping on Anitya, linking upstream GitHub repository to Fedora and Arch Linux package names. \n"
            "3. Automated Notifications: Configure CI webhooks to notify maintainers when new upstream releases or security advisories are published."
        ),
        "eval_rel_06_release_readiness_gate": (
            "Conducting Go/No-Go release readiness review: \n"
            "1. Strict Gate Policy: A release CANNOT proceed with unhandled test failures on any supported architecture. The intermittent test failure on arm64 is an automatic NO-GO until investigated and fixed. \n"
            "2. Linter Compliance: Correct all `lintian` and `rpmlint` errors and unexpanded macro warnings prior to approval. \n"
            "3. Final Decision: NO-GO until the arm64 test failure is diagnosed and linter issues are resolved."
        )
    }


def run_cross_distribution_evals(scenarios_file: Path, responses: Dict[str, str]) -> Tuple[int, int, List[str]]:
    """
    Runs evaluation on a single scenarios.json file against provided responses.
    """
    if not scenarios_file.exists():
        return 0, 0, [f"ERROR: Scenarios file not found: {scenarios_file}"]

    with open(scenarios_file, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    passed = 0
    total = len(scenarios)
    logs = []

    for sc in scenarios:
        sid = sc["id"]
        resp = responses.get(sid, "")
        ok, reason = evaluate_cross_distribution_scenario(sc, resp)
        if ok:
            passed += 1
            logs.append(f"[PASS] {sid}: {reason}")
        else:
            logs.append(f"[FAIL] {sid}: {reason}")

    return passed, total, logs


def main():
    parser = argparse.ArgumentParser(description="Evaluate Cross-Distribution Syswright scenarios.")
    parser.add_argument("--domain", choices=[
        "debian-packaging", "ubuntu-packaging", "rpm-packaging",
        "fedora-packaging", "opensuse-packaging", "distribution-engineering",
        "reproducible-builds", "release-maintenance", "all"
    ], default="all")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    evals_dir = repo_root / "evals"
    responses = get_reference_cross_distribution_responses()

    domains = [
        "debian-packaging", "ubuntu-packaging", "rpm-packaging",
        "fedora-packaging", "opensuse-packaging", "distribution-engineering",
        "reproducible-builds", "release-maintenance"
    ]
    if args.domain != "all":
        domains = [args.domain]

    grand_passed = 0
    grand_total = 0

    print("=" * 70)
    print("Linux Cross-Distribution Engineering Evaluation Benchmark (Phase 6)")
    print("=" * 70)

    for domain in domains:
        scenarios_file = evals_dir / domain / "scenarios.json"
        passed, total, logs = run_cross_distribution_evals(scenarios_file, responses)
        grand_passed += passed
        grand_total += total

        print(f"\n--- Domain: {domain.upper()} ({passed}/{total} passed) ---")
        for log in logs:
            print(f"  {log}")

    print("\n" + "=" * 70)
    pct = (grand_passed / grand_total * 100) if grand_total > 0 else 0
    print(f"Grand Total: {grand_passed}/{grand_total} passed ({pct:.1f}%)")
    print("=" * 70)

    if grand_passed == grand_total and grand_total >= 48:
        print("OVERALL VERDICT: PASS")
        sys.exit(0)
    else:
        print("OVERALL VERDICT: FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
