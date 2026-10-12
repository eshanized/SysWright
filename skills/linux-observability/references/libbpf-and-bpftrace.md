# eBPF Tooling: bpftrace Scripts, libbpf Skeletons, and Verifier Triage

Hands-on guide to authoring bpftrace one-liners and writing production C programs with libbpf skeletons.

---

## 1. Quick Ad-Hoc Tracing with bpftrace

`bpftrace` uses an AWK-like syntax to compile high-level tracing expressions into eBPF bytecode on the fly:

```bash
# 1. Trace all process executions (execve syscall) with arguments
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_execve { printf("PID %d (%s) executed %s\n", pid, comm, str(args->filename)); }'

# 2. Histogram of read() system call latency per process
sudo bpftrace -e '
tracepoint:syscalls:sys_enter_read { @start[tid] = nsecs; }
tracepoint:syscalls:sys_exit_read /@start[tid]/ {
    @latency[comm] = hist((nsecs - @start[tid]) / 1000);
    delete(@start[tid]);
}'

# 3. Count VFS open calls by file extension
sudo bpftrace -e 'kprobe:vfs_open { @[str(arg0)] = count(); }'
```

---

## 2. Production eBPF with libbpf and BPF Skeletons

For production daemons, write the eBPF kernel program in C and load it via `libbpf` skeleton generation:

### Kernel-Side eBPF Code (`my_trace.bpf.c`):
```c
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_core_read.h>

char LICENSE[] SEC("license") = "Dual BSD/GPL";

struct event {
    u32 pid;
    char comm[16];
};

struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024); // 256 KB ring buffer
} rb SEC(".maps");

SEC("tp/syscalls/sys_enter_openat")
int handle_openat(struct trace_event_raw_sys_enter *ctx)
{
    struct event *e;
    e = bpf_ringbuf_reserve(&rb, sizeof(*e), 0);
    if (!e)
        return 0;

    e->pid = bpf_get_current_pid_tgid() >> 32;
    bpf_get_current_comm(&e->comm, sizeof(e->comm));
    bpf_ringbuf_submit(e, 0);
    return 0;
}
```

### Build Workflow:
```bash
# 1. Compile eBPF program to ELF object
clang -g -O2 -target bpf -D__TARGET_ARCH_x86 -I/usr/include -c my_trace.bpf.c -o my_trace.bpf.o

# 2. Generate C skeleton header
bpftool gen skeleton my_trace.bpf.o > my_trace.skel.h

# 3. User-space C daemon includes my_trace.skel.h:
# struct my_trace_bpf *skel = my_trace_bpf__open_and_load();
# my_trace_bpf__attach(skel);
```

---

## 3. Triaging BPF Verifier Rejections

When the verifier rejects a BPF program, `libbpf` dumps the verifier log:

```text
libbpf: prog 'handle_openat': BPF program load failed: Permission denied
libbpf: -- BEGIN PROG LOAD LOG --
0: R1=ctx(off=0,imm=0) R10=fp0
; int handle_openat(struct trace_event_raw_sys_enter *ctx)
0: (bf) r6 = r1
...
12: (79) r3 = *(u64 *)(r6 + 16)
R6 invalid mem access 'inv'
-- END PROG LOAD LOG --
```

### Common Verifier Errors and Fixes:
| Verifier Message | Cause | Fix |
|---|---|---|
| `invalid mem access 'inv'` | Direct pointer dereference of kernel memory without safety bounds. | Use `bpf_core_read()` or `BPF_CORE_READ()` helper to read kernel pointers. |
| `R1 unbounded memory access` | Indexing an array with a variable whose upper bound is not proven to the verifier. | Mask or clamp index: `idx &= (MAX_ENTRIES - 1);` before array lookup. |
| `variable stack access var_off=...` | Using a dynamic runtime variable to index a stack buffer. | BPF does not allow dynamic stack offsets; use a map or constant index. |
| `back-edge from insn X to Y` | Loop condition lacks a static bound proven at verification time. | Use `#pragma unroll` or ensure loop has static bound `for (int i=0; i < 16; i++)`. |
