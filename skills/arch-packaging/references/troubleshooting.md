# Arch Linux Packaging Troubleshooting & Diagnostics Reference

## 1. Scope

This document provides technical root-cause diagnostic workflows and remediations for build, packaging, linkage, and runtime failures encountered across the Arch Linux packaging lifecycle.

---

## 2. Diagnostics Decision Tree

```mermaid
flowchart TD
    FAIL["Package Build or Runtime Failure"] --> STAGE{"Identify Failing Stage"}

    STAGE -->|Source Retrieval| NET["Source Download / Checksum / PGP Failure"]
    STAGE -->|prepare() / build()| COMP["Missing Headers / Toolchain / Build Flags"]
    STAGE -->|check()| TEST["Test Suite Failure"]
    STAGE -->|package()| FHS["Filesystem / Permission / Directory Error"]
    STAGE -->|Post-Build / namcap| LINT["Undeclared Dependency / Permission Warning"]
    STAGE -->|Clean Chroot Only| ISOL["Undeclared makedepends Leakage from Host"]
    STAGE -->|Runtime Execution| DYN["Missing .so Dynamic Library / Symbol Error"]
```

---

## 3. Failure Categories & Remediation Matrix

### 3.1 Source Download & Checksum Failures

#### Symptom: `One or more files did not pass the validity check!`
- **Diagnosis**: The cryptographic hash (`sha256sums` or `b2sums`) in `PKGBUILD` does not match the downloaded source file.
- **Root Causes**:
  1. Upstream retagged a release or changed archive compression parameters.
  2. The download was corrupted or interrupted.
  3. Man-in-the-middle attack or upstream tampering.
- **Remediation**:
  1. Inspect the downloaded file size and type (`file "$SRCDEST/$filename"`).
  2. Compute hash manually: `sha256sum "$SRCDEST/$filename"`.
  3. Compare against upstream signed release notes or announcement commits.
  4. **Strict Invariant**: NEVER replace the checksum with `SKIP`. Update the checksum only after verifying why upstream changed the archive.

#### Symptom: `The signature could not be verified (unknown public key)`
- **Diagnosis**: `makepkg` encountered a detached signature (`.sig`/`.asc`), but the public key is not in the user's GPG keyring.
- **Remediation**:
  1. Extract fingerprint from signature: `gpg --verify "$filename.sig" "$filename"`.
  2. Search authoritative upstream sources (developer's website, git signed commits) for the verified 40-character fingerprint.
  3. Add the verified 40-char fingerprint to `validpgpkeys=('<FINGERPRINT>')` in `PKGBUILD`.
  4. Import key to local GPG keyring: `gpg --recv-keys <FINGERPRINT>`.

---

### 3.2 Compilation & Configuration Failures

#### Symptom: `fatal error: foo/foo.h: No such file or directory`
- **Diagnosis**: Missing C/C++ development header file during compilation.
- **Remediation**:
  1. Query pacman database for the file:
     ```bash
     pacman -F foo.h
     ```
  2. Identify the providing Arch package and add it to `makedepends=()`.

#### Symptom: CMake `Could not find a package configuration file provided by "Foo"`
- **Diagnosis**: CMake cannot locate `FooConfig.cmake` or `FindFoo.cmake`.
- **Remediation**:
  ```bash
  pacman -F FooConfig.cmake
  ```
  Add the supplying package to `makedepends`.

#### Symptom: Meson `Dependency "foo" not found, tried pkgconfig`
- **Diagnosis**: `pkg-config` cannot locate `foo.pc`.
- **Remediation**:
  ```bash
  pacman -F foo.pc
  ```
  Add the package owning `usr/lib/pkgconfig/foo.pc` to `makedepends`.

#### Symptom: `undefined reference to 'foo_symbol'` / Linker error
- **Diagnosis**: The compiler compiled object files, but the linker cannot resolve a dynamic symbol.
- **Root Cause**:
  1. Missing library in linker flags (`-lfoo` omitted).
  2. Library ordering issue in `LDFLAGS`.
  3. ABI incompatibility between compiler toolchain and installed library.
- **Remediation**: Inspect upstream build scripts (`CMakeLists.txt`, `Makefile`) to verify `target_link_libraries` or `pkg-config --libs` inclusion.

---

### 3.3 Build System Specific Failures

#### Cargo / Rust: `error: the lock file /.../Cargo.lock needs to be updated but --frozen was passed`
- **Diagnosis**: `--frozen` was passed, but dependencies listed in `Cargo.toml` do not match `Cargo.lock` or need updating.
- **Remediation**:
  1. Run `cargo fetch --locked` in `prepare()` so all dependencies are pre-cached.
  2. If upstream modified `Cargo.toml` without updating `Cargo.lock`, use `--locked` instead of `--frozen`, or re-generate `Cargo.lock` in `prepare()`.

#### Go: `go: updates to go.mod needed, disabled by -mod=readonly`
- **Diagnosis**: `go build` attempted to download or update Go modules during compilation with `-mod=readonly`.
- **Remediation**:
  Execute `go mod download -modcacherw` in `prepare()` so all required modules are downloaded before compilation starts.

---

### 3.4 Clean-Chroot Discrepancies (Works Locally, Fails in Chroot)

#### Symptom: Package builds with `makepkg` on workstation, but fails in `pkgctl build --clean`
- **Diagnosis**: Workstation contamination. The host workstation has development headers, static libraries, or tools installed that were omitted from `makedepends` in the `PKGBUILD`.
- **Remediation**:
  1. Inspect the chroot build failure log. Identify the missing header or command.
  2. Add the missing tool to `makedepends`.
  3. Rebuild with `pkgctl build --clean`.
  4. **Invariant**: The clean-chroot outcome is always authoritative over local builds.

---

### 3.5 Runtime Linkage & Dynamic Library Failures

#### Symptom: `error while loading shared libraries: libfoo.so.X: cannot open shared object file`
- **Diagnosis**: A compiled binary was installed, but its dynamically linked dependency is missing from the system at runtime.
- **Root Cause**: The package was added to `makedepends` (so it built), but omitted from `depends` (so it was not installed at runtime).
- **Remediation**:
  1. Check dynamic sections of the binary:
     ```bash
     readelf -d "$pkgdir/usr/bin/mybinary" | grep NEEDED
     ```
  2. Locate the Arch package providing `libfoo.so.X`:
     ```bash
     pacman -F libfoo.so.X
     ```
  3. Move or add the package to `depends=()`.

---

### 3.6 Filesystem Layout & Permission Warnings

#### Symptom: `namcap: file-world-writable`
- **Diagnosis**: A file installed in `$pkgdir` has permissions `0777` or `0666`.
- **Remediation**:
  Fix permissions during `package()` using `install -Dm644` for files or `chmod 0755` for directories.

#### Symptom: `namcap: non-fhs-man-page` or files in `/usr/local`
- **Diagnosis**: Upstream install script installed manual pages to `/usr/man` instead of `/usr/share/man`, or files to `/usr/local`.
- **Remediation**:
  Pass `--prefix=/usr` and `--mandir=/usr/share/man` to configure script, or move files explicitly in `package()`:
  ```bash
  mv "$pkgdir/usr/man" "$pkgdir/usr/share/man"
  ```

---

## 4. Authoritative References

- [Arch package guidelines: Troubleshooting](https://wiki.archlinux.org/title/Arch_package_guidelines)
- [readelf(1) Manual](https://man.archlinux.org/man/readelf.1)
- [pacman(8) Manual](https://man.archlinux.org/man/pacman.8)
