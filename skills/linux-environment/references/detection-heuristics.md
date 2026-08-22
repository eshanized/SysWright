# Environment Reference: System Detection Heuristics

## 1. Distribution Detection

The primary, POSIX-standard mechanism for identifying the active Linux distribution is parsing `/etc/os-release` (or `/usr/lib/os-release` per systemd specifications):
- `ID`: Lowercase distribution identifier (e.g., `arch`, `debian`, `fedora`, `ubuntu`).
- `ID_LIKE`: Space-separated list of equivalent distributions (e.g., `ID_LIKE="rhel fedora"`).
- `VERSION_ID`: Version number (e.g., `12` for Debian Bookworm, `24.04` for Ubuntu). Rolling distributions (Arch) omit or set `rolling`.
- `BUILD_ID`: Often used by rolling distributions (e.g., Arch `BUILD_ID=rolling`).

**Fallback Heuristics**:
If `/etc/os-release` is missing:
- `/etc/arch-release`: Arch Linux.
- `/etc/debian_version`: Debian / Ubuntu derivative.
- `/etc/fedora-release`: Fedora.

---

## 2. Execution Context & Virtualization Detection

Distinguishing between native bare metal, containers, virtual machines, and chroots is critical for safety decisions (e.g., whether to allow clean chroot builds or require microVMs).

### 2.1 Container Detection
1. `/.dockerenv`: Indicates standard Docker container.
2. `/run/.containerenv`: Indicates Podman or OCI container.
3. `/proc/1/cgroup`: Contains `docker`, `containerd`, `lxc`, `kubepods`, or `/user.slice`.
4. `systemd-detect-virt -c`: Returns container engine name (`docker`, `podman`, `lxc`).

### 2.2 Virtual Machine Detection
1. `systemd-detect-virt -v`: Returns hypervisor name (`kvm`, `qemu`, `vmware`, `oracle`, `microsoft`).
2. `/sys/class/dmi/id/sys_vendor` and `product_name`: Check for `QEMU`, `KVM`, `VMware, Inc.`, `VirtualBox`.
3. `/proc/cpuinfo`: Inspect `flags` for `hypervisor`.

### 2.3 Chroot Detection
1. Compare inode of `/` with inode of root namespace if inspectable.
2. `systemd-detect-virt -r`: Detects chroot environments.

---

## 3. Toolchain & Build System Discovery

Check presence and version without running mutating subcommands:
- **C/C++ Compilers**: `gcc --version`, `clang --version`.
- **Rust Toolchain**: `rustc --version`, `cargo --version`.
- **Build Systems**: `meson --version`, `cmake --version`, `make --version`, `ninja --version`.
- **Packaging Utilities**: `makepkg --version`, `pkgctl version`, `dpkg --version`, `rpm --version`.
- **Diagnostics**: `systemd-analyze --version`, `namcap --version`, `strace -V`, `gdb --version`.
