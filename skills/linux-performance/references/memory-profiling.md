# Linux Memory Profiling: RSS, PSS, Page Faults, and Heap Analysis

Technical reference for measuring physical memory consumption, allocation hotspots, page faults, and fragmentation.

---

## 1. Physical vs Virtual Memory on Linux

A frequent misconception is treating Virtual Size (`VSZ`) as actual memory consumption.

| Metric | Definition | Significance |
|---|---|---|
| **VSZ (Virtual Size)** | Total address space allocated (mapped files, shared libs, allocated but untouched pages). | Informational only. High VSZ does NOT mean physical RAM is exhausted. |
| **RSS (Resident Set Size)** | Physical RAM pages currently mapped into the process's page table. | Includes shared libraries mapped into other processes; summing RSS across processes double-counts shared memory. |
| **PSS (Proportional Set Size)** | RSS divided proportionally among all processes sharing the page. | **Most accurate representation** of physical RAM consumed by a single process. |
| **USS (Unique Set Size)** | Memory private to this specific process alone (freed if process dies). | Exact RAM saved if process is terminated. |

### Inspecting PSS and USS via `/proc/PID/smaps_rollup`:
```bash
cat /proc/$(pgrep my_app)/smaps_rollup | grep -E '^(Rss|Pss|Private_Clean|Private_Dirty):'
```

Using `smem` (proportional memory reporter):
```bash
smem -t -k -c "pid user command pss rss uss" | grep my_app
```

---

## 2. Page Faults: Minor vs Major

Page faults occur when a process accesses a virtual address not currently backed by a physical page table entry:

### Minor Page Faults (`flt/s`):
- The requested page is already in the OS page cache or is a fresh anonymous allocation (zero-fill-on-demand).
- Satisfied entirely in RAM (CPU trap $\to$ update page table $\to$ resume execution).
- Low latency (~1 microsecond), but thousands per second consume measurable CPU cycles.

### Major Page Faults (`majflt/s`):
- The page must be read synchronously from disk (storage I/O required) because it was swapped out or is a cold file-backed mapping.
- High latency (milliseconds on HDD, microseconds on NVMe).
- Major page faults during critical application paths cause severe latency spikes (UI stutter, dropped frames).

```bash
# Monitor page faults per second for PID
pidstat -r -p $(pgrep my_app) 1
```

---

## 3. Heap Allocation Profiling with heaptrack

`heaptrack` tracks every allocation (`malloc`, `calloc`, `realloc`, `free`, `new`, `delete`) with full stack traces, tracking peak heap consumption, temporary allocations, and memory leaks.

```bash
# Profile application execution
heaptrack ./my_app

# Analyze results in CLI
heaptrack --analyze heaptrack.my_app.4821.zst
```

### Key Metrics Reported by heaptrack:
1. **Peak Heap Usage**: High-water mark of allocated memory.
2. **Temporary Allocations**: Allocations immediately followed by a free (short-lived buffers). High counts cause memory fragmentation and allocator lock contention.
3. **Leaked Memory**: Allocations never freed at termination.

---

## 4. Allocator Fragmentation & glibc Tunables

glibc's `ptmalloc` maintains multiple memory arenas (up to $8 \times \text{CPU cores}$).
- When multiple threads allocate memory, each thread gets its own arena to avoid lock contention.
- However, excessive arenas can lead to high virtual address space fragmentation and retained heap memory (`MALLOC_ARENA_MAX`).

```bash
# Restrict arena count to reduce fragmentation in multi-threaded daemons
export MALLOC_ARENA_MAX=2

# Force glibc to return unused heap memory to OS aggressively
export MALLOC_TRIM_THRESHOLD_=131072  # 128 KB
```
Alternatively, for allocation-heavy multi-threaded applications, benchmark replacing `ptmalloc` with `mimalloc` or `jemalloc` (`LD_PRELOAD=/usr/lib/libjemalloc.so.2`).
