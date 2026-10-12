# Native Application Security: Memory Safety, Injection, and Insecure Temporary Files

Technical reference for preventing and auditing memory corruption, command injection, path traversal, and temporary file race conditions in native Linux software.

---

## 1. Command Injection Prevention

Never construct shell commands by string concatenation:

### Vulnerable C Code:
```c
// VULNERABLE: Command injection via filename
char command[512];
snprintf(command, sizeof(command), "tar -czf /backup/archive.tar.gz %s", user_filename);
system(command); // Attacker sets user_filename = "file; rm -rf /"
```

### Secure C Code:
Execute binaries directly with vector arguments using `execve` or `posix_spawn`, bypassing the shell completely:
```c
#include <spawn.h>

char *argv[] = { "tar", "-czf", "/backup/archive.tar.gz", user_filename, NULL };
pid_t pid;
posix_spawnp(&pid, "tar", NULL, NULL, argv, environ);
waitpid(pid, NULL, 0);
```

---

## 2. Path Traversal & Symlink Attacks

When processing user-supplied file paths, attackers supply relative path traversal sequences (`../../etc/shadow`) or point symlinks to restricted files.

### Mitigation:
1. **Canonicalize Paths with `realpath(3)`**:
   Verify that the canonicalized destination path starts with the trusted root directory:
   ```c
   char resolved[PATH_MAX];
   if (!realpath(user_path, resolved) || strncmp(resolved, ALLOWED_BASE_DIR, strlen(ALLOWED_BASE_DIR)) != 0) {
       // Reject path traversal attempt
       return -EACCES;
   }
   ```
2. **`O_NOFOLLOW` and `openat2(2)` with `RESOLVE_BENEATH`**:
   In modern Linux (kernel 5.6+), `openat2` provides kernel-enforced path resolution restrictions:
   ```c
   struct open_how how = {
       .flags = O_RDONLY | O_CLOEXEC,
       .resolve = RESOLVE_BENEATH | RESOLVE_NO_SYMLINKS,
   };
   int fd = syscall(SYS_openat2, dirfd, user_subpath, &how, sizeof(how));
   ```
   *The kernel will atomically reject any path resolving outside `dirfd` or traversing a symlink.*

---

## 3. Secure Temporary File Handling

Creating temporary files in `/tmp` using predictable names (`/tmp/my_app.tmp`) is vulnerable to symlink race conditions (`TOCTOU`: Time-Of-Check to Time-Of-Use). An unprivileged attacker creates a symlink `/tmp/my_app.tmp -> /etc/shadow` before the application writes to it.

### Vulnerable Patterns:
- Using `tmpnam()`, `tempnam()`, or `mktemp()` (flagged as insecure by all modern linkers).
- `fopen("/tmp/tempfile", "w")`.

### Secure Implementation:
Always use `mkstemp(3)` or `open(..., O_TMPFILE)`:
```c
// Secure method 1: mkstemp
char template[] = "/tmp/myapp_XXXXXX";
int fd = mkstemp(template);
// Automatically creates file with permissions 0600 (owner read/write only)

// Secure method 2: Anonymous O_TMPFILE (Linux 3.11+)
int fd = open("/tmp", O_TMPFILE | O_RDWR | O_EXCL, 0600);
// An unnamed temporary file that leaves no inode in /tmp directory tree
```

---

## 4. Compiler Hardening Flags

Ensure build systems enforce full compiler and linker hardening flags:

```makefile
CFLAGS += -O2 -g -Wall -Wextra -Wformat -Wformat-security \
          -fstack-protector-strong \
          -fstack-clash-protection \
          -D_FORTIFY_SOURCE=3 \
          -D_GLIBCXX_ASSERTIONS \
          -fPIE

LDFLAGS += -Wl,-z,relro -Wl,-z,now -Wl,-z,noexecstack -pie
```
