# Build Environment Normalization & Compiler Flags

Build systems leak environmental properties into compiled binaries unless strict sanitization is applied to compiler flags, file paths, and process environments.

---

## 1. Stripping Build Paths (`-ffile-prefix-map`)

Compilers embed absolute source paths into DWARF debug symbols and `__FILE__` macros. If user A builds in `/home/alice/build` and CI builds in `/builds/runner-1/myapp`, the binaries will produce different hashes.

### Compiler Path Normalization Flags:
Pass the following flags to GCC and Clang via `CFLAGS`, `CXXFLAGS`, and `RUSTFLAGS`:

```bash
# C / C++ Flags
CFLAGS="-ffile-prefix-map=${PWD}=. -fdebug-prefix-map=${PWD}=."
CXXFLAGS="-ffile-prefix-map=${PWD}=. -fdebug-prefix-map=${PWD}=."

# Rust Flags
RUSTFLAGS="--remap-path-prefix=${PWD}=."
```

---

## 2. Environment Variables Sanitization

Build scripts must run within a cleansed environment. Volatile environment variables must be reset before triggering builds:

```bash
# Standard Sanitization Wrapper
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export TZ=UTC
export umask 0022
export PATH="/usr/bin:/bin"
unset HOSTNAME
unset USER
unset LOGNAME
unset HOME
```

---

## 3. Kernel & CPU Architecture Independence

1. **CPU Instructions (`-march=native`)**:
   - Never use `-march=native` in release packages. It enables processor-specific instruction sets (AVX-512, SSE4.2) based on the host CPU, breaking reproducibility across heterogeneous build workers.
   - Use standard baseline targets: `-march=x86-64-v2` or `-march=x86-64-v3`.
2. **Kernel Version Leaks (`uname -r`)**:
   - Ensure build scripts do not run `uname -r` or `uname -m` and embed host kernel revisions into software banner strings.
   - Mock kernel responses or override version discovery macros in Makefiles/CMake.