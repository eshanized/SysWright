# Debian Dependency Relationships & Binary Transitions

Technical reference for Build-Depends, runtime dependencies, package transitions, and virtual packages.

---

## 1. Debian Dependency Field Taxonomy

| Relationship | Semantics | When to Use |
|---|---|---|
| **Build-Depends** | Packages strictly required on the host to compile the source package. | Compilers, build systems, header development packages (`libssl-dev`). |
| **Build-Depends-Indep** | Packages required only when building architecture-independent (`all`) binary packages. | Sphinx, Doxygen, documentation generators. |
| **Depends** | Absolute prerequisite. Package cannot be configured or executed without these. | Shared libraries, essential runtimes, daemon dependencies. |
| **Recommends** | Strong dependency. Installed by default in APT unless `--no-install-recommends` is specified. | Plugins, common auxiliary tools, certificates. |
| **Suggests** | Weak dependency. Optional extensions or documentation. | Example configurations, heavy documentation packages. |
| **Breaks** | Incompatible with another package version; prevents co-installation unless upgraded. | Library transitions, API breakages. |
| **Replaces** | Takes over files formerly owned by another package. | Renamed packages, file movement between split packages. (Used with `Breaks`). |
| **Provides** | Declares that this package implements a virtual package or alias. | `default-mta`, `httpd`, `awk`. |
| **Pre-Depends** | Special dependency that MUST be fully installed and configured *before* unpacking begins. | High-risk; requires approval from debian-devel mailing list. |

---

## 2. Shared Library Transitions & Breaks/Replaces

When a package is renamed or files move between packages:
```ini
Package: libfoo2
Architecture: any
Depends: ${shlibs:Depends}, ${misc:Depends}
Breaks: libfoo1 (<< 2.0.0)
Replaces: libfoo1 (<< 2.0.0)
```
- `Breaks`: Tells APT that `libfoo1` and `libfoo2` cannot be configured simultaneously if `libfoo1 < 2.0.0`.
- `Replaces`: Allows `dpkg` to overwrite files owned by `libfoo1` without throwing an `overwriting file owned by another package` error.

---

## 3. Architecture Restrictions in Dependencies

Restrict dependencies to specific target architectures or profiles:
```ini
Build-Depends:
 debhelper-compat (= 13),
 libnuma-dev [amd64 arm64],
 libvalgrind-dev [!armel !mips64el],
 python3-sphinx <!nodoc>,
```
- `[amd64 arm64]`: Package is required only when building on amd64 or arm64.
- `[!armel]`: Package is required on all architectures except armel.
- `<!nodoc>`: Build profile restriction; dependency is skipped when building with `DEB_BUILD_PROFILES=nodoc`.
