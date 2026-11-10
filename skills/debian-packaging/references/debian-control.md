# Debian Package Metadata: debian/control Reference

Comprehensive reference for fields, architecture qualifiers, Multi-Arch, and substitution variables in `debian/control`.

---

## 1. Structure of `debian/control`

`debian/control` uses RFC 822 / 5322 paragraph formatting. It contains:
1. **Source Paragraph**: Defines the source package, build dependencies, VCS links, and standards version.
2. **Binary Paragraph(s)**: One or more paragraphs each defining a binary `.deb` package built from this source.

```ini
Source: myapp
Section: utils
Priority: optional
Maintainer: Debian Developer <maintainer@debian.org>
Build-Depends:
 debhelper-compat (= 13),
 cmake,
 libssl-dev,
 pkgconf,
Standards-Version: 4.6.2
Homepage: https://example.org/myapp
Vcs-Git: https://salsa.debian.org/debian/myapp.git
Vcs-Browser: https://salsa.debian.org/debian/myapp
Rules-Requires-Root: no

Package: myapp
Architecture: any
Multi-Arch: foreign
Depends:
 ${misc:Depends},
 ${shlibs:Depends},
Recommends:
 ca-certificates,
Suggests:
 myapp-doc,
Description: high-performance secure networking utility
 Fast, multi-threaded networking daemon designed for low-latency
 packet processing across modern multi-core Linux systems.
```

---

## 2. Field Definitions & Best Practices

### Architecture Fields:
- `Architecture: any`: Compiled architecture-dependent binaries (C, C++, Rust, Go). Built independently for every architecture (`amd64`, `arm64`, `riscv64`).
- `Architecture: all`: Architecture-independent files (Python scripts, shell scripts, documentation, images). Built once for all architectures.

### Multi-Arch Relationships:
- `Multi-Arch: same`: Binary package can be co-installed for multiple architectures simultaneously on the same system (standard for shared library packages: `libfoo1:amd64` and `libfoo1:i386`).
- `Multi-Arch: foreign`: Binary package architecture does not matter to dependents (standard for CLI tools and compilers: `myapp:amd64` satisfies dependency for `arm64` cross-builds).
- `Multi-Arch: allowed`: Dependents can declare `Package (>= 1.0) [any]` or direct foreign dependency.

### Substitution Variables:
- `${shlibs:Depends}`: Automatically populated by `dpkg-shlibdeps` analyzing compiled ELF binaries with `objdump` to detect exact soname dependencies (e.g., `libc6 (>= 2.34)`, `libssl3 (>= 3.0.0)`).
- `${misc:Depends}`: Automatically populated by debhelper tools (e.g., systemd units, shared library ldconfig triggers).
- **Rule**: Every binary package MUST include `${misc:Depends}` and (for compiled binaries) `${shlibs:Depends}` in `Depends:`.
