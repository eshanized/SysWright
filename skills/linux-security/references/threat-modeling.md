# Linux Threat Modeling & Attack Surface Analysis

Methodological reference for identifying assets, trust boundaries, entry points, and threats on Linux systems.

---

## 1. Defining Trust Boundaries

A trust boundary is an architectural interface where data or execution transitions between different privilege levels or domains of control.

### Common Linux Trust Boundaries:
1. **Network $\to$ User-Space Daemon**: Untrusted remote packets received over TCP/UDP sockets.
2. **User-Space Application $\to$ Kernel**: System calls (`int 0x80`, `syscall`, `sysenter`) mediated by seccomp and the kernel syscall handler.
3. **Unprivileged Client $\to$ Privileged Daemon**: Local IPC over UNIX domain sockets, D-Bus System Bus, or FIFO pipes.
4. **Local User $\to$ File System**: File operations mediated by VFS DAC (Discretionary Access Control: UID/GID permissions) and MAC (SELinux / AppArmor).
5. **Host $\to$ Container**: Isolation mediated by cgroups v2, namespaces, and seccomp filters.

---

## 2. The STRIDE Threat Classification

Apply STRIDE at each trust boundary:

| Threat Category | Property Violated | Linux Example | Mitigation Strategy |
|---|---|---|---|
| **Spoofing** | Authenticity | Impersonating local user via forged UNIX socket credentials. | Use `SO_PEERCRED` / `SCM_CREDENTIALS` to query kernel for caller's true UID/GID. |
| **Tampering** | Integrity | Overwriting shared configuration files or binary libraries. | Mount `/usr` read-only (`ProtectSystem=strict`), verify checksums/signatures. |
| **Repudiation** | Non-repudiability | Denying performing an administrative action or security change. | Audit logging via `auditd` or journald with immutable forward-secure sealing. |
| **Information Disclosure** | Confidentiality | Leaking private keys or core dumps to world-readable directories. | `PrivateTmp=yes`, `chmod 600`, restrict core dumps via `fs.suid_dumpable=0`. |
| **Denial of Service** | Availability | Exhausting file descriptors or CPU via connection flooding. | cgroups v2 resource limits (`MemoryMax=`, `CPUQuota=`), `RLIMIT_NOFILE`. |
| **Elevation of Privilege** | Authorization | Exploiting setuid root binary or abusing missing capability checks. | Drop setuid binaries; use narrow Linux capabilities; set `NoNewPrivileges=yes`. |

---

## 3. Attack Surface Enumeration Checklist

Before declaring a system or application secure, audit:

- **Listening Network Sockets**:
  ```bash
  ss -tulpn
  ```
  *Rule*: No service should listen on `0.0.0.0` (all interfaces) if it is intended only for local communication (`127.0.0.1` or UNIX socket).
- **Installed Setuid/Setgid Binaries**:
  ```bash
  find /usr -perm /6000 -type f -exec ls -ld {} +
  ```
  *Rule*: Audit all setuid binaries; replace with systemd services or file capabilities where possible.
- **World-Writable Files and Directories**:
  ```bash
  find / -xdev -type d \( -perm -0002 -a ! -perm -1000 \) -ls
  ```
  *Rule*: Sticky bit (`chmod +t`) must be set on any world-writable directory (e.g., `/tmp`, `/var/tmp`) to prevent symlink race attacks.
- **D-Bus System Bus Interfaces**:
  Audit `/etc/dbus-1/system.d/` policy files for unrestricted `<allow send_interface="..."/>` rules allowing arbitrary users to invoke privileged methods.
