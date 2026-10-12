# Linux Native Tracing: ftrace, Tracepoints, Kprobes, and Uprobes

Technical reference for tracing kernel and user-space function execution using native kernel facilities.

---

## 1. ftrace and tracefs

`ftrace` is the official built-in Linux kernel tracer. It is controlled by reading and writing files in `tracefs` (mounted at `/sys/kernel/tracing`):

### Tracing Function Call Graphs:
```bash
# Set tracer to function_graph
echo function_graph > /sys/kernel/tracing/current_tracer

# Filter only functions matching ext4_file_*
echo "ext4_file_*" > /sys/kernel/tracing/set_ftrace_filter

# Enable tracing
echo 1 > /sys/kernel/tracing/tracing_on

# Read trace buffer
head -n 30 /sys/kernel/tracing/trace

# Reset and disable
echo 0 > /sys/kernel/tracing/tracing_on
echo nop > /sys/kernel/tracing/current_tracer
echo > /sys/kernel/tracing/set_ftrace_filter
```

---

## 2. Kernel Tracepoints

Tracepoints are statically defined probes embedded directly into kernel C source code using `TRACE_EVENT()` macros:
- Stable across kernel versions (unlike kprobes, which depend on internal unexported function signatures).
- Negligible overhead when inactive (single-instruction conditional jump or `nop`).

### Listing and Enabling Available Tracepoints:
```bash
# List all available tracepoints
cat /sys/kernel/tracing/available_events | grep "sched:sched_switch"

# Enable scheduling switch tracepoint
echo 1 > /sys/kernel/tracing/events/sched/sched_switch/enable

# View event format and argument layout
cat /sys/kernel/tracing/events/sched/sched_switch/format
```

---

## 3. Dynamic Kprobes vs Uprobes

| Feature | Kprobes / Kretprobes | Uprobes / Uretprobes |
|---|---|---|
| **Target Space** | Linux Kernel Space | User Space Executables & Shared Libraries |
| **Hook Mechanism** | In-place instruction breakpoint (`int3` on x86) in kernel text | In-place instruction breakpoint in user virtual memory |
| **Stability** | Internal kernel function names can change or be inlined between kernel minor releases. | Function symbols depend on exported ELF dynamic symbol table (`.dynsym`). |
| **Latency / Cost** | ~50-100 nanoseconds per hit | ~1-3 microseconds per hit (involves context switch to kernel trap handler and back). |

### Example: Tracing SSL/TLS Plaintext with Uprobes
Because uprobes hook user space, they can inspect payloads immediately before encryption in OpenSSL:
```bash
# Hook SSL_write in libssl.so
sudo bpftrace -e '
uprobe:/usr/lib/libssl.so.3:SSL_write {
    printf("PID %d writing %d bytes: %s\n", pid, arg2, str(arg1, arg2));
}'
```
*(Demonstrates uprobe power, and why access to uprobes requires root privileges to protect sensitive data).*
