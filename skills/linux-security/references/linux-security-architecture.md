# Linux Security Architecture: Capabilities, Seccomp, Namespaces, and LSMs

Technical reference for core Linux kernel security primitives and sandboxing mechanisms.

---

## 1. POSIX Capabilities

Linux capabilities partition the monolithic power of the `root` user (UID 0) into 41 distinct privileges (`capabilities(7)`).

### Essential Capabilities:
- `CAP_NET_BIND_SERVICE`: Bind a socket to privileged ports (< 1024).
- `CAP_NET_ADMIN`: Configure interfaces, routing tables, and firewall rules.
- `CAP_SYS_ADMIN`: Overarching administrative capability (mount filesystems, load eBPF in older kernels). *Avoid granting this unless strictly required.*
- `CAP_PERFMON` (Linux 5.8+): Decouples performance profiling from `CAP_SYS_ADMIN`.
- `CAP_BPF` (Linux 5.8+): Decouples eBPF program loading and map creation from `CAP_SYS_ADMIN`.
- `CAP_DAC_OVERRIDE`: Bypass file read/write/execute permission checks.

### Inspecting and Dropping Capabilities:
```c
#include <sys/capability.h>

// Drop all capabilities except CAP_NET_BIND_SERVICE
cap_t caps = cap_init();
cap_value_t cap_list[1] = { CAP_NET_BIND_SERVICE };
cap_set_flag(caps, CAP_PERMITTED, 1, cap_list, CAP_SET);
cap_set_flag(caps, CAP_EFFECTIVE, 1, cap_list, CAP_SET);
cap_set_proc(caps);
cap_free(caps);
```

---

## 2. Seccomp-BPF (System Call Filtering)

Seccomp allows a process to restrict which system calls it and its children can invoke using BPF bytecode:

```c
#include <seccomp.h>

// Default-deny policy: kill process on any unlisted syscall
scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_KILL_PROCESS);

// Allow minimal syscalls needed for execution
seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(read), 0);
seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0);
seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit_group), 0);
seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(sigreturn), 0);

// Load filter into kernel
seccomp_load(ctx);
seccomp_release(ctx);
```

*Note: Before loading a seccomp filter without `CAP_SYS_ADMIN`, `prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)` must be set.*

---

## 3. Landlock (Unprivileged Application Sandboxing)

Available since Linux 5.13, Landlock allows unprivileged user-space processes to safely restrict their own filesystem and network access without requiring root or external LSM policies:

```c
#include <linux/landlock.h>
#include <sys/prctl.h>
#include <sys/syscall.h>

struct landlock_ruleset_attr attr = {
    .handled_access_fs = LANDLOCK_ACCESS_FS_READ_FILE |
                         LANDLOCK_ACCESS_FS_READ_DIR |
                         LANDLOCK_ACCESS_FS_WRITE_FILE,
};

int ruleset_fd = syscall(SYS_landlock_create_ruleset, &attr, sizeof(attr), 0);

// Add read-only rule for /usr and /etc
// Add read-write rule for workspace directory

prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0);
syscall(SYS_landlock_restrict_self, ruleset_fd, 0);
close(ruleset_fd);
```

---

## 4. Linux Security Modules (LSM)

LSM hooks are executed by the kernel before any critical kernel object (inode, socket, credential) is accessed.

- **AppArmor**: Path-based confinement (`/etc/apparmor.d/`). Easy to configure and audit with `aa-status` and `aa-enforce`.
- **SELinux**: Label-based type enforcement (TE). Every file and process has an SELinux context (`user:role:type:level`). Audited with `sestatus` and `audit2allow`.
- **Yama**: Restricts `ptrace(2)` system calls via `kernel.yama.ptrace_scope` (prevents malicious processes from attaching debuggers to other processes of the same user).
