---
name: systemd-engineering
description: Specialist skill for systemd system and service management, unit architecture, sandboxing, cgroups v2 resource control, and diagnostic troubleshooting. Covers service types (simple, exec, notify with sd_notify), socket activation, timers, dependency vs ordering directives (Wants, Requires, BindsTo, Before, After), security hardening (DynamicUser, ProtectSystem=strict, capability dropping, SystemCallFilter), and non-destructive validation via systemd-analyze verify. Use when authoring unit files, hardening daemons, fixing startup timeouts, or investigating failed units.
license: Apache-2.0
compatibility: Requires Linux environment with systemd userspace tooling (systemd-analyze, systemctl).
metadata:
  author: Eshan Roy
  version: "0.1.0"
  claude_context: "fork"
  claude_agent: "general"
---

# systemd Systems & Service Engineering

The `systemd-engineering` skill provides specialist capabilities for designing, configuring, hardening, and troubleshooting Linux systemd services, targets, sockets, timers, and resource management slices.

---

## 1. Operating Principles & Invariants

1. **Dependency Does Not Imply Ordering**: Always pair `Wants=` or `Requires=` with explicit `Before=` or `After=` ordering directives to prevent parallel startup race conditions.
2. **Never Blindly Apply Sandboxing**: Hardening directives (`ProtectSystem=strict`, `DynamicUser=yes`) restrict filesystem and capability access. Always pair sandboxing with managed directories (`StateDirectory=`, `RuntimeDirectory=`) and verify required syscalls before deploying.
3. **Validate Statically Before Reloading**: Always validate unit syntax with `systemd-analyze verify /path/to/unit` before requesting system activation.
4. **Safety Tier Gating**: Enabling, disabling, restarting, or masking host system services (`systemctl restart`, `systemctl enable`) are Tier 3 operations requiring explicit human authorization. Never silently disable system services.

---

## 2. Intent Classification & Workflow Routing

```mermaid
flowchart TD
    REQ["systemd Engineering Request"] --> CLASS{"Classify Task"}

    CLASS -->|Unit Creation / Refactoring| DSN["1. Service Engineering\n(Type=notify, ExecStart, StateDirectory, dependencies)"]
    CLASS -->|Security Hardening| SEC["2. Sandboxing Audit\n(systemd-analyze security, DynamicUser, syscall filters)"]
    CLASS -->|Resource Management| RES["3. Resource Control\n(cgroups v2, CPUQuota, MemoryMax, TasksMax, slices)"]
    CLASS -->|Failure / Timeout Diagnosis| DIAG["4. Troubleshooting\n(journalctl -u, systemd-analyze verify, ordering cycles)"]

    DSN --> EXEC["Execute systemd Workflow"]
    SEC --> EXEC
    RES --> EXEC
    DIAG --> EXEC
```

---

## 3. The 5-Step Service Hardening Workflow

1. **Baseline Assessment**: Run `systemd-analyze security <unit>` to obtain current exposure score.
2. **Privilege Dropping**: Enforce `NoNewPrivileges=yes` and `DynamicUser=yes` (or specify unprivileged `User=` and `Group=`).
3. **Filesystem Lockdown**: Apply `ProtectSystem=strict`, `ProtectHome=yes`, `PrivateTmp=yes`, and `PrivateDevices=yes`. Declare writable directories via `StateDirectory=` and `RuntimeDirectory=`.
4. **Kernel & Syscall Restriction**: Set `ProtectKernelTunables=yes`, `ProtectControlGroups=yes`, and whitelist syscalls with `SystemCallFilter=@system-service`.
5. **Static Verification**: Execute `systemd-analyze verify` and check that the security exposure score drops below `2.5`.

---

## 4. Cross-Specialist Coordination

| Task | Coordinating Specialists | Interaction |
|:---|:---|:---|
| Packaged service unit file | `systemd-engineering` + `arch-packaging` | `systemd-engineering` authors unit; `arch-packaging` places it in `/usr/lib/systemd/system/`. |
| Network-dependent daemon | `systemd-engineering` + `linux-networking` | `linux-networking` verifies interfaces; `systemd-engineering` orders `After=network-online.target`. |
| Mount or encrypted swap unit | `systemd-engineering` + `linux-storage` | `linux-storage` defines UUIDs/options; `systemd-engineering` configures `.mount` or `.swap`. |

---

## 5. Authoritative References Directory

- [Unit Architecture & Dependency Model](references/unit-architecture.md)
- [Service Engineering & Notification Protocol](references/service-engineering.md)
- [Sandboxing & Security Scoring](references/sandboxing.md)
- [Resource Control & cgroups v2](references/resource-control.md)
- [Diagnostics & Troubleshooting](references/troubleshooting.md)
- [Safety Policy](../../references/safety-policy.md)
