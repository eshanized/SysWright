# Linux Native Observability: /proc, /sys, PSI, and cgroups v2

Technical reference for extracting low-overhead telemetry from Linux kernel native pseudo-filesystems.

---

## 1. Key Virtual Filesystems for Observability

Linux provides kernel telemetry directly through memory-backed virtual filesystems without requiring third-party agents:

- `/proc`: Process metrics, hardware info, and global kernel state.
- `/sys`: Device topology, kernel modules, bus architectures, and subsystem parameters.
- `/sys/fs/cgroup`: cgroups v2 resource accounting and limits.
- `/sys/kernel/tracing`: tracefs interface for ftrace and tracepoints.

---

## 2. Pressure Stall Information (PSI)

Introduced in Linux 4.20, PSI provides accurate metrics on resource starvation across CPU, Memory, and I/O (`/proc/pressure/cpu`, `/proc/pressure/memory`, `/proc/pressure/io`):

```bash
cat /proc/pressure/memory
```

```text
some avg10=0.15 avg60=0.08 avg300=0.02 total=1420108
full avg10=0.00 avg60=0.00 avg300=0.00 total=849102
```

### Understanding `some` vs `full`:
- **`some`**: The percentage of wall-clock time that *at least some* tasks were stalled on the resource (e.g., waiting for memory paging or swap), while other non-stalled tasks were still running on CPU cores.
- **`full`**: The percentage of wall-clock time that *all* non-idle tasks on the system were stalled on the resource simultaneously (complete system starvation / thrashing).
*Significance*: High `some` indicates emerging resource pressure; any non-zero `full` indicates severe system-wide bottleneck and degradation.

---

## 3. cgroups v2 Resource Accounting

Under unified cgroups v2 (`/sys/fs/cgroup/`):

```bash
# Total CPU usage in microseconds for a systemd service slice
cat /sys/fs/cgroup/system.slice/my_service.service/cpu.stat
# usage_usec 14592019
# user_usec 10240182
# system_usec 4351837
# nr_throttled 0

# Current physical memory consumption
cat /sys/fs/cgroup/system.slice/my_service.service/memory.current

# Memory peak since boot
cat /sys/fs/cgroup/system.slice/my_service.service/memory.peak

# Total I/O bytes read/written per block device
cat /sys/fs/cgroup/system.slice/my_service.service/io.stat
# 259:0 rbytes=10485760 wbytes=41943040 rios=256 wios=1024
```

---

## 4. Kernel Load Averages vs CPU Saturation

`/proc/loadavg` displays the 1, 5, and 15 minute exponential moving averages:
```text
2.45 1.80 1.20 3/892 14820
```
- In Linux (unlike UNIX/BSD), load average includes both tasks in `TASK_RUNNING` (on CPU or waiting on runqueue) **and** tasks in `TASK_UNINTERRUPTIBLE` (D state, usually blocked on disk I/O or network NFS mounts).
- A high load average on Linux does **not** necessarily mean the CPU is overloaded; it may mean threads are blocked waiting on slow disk or SAN storage. Check `/proc/stat` and PSI to confirm.
