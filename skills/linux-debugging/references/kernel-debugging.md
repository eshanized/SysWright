# Linux Kernel Debugging: Panics, Oopses, KASAN, and Lockdep

Technical reference for diagnosing Linux kernel crashes, lock inversions, and hardware driver faults.

---

## 1. Anatomy of a Kernel Panic and Oops

A kernel "Oops" is a kernel-space exception where an illegal operation occurred (e.g., NULL pointer dereference, page fault in interrupt context). If the kernel cannot safely recover (or if `panic_on_oops=1`), it transitions into a full "Panic".

### Kernel Oops Header Inspection:
```text
[   42.105432] BUG: kernel NULL pointer dereference, address: 0000000000000018
[   42.105445] #PF: supervisor read access in kernel mode
[   42.105450] #PF: error_code(0x0000) - not-present page
[   42.105455] PGD 0 P4D 0 
[   42.105460] Oops: 0000 [#1] PREEMPT SMP PTI
[   42.105467] CPU: 2 PID: 1482 Comm: my_kthread Tainted: G           O       6.6.10-arch1-1 #1
[   42.105474] RIP: 0010:my_device_read+0x42/0x120 [my_driver]
[   42.105481] Code: 48 89 e5 41 57 41 56 53 48 83 ec 18 48 89 7d e0 48 8b 47 18 <48> 8b 40 18 48 89 45 d8
[   42.105490] RSP: 0018:ffffc90001a5bd80 EFLAGS: 00010286
[   42.105495] RAX: 0000000000000000 RBX: ffff888104a29800 RCX: 0000000000000000
[   42.105500] RDX: 0000000000000000 RSI: ffffc90001a5be00 RDI: ffff888104a29800
```

### Critical Fields:
- **Fault Address**: `0000000000000018` — This is an offset (`0x18`) from a base pointer of `0x0` (`NULL` pointer struct dereference).
- **RIP (Instruction Pointer)**: `my_device_read+0x42/0x120 [my_driver]` — Function and offset within module.
- **Code `<48> 8b 40 18`**: The bracketed byte is the exact opcode where the fault occurred (`mov 0x18(%rax), %rax`). Since `%rax` is `0x0000000000000000`, reading `0x18(%rax)` triggers a page fault on an unmapped page.
- **Taint Flags**:
  - `G`: Proprietary module has not been loaded (GPL).
  - `O`: Out-of-tree module has been loaded.
  - `P`: Proprietary module loaded.

---

## 2. Kernel Lockdep: Runtime Lock Dependency Validator

Lockdep tracks lock acquisition order across all CPUs and contexts to detect potential deadlocks before they occur in practice:

```text
[   55.321000] =================================
[   55.321002] WARNING: possible circular locking dependency detected
[   55.321005] 6.6.10-debug #1 Tainted: G
[   55.321008] ---------------------------------
[   55.321010] my_worker/1452 is trying to acquire lock:
[   55.321013]  (&dev->lock_B){+.+.}-{2:2}, at: worker_b_func+0x24/0x50 [my_driver]
[   55.321020] but task is already holding lock:
[   55.321022]  (&dev->lock_A){+.+.}-{2:2}, at: worker_b_func+0x18/0x50 [my_driver]
[   55.321029] which lock already depends on the new lock!
```

---

## 3. Kernel Address Sanitizer (KASAN)

KernelAddressSanitizer detects out-of-bounds accesses and use-after-free defects in slab, page_alloc, and stack memory.

### KASAN Defect Output:
```text
[   60.102300] ==================================================================
[   60.102305] BUG: KASAN: slab-use-after-free in my_driver_send+0x34/0x80 [my_driver]
[   60.102312] Read of size 8 at addr ffff88810234a010 by task kworker/2:1/89
[   60.102318] 
[   60.102322] Allocated by task 1450:
[   60.102326]  kmem_cache_alloc+0x140/0x320
[   60.102330]  my_driver_alloc_packet+0x20/0x60 [my_driver]
[   60.102335] 
[   60.102338] Freed by task 1450:
[   60.102342]  kfree+0x90/0x240
[   60.102346]  my_driver_free_packet+0x18/0x40 [my_driver]
[   60.102350] ==================================================================
```

---

## 4. Kernel Debugging Tools & Infrastructure

- **Dynamic Debug**: Enable printks per-file, per-function, or per-line without rebuilding:
  ```bash
  echo "module my_driver +p" > /sys/kernel/debug/dynamic_debug/control
  ```
- **ftrace**: Trace function execution callgraphs in the kernel:
  ```bash
  echo function_graph > /sys/kernel/tracing/current_tracer
  echo my_driver_* > /sys/kernel/tracing/set_ftrace_filter
  echo 1 > /sys/kernel/tracing/tracing_on
  ```
- **QEMU + GDB**: Always debug custom kernels in a QEMU VM:
  ```bash
  qemu-system-x86_64 -kernel arch/x86/boot/bzImage -append "console=ttyS0 root=/dev/sda nokaslr" -s -S
  gdb vmlinux -ex "target remote :1234"
  ```
  *(Note: `nokaslr` is mandatory to disable Kernel Address Space Layout Randomization so GDB symbols align with runtime virtual addresses).*
