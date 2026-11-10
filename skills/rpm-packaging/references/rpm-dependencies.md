# RPM Dependency Architecture: Automatic Discovery & Rich Dependencies

Technical reference for BuildRequires, runtime Requires, automatic soname tracking, weak dependencies, and Boolean rich dependencies.

---

## 1. Automatic Dependency Generation

RPM automatically scans binary payloads during `%install` to discover shared library and language dependencies without manual specification:

### Automatic Shared Library Tracking:
1. `find-requires`: Scans all compiled ELF binaries with `objdump` / `readelf` to find `DT_NEEDED` entries.
   - Example generated requirement: `Requires: libssl.so.3()(64bit), libc.so.6(GLIBC_2.34)(64bit)`.
2. `find-provides`: Scans all compiled shared libraries to find `DT_SONAME` entries and exported symbols.
   - Example generated capability: `Provides: libfoo.so.1()(64bit)`.
- **Packaging Rule**: Never manually add `Requires: libssl` or `Requires: libc` to an RPM spec file! Automatic dependency generation tracks exact sonames and symbol versions automatically.

---

## 2. Weak & Soft Dependencies

RPM supports non-mandatory dependency relationships:

| Tag | Purpose | Package Manager Behavior |
|---|---|---|
| `Recommends:` | Strong hint | Installed by default by `dnf` / `zypper` unless explicitly disabled. |
| `Suggests:` | Weak hint | Not installed automatically; displayed as optional enhancement. |
| `Supplements:` | Reverse recommends | Package is automatically installed if the specified packages are installed. |
| `Enhances:` | Reverse suggests | Package is suggested if the specified packages are installed. |

---

## 3. Rich / Boolean Dependencies (RPM 4.13+)

Modern RPM supports boolean expressions in dependency tags:

```spec
# Require package A only IF package B is also installed
Requires: (pkgA if pkgB)

# Require at least one of package A or package B
Requires: (pkgA or pkgB)

# Package conflicts with pkgB unless version is >= 2.0
Conflicts: (pkgB with pkgB < 2.0)
```
*Note: Boolean rich dependencies are supported in modern Fedora, RHEL 8+, and openSUSE Leap 15+, but unsupported on legacy RHEL 7 / RPM 4.11.*
