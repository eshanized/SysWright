# Ubuntu Packaging Fundamentals & Versioning Conventions

Technical reference for Ubuntu package maintenance, source formats, and version numbering standards.

---

## 1. Ubuntu Packaging Foundations

Ubuntu is derived from Debian; it uses the `dpkg` package manager, `.deb` binary package format, and `debhelper` build system. However, Ubuntu maintains independent distribution archives, independent release cycles, and distinct packaging policies.

### Version Numbering Invariants:
1. **Direct Sync from Debian**:
   If an unmodified package is synced from Debian unstable, the version number remains identical:
   ```text
   pkgname_1.2.3-1
   ```
2. **Ubuntu-Modified Package (Debian Delta)**:
   If packaging changes are applied on top of a Debian package, append `ubuntu1` (or increment to `ubuntu2`):
   ```text
   pkgname_1.2.3-1ubuntu1
   ```
3. **Ubuntu Native / Unpackaged in Debian**:
   If packaged directly for Ubuntu without a Debian package:
   ```text
   pkgname_1.2.3-0ubuntu1
   ```
4. **PPA / Backport Release Suffix**:
   To ensure proper APT upgrade ordering when publishing to PPAs across multiple Ubuntu series:
   ```text
   pkgname_1.2.3-1ubuntu1~ppa1~noble1
   ```
   *Note: Using the tilde (`~`) ensures that when the user eventually upgrades their host to the official archive version `1.2.3-1ubuntu1`, APT recognizes the official version as newer than the PPA version.*

---

## 2. Changelog Invariant: Series Targeting

In Debian, `debian/changelog` targets `unstable`. In Ubuntu, uploads MUST target the exact series code name:
- Valid: `noble` (24.04 LTS), `jammy` (22.04 LTS), `focal` (20.04 LTS), `oracular` (24.10 Interim).
- Invalid: `unstable`, `testing`, `devel`, or version numbers like `24.04`.
- Launchpad strictly rejects any upload whose changelog distribution does not match an active series code name.
