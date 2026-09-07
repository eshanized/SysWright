# Linux Kernel Architecture & Subsystem Reference

## 1. Scope

This document provides a technical reference on Linux kernel architecture, internal subsystems, memory management, process scheduling, concurrency primitives, and module architecture. It guides AI agents in conducting grounded kernel investigations without relying on assumed or obsolete APIs.

---

## 2. Kernel Source Tree Organization

```text
linux/
├── arch/         # Architecture-specific code (x86, arm64, riscv, etc.)
│   └── x86/      # x86_64 boot, entry, mm, and hardware setup
├── block/        # Block device core layer (blk-mq, I/O schedulers)
├── drivers/      # Device drivers categorized by subsystem (pci, net, usb, nvme)
├── fs/           # Virtual Filesystem (VFS) and filesystem drivers (ext4, btrfs, xfs)
├── include/      # Kernel header files
│   ├── linux/    # Core kernel API headers
│   └── uapi/     # Userspace API headers (stable syscall ABI)
├── init/         # Kernel initialization (main.c, early init, version)
├── ipc/          # System V and POSIX IPC implementations
├── kernel/       # Core subsystems (sched, locking, irq, time, workqueue, bpf)
├── mm/           # Memory management (page allocator, slub, vmalloc, page cache)
├── net/          # Network stack implementations (ipv4, ipv6, netfilter, core)
├── scripts/      # Kbuild helper scripts, checkpatch.pl, get_maintainer.pl
└── tools/        # Userspace development tools (perf, selftests, bpf, objtool)
```

---

## 3. Core Subsystems Architecture

### 3.1 Task & Process Management
- **`struct task_struct`** (`include/linux/sched.h`): Represents every thread/process in the system. Holds PID, credentials (`struct cred`), memory context (`struct mm_struct`), open files (`struct files_struct`), signal handlers, and execution state.
- **Process Scheduling**:
  - **EEVDF (Earliest Eligible Virtual Deadline First)**: Default scheduler in Linux 6.6+ (replacing CFS). Schedules tasks based on lag and virtual deadlines to ensure latency sensitivity and fair time allocation.
  - Real-Time scheduling classes: `SCHED_FIFO` and `SCHED_RR`.
  - Deadline scheduling class: `SCHED_DEADLINE` (EDF + Constant Bandwidth Server).

### 3.2 Memory Management
- **Physical Page Allocation**:
  - Core allocator: Buddy allocator managing contiguous power-of-two page blocks (`struct page`).
  - Allocation API: `alloc_pages()`, `free_pages()`, `get_zeroed_page()`.
  - **GFP (Get Free Page) Flags**:
    - `GFP_KERNEL`: Normal blocking allocation. May sleep, trigger writeback, or compact memory. Used in process context.
    - `GFP_ATOMIC`: Non-blocking allocation. Never sleeps; safe in interrupt handlers and atomic sections with held spinlocks.
    - `GFP_NOWAIT`: Non-blocking, does not sleep.
    - `GFP_DMA` / `GFP_DMA32`: Allocates from lower physical address zones for legacy DMA.
- **Slab / Slub Allocator**:
  - `kmalloc()` / `kfree()`: General-purpose memory allocator for byte-sized allocations up to ~4MB. Returns physically contiguous memory.
  - `kmem_cache_create()` / `kmem_cache_alloc()`: Dedicated object caches for frequently allocated fixed-size structures (e.g., `inode_cache`, `dentry_cache`).
- **Virtual Memory (`vmalloc`)**:
  - `vmalloc()` / `vfree()`: Allocates virtually contiguous, physically non-contiguous memory pages. Slower than `kmalloc()`, requires page table manipulation.

### 3.3 Synchronization & Concurrency
- **Spinlocks** (`spinlock_t`): Busy-waiting lock for short critical sections.
  - Invariants: Must NEVER sleep while holding a spinlock (`kmalloc(GFP_KERNEL)` or `msleep()` is forbidden). Disable interrupts if shared with an IRQ handler (`spin_lock_irqsave()`).
- **Mutexes** (`struct mutex`): Sleeping lock for process context. Task sleeps when contested; cannot be used in atomic/interrupt context.
- **Read/Write Semaphores** (`struct rw_semaphore`): Sleeping lock permitting concurrent readers or exclusive writers.
- **Atomic Operations** (`atomic_t`, `atomic64_t`): Hardware-atomic integers (`atomic_inc()`, `atomic_cmpxchg()`).
- **RCU (Read-Copy Update)**:
  - Reader lock-free primitive: Readers enter with `rcu_read_lock()` and exit with `rcu_read_unlock()`. Readers do not lock out writers.
  - Writers create copies of structures, update pointers atomically with `rcu_assign_pointer()`, and defer reclaiming old memory until all readers have exited quiescent states via `synchronize_rcu()` or `call_rcu()`.

### 3.4 Workqueues & Deferred Execution
- **Workqueues** (`struct work_struct`, `struct workqueue_struct`):
  - Executes deferred tasks in process context (`kworker` threads).
  - Can sleep, allocate memory with `GFP_KERNEL`, and acquire mutexes.
  - Concurrency Managed Workqueues (cmwq) dynamically balance worker thread pools.
- **Timers** (`struct timer_list`):
  - Modern API (Linux 4.15+): Initialized via `timer_setup(timer, callback, flags)`.
  - Obsolete API: `init_timer()` and direct function pointers were removed in 4.15.
  - Runs in software interrupt (`SOFTIRQ`) atomic context; cannot sleep.

---

## 4. Kernel Module Architecture

```c
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Linux Systems Engineer");
MODULE_DESCRIPTION("Core subsystem integration module");
MODULE_VERSION("1.0");

static int __init my_module_init(void)
{
    pr_info("Module loaded successfully\n");
    return 0;
}

static void __exit my_module_exit(void)
{
    pr_info("Module unloaded\n");
}

module_init(my_module_init);
module_exit(my_module_exit);
```

- **Symbol Exporting**:
  - `EXPORT_SYMBOL(symbol_name)`: Exports function or variable to all kernel modules.
  - `EXPORT_SYMBOL_GPL(symbol_name)`: Restricts symbol usage to modules with GPL-compatible `MODULE_LICENSE`.

---

## 5. Authoritative References

- [Linux Kernel Documentation: Core API](https://docs.kernel.org/core-api/index.html)
- [Linux Kernel Memory Management](https://docs.kernel.org/mm/index.html)
- [Linux Kernel Scheduler Architecture](https://docs.kernel.org/scheduler/index.html)
- [Locking in the Linux Kernel](https://docs.kernel.org/locking/index.html)
