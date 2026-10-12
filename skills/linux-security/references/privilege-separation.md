# Privilege Separation and Sandboxing with systemd

Architectural reference for sandboxing system daemons and isolating privileges using systemd execution directives.

---

## 1. The Principle of Privilege Separation

Decompose complex applications into distinct processes separated by trust boundaries:
- **Small Privileged Helper**: Runs briefly at startup to bind privileged port 443 or open raw log file, then drops privileges or hands file descriptor to worker.
- **Unprivileged Worker**: Runs under dedicated unprivileged user (`User=appuser`), confined by systemd sandbox directives and seccomp filters.

---

## 2. Hardened systemd Service Unit Template

```ini
[Unit]
Description=Hardened Example Service
After=network.target

[Service]
Type=notify
ExecStart=/usr/bin/my_daemon
User=myuser
Group=myuser

# -------------------------------------------------------------
# 1. Process & Privilege Bounding
# -------------------------------------------------------------
NoNewPrivileges=yes
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_BIND_SERVICE

# -------------------------------------------------------------
# 2. Filesystem Confinement
# -------------------------------------------------------------
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
PrivateDevices=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectKernelLogs=yes
ProtectControlGroups=yes
ReadWritePaths=/var/lib/my_daemon /var/log/my_daemon

# -------------------------------------------------------------
# 3. Kernel & Memory Protection
# -------------------------------------------------------------
MemoryDenyWriteExecute=yes
RestrictRealtime=yes
RestrictSUIDSGID=yes
LockPersonality=yes

# -------------------------------------------------------------
# 4. Syscall Filtering (Seccomp)
# -------------------------------------------------------------
SystemCallFilter=@system-service
SystemCallFilter=~@privileged @resources @obsolete
SystemCallArchitectures=native

# -------------------------------------------------------------
# 5. Network & IPC Confinement
# -------------------------------------------------------------
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX
RestrictNamespaces=yes
```

---

## 3. Auditing Services with `systemd-analyze security`

`systemd-analyze security` calculates an empirical exposure score (from 0.0 = completely hardened to 10.0 = dangerously exposed):

```bash
systemd-analyze security my_service.service
```

```text
  NAME                             DESCRIPTION                                                EXPOSURE
✗ RootDirectory=/RootImage=        Service runs within the host's root directory                   0.1
✗ User=/DynamicUser=               Service runs as root user                                       0.4
✗ CapabilityBoundingSet=~CAP_SET*  Service may change UID/GID                                      0.2
✗ DeviceAllow=                     Service has no device whitelist                                 0.2
✓ NoNewPrivileges=                 Service cannot acquire new privileges                           
✓ ProtectSystem=                   Service has read-only system mounts                             
✓ SystemCallFilter=                Service has restricted system calls                             

→ Overall exposure level for my_service.service: 2.1 OK
```

*Goal*: All production systemd services should achieve an exposure score $< 2.5$.
