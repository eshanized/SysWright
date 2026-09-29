# Reproducible Build Standards & Determinism

## 1. Scope & The Reproducibility Invariant

A build is **reproducible** if given the exact same source code, build environment, and build instructions, it produces bit-for-bit identical output artifacts.
Reproducibility prevents supply-chain attacks, simplifies debugging, and enables independent binary verification.

---

## 2. Core Sources of Non-Determinism & Remediations

### 2.1 Embedded Timestamps (`SOURCE_DATE_EPOCH`)
- **Problem**: Compilers (`__DATE__`, `__TIME__`) and archive tools (`tar`, `ar`) embed the current wall-clock build timestamp into binary outputs.
- **Solution**: Honor `SOURCE_DATE_EPOCH` (a UNIX timestamp in seconds).
  - Set `SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)` in build environments.
  - GCC and Clang automatically substitute `SOURCE_DATE_EPOCH` for `__DATE__` and `__TIME__`.

### 2.2 Embedded Host File Paths (`-ffile-prefix-map`)
- **Problem**: Debug information (`DWARF`) embeds the absolute path of the source directory (e.g. `/home/developer/build/src/main.c`).
- **Solution**: Strip or map host directory prefixes:
  ```bash
  CFLAGS += -ffile-prefix-map=$PWD=.
  ```
  In Rust / Cargo:
  ```bash
  RUSTFLAGS += --remap-path-prefix=$PWD=.
  ```

### 2.3 Non-Deterministic Archive Ordering & Static Libraries
- **Problem**: `ar` archives static libraries with filesystem-dependent mtime, uid, gid, and file order.
- **Solution**: Pass deterministic flags to `ar`:
  ```bash
  ar Dqc libmy.a file1.o file2.o  # 'D' flag enforces zero timestamps and UIDs
  ```
