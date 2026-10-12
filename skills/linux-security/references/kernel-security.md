# Linux Kernel Security: Lockdown, Module Signing, and Sysctl Hardening

Technical reference for kernel-level security protections, sysctls, and supply-chain integrity.

---

## 1. Kernel Lockdown Mode

Kernel Lockdown prevents user-space root processes from modifying running kernel code or reading sensitive kernel memory (such as cryptographic keys or raw DMA buffers).

### Lockdown Levels:
- **`none`**: Standard operational mode. Root can load unsigned modules, write to `/dev/mem`, and use kexec.
- **`integrity`**: Blocks features that allow user-space to modify running kernel code:
  - Disallows loading unsigned kernel modules (`CONFIG_MODULE_SIG`).
  - Disallows direct memory access via `/dev/mem`, `/dev/kmem`, and `/dev/port`.
  - Disallows arbitrary MSR writes.
  - Enforced automatically when UEFI Secure Boot is active.
- **`confidentiality`**: Includes all `integrity` restrictions and blocks user-space from inspecting sensitive kernel memory:
  - Disallows kernel address leakage (`/proc/kallsyms`).
  - Disallows kprobes and raw BPF access to kernel data.

```bash
# Check current lockdown state
cat /sys/kernel/security/lockdown
# [none] integrity confidentiality
```

---

## 2. Hardened Kernel Sysctls

Recommended baseline sysctl configuration (`/etc/sysctl.d/50-security-hardening.conf`):

```ini
# Prevent unprivileged users from reading dmesg (avoids kernel pointer leaks)
kernel.dmesg_restrict = 1

# Hide kernel pointers in /proc/kallsyms from non-root users
kernel.kptr_restrict = 2

# Restrict ptrace scope to child processes only (Yama LSM)
kernel.yama.ptrace_scope = 1

# Disable unprivileged eBPF to prevent side-channel attacks (Spectre)
kernel.unprivileged_bpf_disabled = 1

# Enable BPF JIT compiler hardening (constant blinding)
net.core.bpf_jit_harden = 2

# Protect against symlink / hardlink race condition exploits in /tmp
fs.protected_symlinks = 1
fs.protected_hardlinks = 1
fs.protected_fifos = 2
fs.protected_regular = 2

# Disable TCP SACK if unpatched against CVE vulnerabilities
# net.ipv4.tcp_sack = 0
```

---

## 3. Kernel Module Signing & Verification

To prevent unauthorized kernel code execution, enforce cryptographically signed kernel modules:
- Kernel config: `CONFIG_MODULE_SIG=y` and `CONFIG_MODULE_SIG_FORCE=y`.
- When `CONFIG_MODULE_SIG_FORCE` is enabled, the kernel strictly refuses to load any module (`init_module` / `finit_module`) lacking a valid cryptographic signature matching a trusted public key in the kernel keyring.
