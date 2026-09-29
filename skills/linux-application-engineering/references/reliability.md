# Linux Application Reliability & Resilience Engineering

## 1. Scope & Reliability Principles

Compiling without errors does not guarantee application reliability. Production Linux applications must withstand sudden system restarts, out-of-memory (OOM) pressure, network timeouts, concurrent access conflicts, and hardware degradation:
- **Crash Recovery & Integrity**: Application state must be recoverable without data loss following sudden SIGKILL or power outage.
- **Defensive Resource Bounding**: Prevent resource leaks (file descriptors, memory, threads) under sustained load.
- **Fail-Safe Defaults**: When an operation encounters ambiguous or partially corrupted state, halt safely and preserve backups rather than executing destructive writes.

---

## 2. Lockfiles & Single-Instance Concurrency

When an application or daemon must ensure single-instance execution or serialize access to shared local databases:

### 2.1 Kernel Advisory Locking (`flock` vs `fcntl`)
- Prefer `flock(2)` (`LOCK_EX | LOCK_NB`) on an open file descriptor in `$XDG_RUNTIME_DIR/<app>.lock`:
  - `flock` locks are tied to the open file table entry and are **automatically released by the Linux kernel** when the process terminates (even upon `SIGKILL` or abnormal crash).
  - Legacy PID files containing written ASCII PIDs are prone to stale lock bugs: if a process crashes without unlinking `/run/app.pid`, another process with an unrelated recycled PID will appear to hold the lock.
  - With `flock`, the presence of the file does not indicate a lock; holding the open kernel lock indicates active ownership:

```c
#include <sys/file.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>

int acquire_single_instance_lock(const char *lockfile_path) {
    int fd = open(lockfile_path, O_CREAT | O_RDWR | O_CLOEXEC, 0600);
    if (fd < 0) return -1;

    if (flock(fd, LOCK_EX | LOCK_NB) < 0) {
        close(fd);
        return -1; /* Another instance is actively running */
    }

    /* Lock acquired successfully; retain 'fd' open for entire process lifetime */
    return fd;
}
```

---

## 3. Crash Handling & Post-Mortem Diagnostics

- **Core Dumps & `coredumpctl`**:
  - Do not catch `SIGSEGV`, `SIGBUS`, or `SIGILL` with custom handlers that attempt to resume execution. Corrupted memory state will cause cascading failures.
  - Let the Linux kernel generate an uncorrupted ELF core dump. Modern systemd-based distributions automatically capture and index core dumps via `systemd-coredump` (`coredumpctl`).
- **Preserving Debug Symbols**:
  - Compile with debug info enabled (`-g` or `-grecord-gcc-switches`) in both development and release builds.
  - Strip debug symbols into separate packages (e.g. `myapp-debug`) using `objcopy --only-keep-debug` during distribution packaging.

---

## 4. Resource Leak Prevention

| Resource Type | Common Leak Mechanism | Prevention & Diagnostic Tool |
|---|---|---|
| **File Descriptors** | Missing `close()` on error paths, missing `O_CLOEXEC` leaking FDs to child processes | Audit via `ls -la /proc/$PID/fd/`; use RAII wrappers; enforce `O_CLOEXEC` |
| **Heap Memory** | Unpaired `malloc`, circular reference in `std::shared_ptr` / GObject | AddressSanitizer (`-fsanitize=address`), Valgrind Memcheck |
| **Thread Accumulation** | Unjoined worker threads, blocked network sockets without timeouts | `std::jthread` (C++20), inspect `/proc/$PID/task/` |
| **Zombie Processes** | Spawning child processes via `fork` without reaping via `waitpid` | Handle `SIGCHLD` with `waitpid(-1, &status, WNOHANG)` |
