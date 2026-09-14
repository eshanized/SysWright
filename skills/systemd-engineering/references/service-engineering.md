# systemd Service Engineering Reference

## 1. Scope

This document details service unit configuration, startup types (`Type=notify`, `exec`, `simple`), execution lifecycles, notification protocols, and environment management.

---

## 2. Service Startup Types (`Type=`)

| Type | Startup Completion Criteria | Recommended Use Case |
|:---|:---|:---|
| **`notify`** | Process sends `READY=1` signal via UNIX socket (`sd_notify(0, "READY=1")`). | **Production standard for modern daemons.** Zero startup race conditions. |
| **`exec`** | systemd forks and completes `execve()` of the main process binary. | Simple binaries without internal backgrounding. |
| **`simple`** | systemd forks the process. Considers unit active immediately upon `fork()`. | Default type; potential race condition for dependent units if binary takes time to bind ports. |
| **`forking`** | Process calls `fork()` to become a daemon and parent exits. Requires `PIDFile=`. | Legacy daemons that cannot run in the foreground. |
| **`oneshot`** | Process runs to completion and exits with code 0 before dependent units proceed. | Setup scripts, migrations, batch jobs (`RemainAfterExit=yes`). |
| **`dbus`** | Process claims a designated name on the D-Bus system bus (`BusName=`). | D-Bus system services. |

---

## 3. Production Service Architecture

```ini
[Unit]
Description=High-Performance API Daemon
Documentation=https://example.org/docs
After=network-online.target
Wants=network-online.target

[Service]
Type=notify
ExecStart=/usr/bin/apid --config /etc/apid/apid.conf
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
RestartSec=5s
TimeoutStartSec=30s

# Sandboxing and Security
NoNewPrivileges=yes
DynamicUser=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
PrivateDevices=yes
CapabilityBoundingSet=
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6

# Managed Paths
ConfigurationDirectory=apid
RuntimeDirectory=apid
StateDirectory=apid

[Install]
WantedBy=multi-user.target
```

---

## 4. The Notification Protocol (`sd_notify`)

For `Type=notify` services, the binary communicates with systemd over the socket defined in `$NOTIFY_SOCKET`:

```c
#include <systemd/sd-daemon.h>

int main(void) {
    // 1. Initialize configuration and bind sockets
    initialize_application();

    // 2. Notify systemd that startup is complete
    sd_notify(0, "READY=1\nSTATUS=Listening for connections on port 8080");

    // 3. Main event loop
    run_event_loop();

    // 4. Notify systemd before shutdown
    sd_notify(0, "STOPPING=1");
    return 0;
}
```

---

## 5. Directory Management Directives

Avoid hardcoding `/run/mydaemon` or `/var/lib/mydaemon` creation in shell scripts. systemd provides declarative directory provisioning:
- **`RuntimeDirectory=mydaemon`**: Creates `/run/mydaemon` owned by the service user; deleted on service stop.
- **`StateDirectory=mydaemon`**: Creates persistent `/var/lib/mydaemon` owned by the service user.
- **`ConfigurationDirectory=mydaemon`**: Exposes `/etc/mydaemon` to the service.
- **`LogsDirectory=mydaemon`**: Creates `/var/log/mydaemon`.

---

## 6. Authoritative References

- [systemd.service(5) Manual](https://man.archlinux.org/man/systemd.service.5)
- [systemd.exec(5) Manual](https://man.archlinux.org/man/systemd.exec.5)
- [sd_notify(3) Manual](https://man.archlinux.org/man/sd_notify.3)
