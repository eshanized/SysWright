# Systemd User Integration & Desktop Services

## 1. Scope & The User Manager Session

On modern Linux systems, desktop sessions and user background services are managed by a dedicated instance of systemd: **`systemd --user`**:
- Executes as the unprivileged user (UID $>1000$).
- Started automatically during user login via PAM (`pam_systemd`).
- Manages user background services, syncthing daemons, notification bridges, and media daemons.

---

## 2. Systemd User Units vs D-Bus Activation

Historically, background services were launched via D-Bus activation files (`/usr/share/dbus-1/services/`). In modern systems, D-Bus activation is handed over to systemd user services:

### 2.1 The D-Bus Service File (`com.example.Daemon.service`)
Installed to `/usr/share/dbus-1/services/com.example.Daemon.service`:
```ini
[D-BUS Service]
Name=com.example.Daemon
Exec=/usr/bin/mydaemon
SystemdService=mydaemon.service
```

### 2.2 The Systemd User Unit (`mydaemon.service`)
Installed to `/usr/lib/systemd/user/mydaemon.service`:
```ini
[Unit]
Description=My Application Background Sync Daemon
Documentation=man:mydaemon(1)
PartOf=graphical-session.target

[Service]
Type=notify
ExecStart=/usr/bin/mydaemon
Restart=on-failure
RestartSec=5s

# Sandboxing in user session
ProtectSystem=strict
ProtectHome=read-only
PrivateTmp=yes

[Install]
WantedBy=graphical-session.target
```

### Key Advantage:
When a client application invokes a D-Bus method on `com.example.Daemon`, D-Bus asks systemd to start `mydaemon.service`. Systemd spawns the daemon inside its own dedicated cgroup with resource limits, logging to journald, and automatic crash restarts.
