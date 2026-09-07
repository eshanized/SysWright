# Kernel Debugging, Tracing & Crash Analysis Reference

## 1. Scope

This document details diagnostic techniques for kernel panics, Oops call traces, dynamic tracing via ftrace, eBPF inspection, and crash dumps.

---

## 2. Decoding Kernel Panics & Oops Call Traces

A kernel Oops represents an unhandled exception (e.g., page fault on NULL pointer dereference) in kernel mode:

```text
[   21.340120] BUG: kernel NULL pointer dereference, address: 0000000000000018
[   21.340310] #PF: supervisor read access in kernel mode
[   21.340450] #PF: error_code(0x0000) - not-present page
[   21.340600] PGD 0 P4D 0
[   21.340700] Oops: 0000 [#1] PREEMPT SMP NOPTI
[   21.340850] CPU: 2 PID: 450 Comm: worker Tainted: G           O      6.18.64 #1
[   21.341050] RIP: 0010:e1000_probe+0x54/0x320 [e1000e]
[   21.341200] Code: 48 89 df e8 4a ...
[   21.341350] RSP: 0018:ffffc900004b3c10 EFLAGS: 00010246
[   21.341500] RAX: 0000000000000000 RBX: ffff888102a30000 RCX: 0000000000000000
```

### Key Diagnostic Elements:
1. **Fault Address**: `address: 0000000000000018` indicates a structure member dereference at offset `0x18` from a NULL base pointer.
2. **RIP Register**: `e1000_probe+0x54/0x320` identifies the exact instruction offset within the function.
3. **Translating RIP with `faddr2line`**:
   ```bash
   ./scripts/faddr2line drivers/net/ethernet/intel/e1000e/e1000e.ko e1000_probe+0x54
   # Output gives exact source file and line number:
   # e1000_probe+0x54/0x320: e1000_main.c:1204
   ```
4. **Tainted Flags**:
   - `G`: All modules loaded are GPL compliant.
   - `P`: Proprietary module loaded.
   - `F`: Module was force-loaded.
   - `O`: Out-of-tree module loaded.
   - `W`: Kernel emitted a warning previously.

---

## 3. Kernel Tracing Infrastructure

### 3.1 `ftrace` (Function Tracer)
Located in `/sys/kernel/tracing/`:
```bash
# 1. Select function tracer
echo function_graph > /sys/kernel/tracing/current_tracer

# 2. Filter specific function
echo e1000_probe > /sys/kernel/tracing/set_ftrace_filter

# 3. Enable and inspect output
echo 1 > /sys/kernel/tracing/tracing_on
sleep 1
echo 0 > /sys/kernel/tracing/tracing_on
cat /sys/kernel/tracing/trace | head -n 30
```

### 3.2 Dynamic Debug (`dyndbg`)
Enables runtime debug logging for specific files or functions without rebuilding the kernel:
```bash
# Enable debug messages in e1000e driver
echo "module e1000e +p" > /proc/dynamic_debug/control
```

---

## 4. Emergency Controls: Magic SysRq

Configured via `/proc/sys/kernel/sysrq`:
- `Alt + SysRq + b`: Immediate reboot without unmounting or syncing (dangerous).
- `Alt + SysRq + c`: Force crash/panic to generate a crash dump.
- `Alt + SysRq + s`: Synchronize filesystems to disk.
- `Alt + SysRq + u`: Remount all filesystems read-only.
- **Safe Emergency Reboot Sequence**: **`REISUB`**
  - **R**aw keyboard mode $\to$ **E**xecute SIGTERM $\to$ **I**mmediate SIGKILL $\to$ **S**ync disks $\to$ **U**nmount to RO $\to$ Re**B**oot.

---

## 5. Authoritative References

- [Kernel Oops and Panic Analysis](https://docs.kernel.org/admin-guide/bug-hunting.html)
- [ftrace - Function Tracer](https://docs.kernel.org/trace/ftrace.html)
- [Dynamic Debug Howto](https://docs.kernel.org/admin-guide/dynamic-debug-howto.html)
- [Magic SysRq Key Documentation](https://docs.kernel.org/admin-guide/sysrq.html)
