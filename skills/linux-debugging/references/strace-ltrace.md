# System Call and Library Tracing: strace & ltrace

Guidance on intercepting system calls, signals, file descriptors, and dynamic library interactions.

---

## 1. System Call Tracing with strace

`strace` intercepts and records the system calls made by a process and signals received. It relies on `ptrace(PTRACE_SYSCALL)`.

### Essential CLI Invocations:
```bash
# Trace specific syscall categories (file, network, process, memory)
strace -e trace=file -o trace_file.txt ./my_app
strace -e trace=network,process ./my_app

# Trace child processes / threads (-f) with microsecond timestamps (-tt)
strace -f -tt -T -o app_trace.log ./my_daemon

# Filter specific failing calls (e.g. openat, connect) with return status
strace -e trace=openat,connect -e status=failed ./my_app

# Profile syscall timing and frequency (-c)
strace -c ./my_app

# Inspect string sizes up to 256 bytes (-s 256) and file descriptor paths (-y)
strace -s 256 -y -e trace=read,write ./my_app
```

### Key Flags Explained:
- `-f`: Follow fork, vfork, and clone calls (vital for multi-threaded applications and daemons).
- `-T`: Show elapsed wall-clock time spent inside each system call.
- `-tt`: Print microsecond timestamps (`HH:MM:SS.microseconds`) on each line.
- `-y`: Print file descriptor target paths (e.g., `3</var/log/app.log>`).
- `-yy`: Print socket peer addresses and protocol details alongside descriptor numbers.
- `-s <size>`: Maximum string size to display (default is 32; truncated strings display `...`).

---

## 2. Common strace Diagnostic Patterns

### A. Missing Configuration File or Permission Denied
```text
openat(AT_FDCWD, "/etc/myapp/config.yaml", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/home/user/.config/myapp/config.yaml", O_RDONLY|O_CLOEXEC) = -1 EACCES (Permission denied)
```
*Diagnosis*: Application tries fallback path, which fails due to bad directory permissions.

### B. TCP Connection Reset or Timeout
```text
socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, IPPROTO_TCP) = 3<TCP:[]>
connect(3<TCP:[192.168.1.50:8080]>, {sa_family=AF_INET, sin_port=htons(8080), sin_addr=inet_addr("192.168.1.50")}, 16) = -1 ECONNREFUSED (Connection refused) <0.000412>
```
*Diagnosis*: Target service is not listening on port 8080 or packet rejected immediately by firewall RST.

### C. Process Hanging on Deadlock or Unfulfilled Read
```text
futex(0x7ffff7c8b9d0, FUTEX_WAIT_PRIVATE, 2, NULL
```
*Diagnosis*: The last syscall is a blocking `futex` wait without timeout (`NULL`), indicating a thread deadlock or missing `futex_wake`.

---

## 3. Dynamic Library Call Tracing with ltrace

`ltrace` intercepts dynamic library calls made through the Procedure Linkage Table (PLT).

```bash
# Trace library calls to libc and custom libraries
ltrace -C -o ltrace.log ./my_app

# Trace calls to specific library only (-l)
ltrace -l libcrypto.so.3 ./my_app

# Show library calls and system calls (-S)
ltrace -S ./my_app
```

### Limitations of ltrace:
1. **PLT-Only**: Cannot intercept internal static functions or calls resolved within the same shared library.
2. **Architecture Support**: On modern x86_64, `ltrace` can fail or cause segmentation faults on binaries with modern relocations or full RELRO/PIE.
3. **Alternative**: Prefer `gdb` breakpoints, `uprobes` via `bpftrace`, or `LD_PRELOAD` hooks when `ltrace` is unreliable.

---

## 4. Overhead and Production Precautions

> [!WARNING]
> `ptrace` stops the traced thread on every entry and exit of every system call (2 context switches per syscall). For I/O-intensive workloads, `strace -f` can slow execution down by 10x-50x. Never run an unbounded `strace` on a high-throughput production database or network proxy without rate-limiting or specific syscall filters (`-e trace=...`).
