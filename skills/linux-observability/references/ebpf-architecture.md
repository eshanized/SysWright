# eBPF Architecture: Verifier, BTF, CO-RE, Maps, and Ring Buffers

Deep technical reference for modern extended Berkeley Packet Filter (eBPF) architecture on Linux.

---

## 1. The eBPF Execution Model

eBPF executes custom bytecode inside the Linux kernel in response to events (tracepoints, kprobes, network packets, cgroup events).

```
[eBPF C Code] ──(clang -target bpf)──► [ELF Bytecode] ──(bpf() syscall)──► [Kernel Verifier]
                                                                                   │
                                                      [JIT Compiler] ◄─────[Verifier Passed]
                                                            │
                                                  [Native Machine Code] ──► [Event Execution]
```

### Core Program Types:
- `BPF_PROG_TYPE_KPROBE`: Hook arbitrary kernel functions.
- `BPF_PROG_TYPE_TRACEPOINT`: Hook static kernel tracepoints.
- `BPF_PROG_TYPE_PERF_EVENT`: Sample on hardware counters or timer ticks.
- `BPF_PROG_TYPE_XDP`: Extreme high-performance network packet processing at NIC driver level.
- `BPF_PROG_TYPE_SCHED_CLS`: Traffic control (tc) network packet inspection/mutation.
- `BPF_PROG_TYPE_LSM`: Security policy enforcement on LSM hooks.

---

## 2. The BPF Verifier: Invariants & Rejection Rules

The BPF verifier performs static analysis on bytecode before loading to guarantee that the program cannot crash or freeze the host kernel.

### Strict Verifier Invariants:
1. **Guaranteed Termination**: No unbounded or infinite loops. In modern kernels (Linux 5.3+), bounded loops are permitted if the verifier can mathematically prove an upper iteration limit.
2. **Safe Memory Accesses**: Every pointer dereference is tracked with bounds. Out-of-bounds array indexing, NULL dereference, or unaligned access will cause immediate verifier rejection.
3. **Initialized Registers**: Reading a register before initializing it is strictly rejected.
4. **Stack Limit**: BPF stack size is strictly limited to 512 bytes. Allocating large structs on the stack triggers verifier rejection (use BPF maps for large storage).
5. **Instruction Limit**: The maximum program complexity is 1 million verified instructions.

---

## 3. BPF Type Format (BTF) & CO-RE (Compile Once - Run Everywhere)

Historically, BPF programs required kernel C headers on the target host and recompiled using BCC. Modern eBPF uses CO-RE:

1. **`vmlinux.h`**: A single generated C header containing all kernel types, structs, and enums from the running kernel (`bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h`).
2. **Clang CO-RE Relocations**: Clang emits field offset relocations in `.BTF.ext` ELF sections.
3. **libbpf Runtime Adjustment**: When loading the pre-compiled binary on a target kernel, `libbpf` inspects target `/sys/kernel/btf/vmlinux` and adjusts struct offsets automatically even if fields were added or reordered in the target kernel.

---

## 4. BPF Maps & Ring Buffers

BPF programs communicate with user-space through kernel memory-backed BPF Maps:

| Map Type | Purpose | Concurrency Behavior |
|---|---|---|
| `BPF_MAP_TYPE_HASH` | Key-value store | Thread-safe across CPUs; hash lookup overhead |
| `BPF_MAP_TYPE_ARRAY` | Fixed-size array indexed by integer | Fast constant-time access; pre-allocated |
| `BPF_MAP_TYPE_PERF_EVENT_ARRAY` | Legacy event streaming to user-space | Per-CPU buffer; events can arrive out of order across CPUs; memory overhead |
| `BPF_MAP_TYPE_RINGBUF` (Linux 5.8+) | Modern high-throughput event streaming | **Unified multi-CPU memory ring buffer**; in-order event delivery; zero memory waste; supports memory reservations (`bpf_ringbuf_reserve()`) |

> [!TIP]
> Always prefer `BPF_MAP_TYPE_RINGBUF` over `BPF_MAP_TYPE_PERF_EVENT_ARRAY` for new eBPF programs on kernels $\ge 5.8$. It consumes significantly less memory and guarantees global event ordering.
