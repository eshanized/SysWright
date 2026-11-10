# Multi-Distribution Maintenance & Packaging Overlay Architecture

Maintaining software across Arch Linux, Debian, Ubuntu, Fedora, and openSUSE requires a clear overlay architecture to avoid duplicating packaging effort and diverging bugfixes.

---

## 1. Multi-Distribution Directory Architecture

A recommended repository layout for a cross-distribution project:

```text
project-root/
├── src/                          <-- Upstream source code
├── tests/
├── packaging/
│   ├── arch/
│   │   └── PKGBUILD              <-- Arch Linux package definition
│   ├── debian/
│   │   ├── control               <-- Debian / Ubuntu metadata
│   │   ├── rules                 <-- debhelper build instructions
│   │   ├── changelog
│   │   └── patches/
│   ├── fedora/
│   │   └── myapp.spec            <-- Fedora RPM spec
│   └── opensuse/
│       ├── myapp.spec            <-- openSUSE RPM spec
│       └── myapp.changes
└── Makefile / CMakeLists.txt
```

---

## 2. Harmonizing Package Metadata

| Property | Arch Linux | Debian / Ubuntu | Fedora | openSUSE |
|---|---|---|---|---|
| **Package Name** | `pkgname=myapp` | `Package: myapp` | `Name: myapp` | `Name: myapp` |
| **C++ Compiler** | `makedepends=('gcc')` | `Build-Depends: g++` | `BuildRequires: gcc-c++` | `BuildRequires: gcc-c++` |
| **Systemd Lib** | `depends=('systemd-libs')` | `libsystemd-dev` | `pkgconfig(libsystemd)` | `pkgconfig(libsystemd)` |
| **License** | `license=('Apache-2.0')` | `debian/copyright` | `License: Apache-2.0` | `License: Apache-2.0` |

### Strategy:
- Use `pkgconfig(...)` format where possible in RPM specs (Fedora and openSUSE both support virtual pkgconfig dependencies).
- Keep patch series centralized; when a bug is fixed for Debian in `debian/patches/`, the exact patch file can be referenced in Fedora's `myapp.spec` (`Patch0: 0001-fix-bug.patch`).

---

## 3. Synchronized Matrix Verification Workflow

Before issuing a cross-distribution release tag:
1. **Containerized Build Matrix**:
   Use Docker or Podman to build each target in clean rootfs containers:
   ```bash
   podman run --rm -v $PWD:/src:ro archlinux:latest ...
   podman run --rm -v $PWD:/src:ro debian:bookworm ...
   podman run --rm -v $PWD:/src:ro fedora:40 ...
   podman run --rm -v $PWD:/src:ro opensuse/tumbleweed:latest ...
   ```
2. **Artifact Verification**:
   Inspect generated packages for missing files or unexpected runtime dependencies.