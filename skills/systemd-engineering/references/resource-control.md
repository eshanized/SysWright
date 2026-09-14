# systemd Resource Control & cgroups v2 Reference

## 1. Scope

This document details resource management, CPU quotas, memory limits, task limits, and cgroups v2 integration in systemd.

---

## 2. cgroups v2 Unified Hierarchy

Modern Linux systems run cgroups v2 (`/sys/fs/cgroup/`) as a single unified hierarchy:
- System services reside in `system.slice` (e.g. `system.slice/nginx.service`).
- User sessions reside in `user.slice` (e.g. `user-1000.slice/user@1000.service`).
- Background batch jobs reside in `background.slice`.

---

## 3. Resource Control Directives

Configure resource limits in the `[Service]` or `[Slice]` section:

```ini
[Service]
# CPU Limits
CPUAccounting=yes
CPUQuota=150%             # Restricts process to 1.5 CPU cores
CPUWeight=100             # Proportional share (1-10000, default 100)

# Memory Limits
MemoryAccounting=yes
MemoryHigh=1.8G           # Soft limit: triggers memory reclaim/throttling when exceeded
MemoryMax=2.0G            # Hard limit: Out-Of-Memory (OOM) killer invoked if exceeded
MemorySwapMax=0           # Completely disables swap for this service

# Process & Thread Limits
TasksMax=250              # Prevents fork-bomb exhaustion of kernel PID space

# Block I/O Limits
IOAccounting=yes
IOWeight=100
IOReadBandwidthMax=/dev/nvme0n1 100M
IOWriteBandwidthMax=/dev/nvme0n1 50M
```

---

## 4. Resource Monitoring Tools

```bash
# Top-like monitoring of systemd cgroups and slices
systemd-cgtop

# Hierarchical tree view of control groups and PIDs
systemd-cgls
```

---

## 5. Authoritative References

- [systemd.resource-control(5) Manual](https://man.archlinux.org/man/systemd.resource-control.5)
- [cgroup v2 Kernel Documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html)
