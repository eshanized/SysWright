# Global Engineering Reference: Version Awareness & API Lifecycles

## 1. The Version Evolution Principle

Linux is not a monolithic static operating system; it is a continuously evolving ecosystem. Code or configuration valid on one kernel, glibc, systemd, or compiler version will frequently fail, trigger warnings, or cause security regressions on another.

An engineer must never apply technical recommendations without verifying the **active version boundary**.

---

## 2. Kernel Lifecycle Awareness

| Kernel Branch | Release Cadence | Target Use Case | Engineering Consideration |
|:---|:---|:---|:---|
| **Mainline (torvalds/linux)** | Every 9–10 weeks | Upstream development | Contains newest APIs; rapid API deprecation/removal. |
| **Stable (x.y.z)** | Weekly patch releases | Current rolling distros (Arch) | Bug/security fixes only; no breaking API changes within minor branch. |
| **LTS (Long Term Support)** | Maintained 2–6 years | Enterprise / LTS distros (Debian, RHEL, Ubuntu LTS) | Kernel internal APIs remain fixed; backported driver fixes must be compatible with older sub-APIs. |

### Common Kernel API Evolutions
- **Timers**: `init_timer(&t)` (obsolete since Linux 4.14) $\to$ `timer_setup(&t, callback, 0)`.
- **Randomness**: `get_random_bytes()` / `get_random_u32()` (modern) vs. deprecated `/dev/urandom` ioctls.
- **GPIO**: Legacy sysfs (`/sys/class/gpio`) deprecated $\to$ modern character device API (`libgpiod` v2+).

---

## 3. Userspace & Systemd Versioning

### systemd Directives
Directives introduced in newer systemd releases are silently ignored or produce errors on older versions:
- `ProtectSystem=strict` (systemd v231+)
- `DynamicUser=yes` (systemd v235+)
- `ProtectClock=yes`, `ProtectKernelLogs=yes` (systemd v245+)
- `MemoryDenyWriteExecute=yes` (systemd v231+)

**Rule**: Before applying advanced sandboxing directives, verify the running systemd version with `systemd --version` or inspect target distribution baselines.

---

## 4. Compiler & Language Standards

| Toolchain | Standards Supported | Hardening Baseline |
|:---|:---|:---|
| **GCC 13 / 14** | C23 (partial), C++23 | `-D_FORTIFY_SOURCE=3`, `-fstack-protector-strong`, `-fPIE` |
| **Clang / LLVM 17 / 18** | C23, C++23 | ThinLTO, SafeStack, Control Flow Integrity (CFI) |
| **Rust 1.75+ / 1.80+** | Edition 2021 / 2024 | Strict lints, standard clippy passes |
| **glibc 2.38 / 2.39+** | POSIX.1-2024 additions | Modern `strlcpy` / `strlcat` in libc, modern `close_range()` |

**Rule**: Never assume next-generation compiler features are universally available across older enterprise distributions. Always check compiler capability or probe feature flags via build scripts (e.g., Meson `cc.has_argument()`).
