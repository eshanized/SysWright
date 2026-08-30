# Arch Linux Package Standards & Philosophy

## 1. Scope

This document establishes the authoritative standards and packaging philosophy for Arch Linux packages. It applies across all package distribution channels: official Arch Linux repositories, the Arch User Repository (AUR), local system builds, and custom Arch-based distribution repositories.

---

## 2. Arch Packaging Philosophy

Arch Linux follows a strict packaging philosophy documented in the [Arch package guidelines](https://wiki.archlinux.org/title/Arch_package_guidelines):

1. **Upstream-Vanilla Packaging**:
   - Software must be packaged as close to standard upstream release as possible.
   - Do not apply downstream branding, distribution logos, customized default configurations, or feature modifications unless technically required for system integration.
   - Patches are restricted to bug fixes, security remediations, compiler compatibility fixes, or standard filesystem path alignment. Every patch must reference an upstream issue or pull request.
2. **Minimal Downstream Divergence**:
   - Upstream build systems and configurations should be preserved.
   - Avoid disabling features enabled by upstream defaults unless they introduce unresolvable dependency bloat or violate Arch packaging policies.
3. **Reproducibility & Determinism**:
   - Packages must build deterministically in isolated environments.
   - Package builds must not depend on ambient host state or unversioned network assets.
4. **SPDX License Compliance**:
   - Modern Arch Linux packages require standard SPDX license identifiers.

---

## 3. Package Naming Conventions

Package names (`pkgname`) must strictly conform to Arch standards:

| Rule | Requirement | Examples / Violations |
|:---|:---|:---|
| **Character Set** | Lowercase alphanumeric characters (`a-z`, `0-9`) and hyphens (`-`). No underscores, no uppercase letters, no spaces. | `ripgrep` (Valid)<br>`RipGrep` (Invalid)<br>`rip_grep` (Invalid) |
| **Language Prefixes** | Python modules/libraries: `python-<modulename>`.<br>Perl modules: `perl-<modulename>`.<br>Ruby gems: `ruby-<gemname>`.<br>Go modules/libraries: `go-<modulename>`.<br>End-user applications written in these languages use the application name without prefix (e.g., `black`, not `python-black`). | `python-requests` (Library)<br>`black` (CLI tool) |
| **VCS Packages** | Development/VCS packages must append `-git`, `-svn`, `-hg`, or `-bzr` matching upstream's VCS. | `neovim-git` |
| **Binary Packages** | Packages that repackage upstream prebuilt binaries (when source is available) must append `-bin`. | `terraform-bin` |
| **Compatibility Packages** | Legacy versions coexisting with current releases append major version numbers. | `python2`, `openssl-1.1`, `qt5-base` |
| **Split Packages** | Split package base names (`pkgbase`) identify the unified source tree; subpackage names (`pkgname`) identify specific runtime outputs. | `pkgbase=gcc`<br>`pkgname=('gcc' 'gcc-libs' 'gcc-fortran')` |

---

## 4. Versioning & Release Numbering

### 4.1 Upstream Version (`pkgver`)
- Must match the official upstream release tag or version string (e.g., `1.8.0`).
- Must contain only alphanumeric characters, dots (`.`), and underscores (`_`). Hyphens (`-`) are strictly forbidden inside `pkgver` because pacman uses hyphens to separate `pkgname`, `pkgver`, and `pkgrel`.
- If upstream uses hyphens (e.g., `1.8-rc1`), convert them to underscores or dots: `1.8_rc1` or `1.8.rc1`.

### 4.2 Package Release (`pkgrel`)
- Represents the release number of the Arch package build for a specific `pkgver`.
- Starts at `1` for the first release of a new `pkgver`.
- Incremented by `1` (`2`, `3`, ...) whenever the package is modified without an upstream version change (e.g., fixing a packaging bug, adding a patch, rebuilding for a shared library SONAME bump).
- **Mandatory Reset**: `pkgrel` must be reset to `1` whenever `pkgver` is incremented.

### 4.3 Epoch (`epoch`)
- An unsigned integer that forces pacman to consider a package newer than any release without an epoch, or with a lower epoch.
- **Strict Limitation**: Use only when upstream changes versioning schemes in a way that causes pacman version comparison (`vercmp`) to consider the new version older than the previous version (e.g., transitioning from date-based `20240101` to semver `1.0.0`).
- Never decrement or remove an `epoch` once added.

---

## 5. Architecture Declarations (`arch`)

| Declaration | Usage | Criteria |
|:---|:---|:---|
| `arch=('x86_64')` | Compiled native binaries, ELF shared libraries, or architecture-dependent code. | Architecture-specific binaries (`gcc`, `rustc`, `cmake` native targets). |
| `arch=('any')` | Architecture-independent packages. | Pure Python scripts, shell scripts, Perl modules without XS, fonts, themes, documentation, header-only libraries without compiled helpers. |

*Warning*: If a package contains even a single compiled ELF binary or shared object, `arch` must NOT be `'any'`.

---

## 6. SPDX Licenses & File Placement

Arch Linux transitioned to SPDX license identifiers across all repositories:

1. **Common Licenses**:
   - For licenses included in the `licenses` package (e.g., `Apache-2.0`, `GPL-2.0-or-later`, `GPL-3.0-or-later`, `LGPL-3.0-or-later`, `MIT`, `BSD-2-Clause`, `BSD-3-Clause`, `MPL-2.0`):
     - Specify the exact SPDX identifier in the `license` array: `license=('MIT')` or `license=('Apache-2.0' 'MIT')`.
     - Dual-licensed code: list both in the array.
2. **Custom and MIT/BSD License Installation**:
   - For `MIT`, `BSD`, `ISC`, and any non-standard license, a copy of the license file must be installed to:
     ```bash
     install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
     ```
   - For proprietary or unclassified custom licenses, use `license=('LicenseRef-Custom')` or `license=('custom:LicenseName')` and install the text into `$pkgdir/usr/share/licenses/$pkgname/`.

---

## 7. Package Descriptions (`pkgdesc`)

- Must be a concise summary of the software (under 80 characters).
- Must NOT end with a period (`.`).
- Must NOT redundantly repeat the package name (e.g., write `"Fast grep replacement"`, not `"ripgrep is a fast grep replacement"`).
- Must avoid marketing superlatives (`"The best and most revolutionary text editor"`).

---

## 8. Common Mistakes

1. **Using hyphens in `pkgver`**: Causes pacman parsing failure (`1.0-beta` $\to$ must be `1.0_beta`).
2. **Forgetting to reset `pkgrel`**: Updating `pkgver=2.0.0` while leaving `pkgrel=4` from the previous version.
3. **Setting `arch=('any')` for compiled packages**: Leads to broken installations on non-x86 architectures when precompiled ELF code is shipped.
4. **Missing license file for MIT/BSD**: MIT and BSD licenses require packaging the copyright and permission notice file in `/usr/share/licenses/$pkgname/`.
5. **Non-SPDX license strings**: Using `license=('GPL')` or `license=('custom')` instead of `license=('GPL-3.0-or-later')` or installing the custom license properly.

---

## 9. Verification Guidance

Execute the following checks before approving package standards compliance:
```bash
# 1. Parse and print package source info
makepkg --printsrcinfo

# 2. Check version ordering using vercmp
vercmp "1.0_beta-1" "1.0-1"

# 3. Check license compliance and packaging metadata via namcap
namcap PKGBUILD
```

---

## 10. Authoritative References

- [Arch package guidelines](https://wiki.archlinux.org/title/Arch_package_guidelines)
- [PKGBUILD(5) Manual](https://man.archlinux.org/man/PKGBUILD.5)
- [SPDX License List](https://spdx.org/licenses/)
- [Arch Linux License Guidelines](https://wiki.archlinux.org/title/Arch_package_guidelines#License)
