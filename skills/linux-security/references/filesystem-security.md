# Linux Filesystem & Storage Security: DAC, ACLs, and Mount Hardening

Technical reference for permissions, POSIX Access Control Lists (ACLs), mount flags, and encryption on Linux.

---

## 1. Discretionary Access Control (DAC) Permissions

Standard POSIX permissions enforce read (`r=4`), write (`w=2`), and execute (`x=1`) across owner, group, and others.

### Special Permission Bits:
- **Setuid (`04000`)**: Executes binary with permissions of file owner (usually root). High risk.
- **Setgid (`02000`)**: Executes with file group or causes newly created files in directory to inherit parent directory group.
- **Sticky Bit (`01000` / `+t`)**: In directories (e.g., `/tmp`), prevents users from deleting or renaming files owned by other users, even if directory is world-writable.

---

## 2. Mount Option Hardening

Harden partition mounts in `/etc/fstab` to neutralize executable binaries or setuid exploits in untrusted or writable partitions:

| Mount Flag | Security Effect | Recommended Partitions |
|---|---|---|
| `nodev` | Prevents character and block device files from being recognized or opened. | `/tmp`, `/var`, `/home`, `/dev/shm` |
| `nosuid` | Disables setuid and setgid execution bits on all binaries within the filesystem. | `/tmp`, `/var`, `/home`, `/dev/shm` |
| `noexec` | Blocks binary execution and prevents dynamic libraries from being mapped as executable. | `/tmp`, `/var/tmp`, `/dev/shm` |
| `ro` | Mounts filesystem as strictly read-only. | `/boot`, `/usr` (on immutable distros) |

### Example Hardened Mount in `/etc/fstab`:
```text
tmpfs   /tmp        tmpfs   rw,nosuid,nodev,noexec,relatime,size=2G   0 0
tmpfs   /dev/shm    tmpfs   rw,nosuid,nodev,noexec,relatime          0 0
```

---

## 3. POSIX Access Control Lists (ACLs)

When standard Owner/Group/Other permissions are too coarse (e.g., granting read access to a specific backup service user without opening permissions to all users in the group), use POSIX ACLs:

```bash
# View current ACLs
getfacl /var/log/my_app/audit.log

# Grant specific read access to user 'backup_daemon'
setfacl -m u:backup_daemon:r /var/log/my_app/audit.log

# Set default ACL for future files created in directory (-d)
setfacl -d -m u:backup_daemon:rx /var/log/my_app
```

---

## 4. Sensitive Data in Memory and Storage

1. **Core Dump Sanitization**:
   Core dumps contain full process memory, including plaintext passwords, encryption keys, and tokens.
   - Disable core dumps for sensitive processes: `prctl(PR_SET_DUMPABLE, 0)`.
   - In C/Rust: Lock sensitive buffers in RAM (`mlock`) to prevent paging to unencrypted swap.
2. **Explicit Zeroing of Buffers**:
   Never use standard `memset()` to clear cryptographic keys or passwords before freeing; optimizing compilers (GCC/Clang) treat `memset()` on dead memory as dead code and eliminate it completely.
   - Use `explicit_bzero()` (glibc) or `sodium_memzero()`.
