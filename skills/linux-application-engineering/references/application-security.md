# Native Linux Application Security Engineering

## 1. Scope & The Principle of Least Privilege

Application security begins with the premise that applications process untrusted inputs, operate in shared multi-user environments, and can be compromised. Software must run with the minimum privileges required to perform its function:
- **Never Run as Root**: Desktop applications, web-facing clients, and document parsers must never run with UID 0. If a privileged operation is required (e.g., configuring a network device or mounting a partition), delegate that specific action to a polkit-mediated helper service or unprivileged systemd unit.
- **Drop Privileges Immediately**: If an application requires binding a privileged port ($<1024$), use file capabilities (`setcap 'cap_net_bind_service=+ep' /usr/bin/myapp`) rather than running under `setuid root`.

---

## 2. Filesystem & Path Traversal Protections

### 2.1 Path Traversal Vulnerabilities
When processing user-supplied file paths, archive members (tar/zip), or network URIs:
- Never concatenate unverified strings with a root directory (e.g., `sprintf(path, "/var/data/%s", user_input);`). Paths containing `../` or leading `/` allow attackers to escape the sandbox.
- **Canonicalization & Boundary Checking**:
  1. Canonicalize the target path using `realpath(3)` or `std::fs::canonicalize()`.
  2. Verify that the canonicalized path starts with the base directory prefix.
- **Modern Linux Syscall: `openat2(2)` with `RESOLVE_BENEATH`**:
  ```c
  #include <sys/syscall.h>
  #include <linux/openat2.h>

  int open_safe_subpath(int dir_fd, const char *subpath) {
      struct open_how how = {
          .flags = O_RDONLY | O_CLOEXEC,
          .resolve = RESOLVE_BENEATH | RESOLVE_NO_MAGICLINKS,
      };
      return syscall(SYS_openat2, dir_fd, subpath, &how, sizeof(how));
  }
  ```
  `RESOLVE_BENEATH` instructs the Linux kernel VFS to immediately return `-EXDEV` if path resolution attempts to escape `dir_fd` via `..` or symlinks.

### 2.2 Symlink & Race Condition Attacks
- When creating files in shared directories (like `/tmp`), never use predictable file names with `fopen(path, "w")`. Attackers can pre-create a symlink pointing to `/etc/shadow` or other sensitive targets.
- Always use `mkstemp(3)` or `open(path, O_CREAT | O_EXCL | O_RDWR | O_CLOEXEC, 0600)`.
- Use `O_NOFOLLOW` when opening existing files to prevent trailing symlink redirection.

---

## 3. Command Execution & Process Spawning

### 3.1 Strict Prohibition of Shell Invocation
- Never invoke system shells via `system(command_string)` or `popen("cmd " + arg, "r")`. Shell invocation introduces command injection vulnerabilities via metacharacters (`;`, `|`, `&&`, `$()`, `` ` ``).
- Always use direct `execve(2)`, `posix_spawnp(3)`, or language equivalents (`std::process::Command` in Rust, `QProcess` in Qt, `GSubprocess` in GLib) passing explicit argument arrays:

```rust
// SECURE: Direct kernel process execution with discrete argv elements
use std::process::Command;

fn run_linter(file_path: &std::path::Path) -> std::io::Result<std::process::Output> {
    Command::new("/usr/bin/linter")
        .arg("--strict")
        .arg("--") // End of options guard
        .arg(file_path)
        .output()
}

// INSECURE ANTI-PATTERN: Shell interpolation
// Command::new("sh").arg("-c").arg(format!("linter {}", file_path.display())).output()
```

---

## 4. Secret Management & Memory Scrubbing

- **Memory Locking (`mlock`)**: Lock memory pages containing cryptographic keys or passwords using `mlock(2)` / `mlockall(MCL_CURRENT | MCL_FUTURE)` to prevent keys from being swapped to disk or included in core dumps.
- **Zeroing Sensitive Memory**: When freeing buffers holding passwords or keys, use `explicit_bzero(3)` (or `memset_s` / `zeroize` crate in Rust). Standard `memset()` calls can be optimized away by the compiler as dead stores.
- **Desktop Secret Storage**: Use the **Secret Service API** via D-Bus (`org.freedesktop.secrets`) or libsecret to store long-lived credentials securely in the user's encrypted keyring (GNOME Keyring / KWallet), rather than storing plaintext in configuration files.
