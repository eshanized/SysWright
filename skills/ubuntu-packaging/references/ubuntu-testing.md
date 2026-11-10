# Ubuntu Package Testing: Autopkgtest Infrastructure & Architecture Validation

Technical reference for running and debugging autopkgtests on Ubuntu build infrastructure and resolving architecture-specific failures.

---

## 1. Ubuntu autopkgtest Infrastructure

In Ubuntu development, autopkgtest results gate archive migration from `<series>-proposed` to `<series>`:
- If a package or any of its reverse dependencies fail autopkgtests in `-proposed`, the package will **never** migrate to the release archive.
- Tests run in isolated LXD/Incus containers or QEMU virtual machines on Canonical infrastructure.

### Running autopkgtest Locally against Ubuntu Targets:
```bash
# Run autopkgtest using LXD container testbed targeting Ubuntu noble (24.04)
autopkgtest myapp_1.2.3-1ubuntu1_amd64.changes -- lxd ubuntu:noble/amd64
```

---

## 2. Launchpad Architecture Build Failures

Launchpad builds across 6 architectures: `amd64`, `arm64`, `armhf` (32-bit ARM), `ppc64el` (64-bit PowerPC little-endian), `s390x` (64-bit IBM System/z big-endian), and `riscv64`.

### Common Architecture Failure Patterns:
1. **32-Bit Time / Pointer Issues (`armhf`)**:
   - `sizeof(void*) == 4`, `sizeof(time_t) == 8` (since Debian/Ubuntu 64-bit `time_t` transition).
   - Assuming `sizeof(long) == 8` fails on 32-bit architectures. Use `intptr_t` or `size_t`.
2. **Big-Endian Clashes (`s390x`)**:
   - Intel/ARM are little-endian; IBM s390x is big-endian.
   - Code that casts byte arrays directly to integer structs fails on s390x. Use endian-safe conversion macros (`htons()`, `be32toh()`).
3. **Missing Architecture Build Dependencies**:
   - Certain packages (e.g., `valgrind`, `libnuma-dev`) are not available on all architectures. Restrict in `debian/control` using architecture wildcards: `[any-amd64 any-arm64]`.
