# Fedora Packaging Guidelines: Licensing, Unbundling, and Standards

Technical reference for core Fedora packaging policies, mandatory SPDX licensing, and dependency unbundling rules.

---

## 1. Strict SPDX License Identifiers

Fedora requires all spec files to use valid **SPDX License Identifiers** in the `License:` tag:
- Standard identifiers: `Apache-2.0`, `MIT`, `GPL-2.0-or-later`, `GPL-3.0-only`, `BSD-3-Clause`.
- Compound licenses: Use `AND` (all licenses apply) and `OR` (dual-licensing options):
  `License: Apache-2.0 AND MIT`
  `License: GPL-2.0-or-later OR BSD-2-Clause`
- Check license validity with `license-fedora-review` or official Fedora license data.
- **Prohibited**: Non-free licenses, licenses forbidding commercial use, or patented algorithms (MP3 in older releases, patented codecs).

---

## 2. The Strict Unbundling Mandate

> [!IMPORTANT]
> **Fedora policy strictly forbids bundling external libraries inside software packages.**
> If an upstream project bundles a third-party copy of `zlib`, `sqlite`, `libpng`, or `fmt` inside `third_party/` or `vendor/`, the packager MUST:
> 1. Remove the vendored directory in `%prep` (`rm -rf vendor/zlib`).
> 2. Patch the build system (CMake/Meson/Makefile) to find and link against the Fedora system package.
> 3. Add the corresponding package to `BuildRequires:` (`BuildRequires: zlib-ng-devel`, `BuildRequires: sqlite-devel`).
> 
> *Rationale*: Bundled libraries bypass security updates. When a CVE is patched in Fedora's `zlib`, all applications must benefit immediately without rebuilding hundreds of individual packages.

---

## 3. Compiler Flags & Hardening

Fedora injects strict compiler flags automatically via standard build macros (`%set_build_flags`, `%cmake`, `%meson`):
- Full RELRO: `-Wl,-z,relro -Wl,-z,now`
- Position Independent Executables: `-fPIE -pie`
- Stack Protection: `-fstack-protector-strong -fstack-clash-protection`
- Fortify Source: `-D_FORTIFY_SOURCE=3`
- Control Flow Integrity: `-fcf-protection` on x86_64
