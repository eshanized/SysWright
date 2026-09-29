# Desktop Environment Compatibility (KDE, GNOME, Xfce, COSMIC)

## 1. Scope & Desktop Neutrality

Linux Engineering applications must avoid hardcoding assumptions about specific desktop environments. An application should run seamlessly across **KDE Plasma**, **GNOME**, **Xfce**, **Cinnamon**, **COSMIC**, and **LXQt**.

---

## 2. Desktop Environment Matrix

| Desktop Environment | Primary Toolkit | Display Protocols | Key Design & Integration Characteristics |
|---|---|---|---|
| **KDE Plasma** | Qt 6 / KDE Frameworks | Native Wayland (KWin) & X11 | Supports standard desktop menus, server-side decorations (SSD), system tray (StatusNotifierItem), dark/light theme switching |
| **GNOME** | GTK 4 / Libadwaita | Native Wayland (Mutter) & X11 | Client-side decorations (CSD / HeaderBar), app-indicator extension required for system trays, strictly adheres to GNOME HIG |
| **Xfce** | GTK 3 / GTK 4 | X11 & Wayland (Xfwm4 / Labwc) | Traditional desktop layout, panel plugins, server-side decorations, minimal resource consumption |
| **COSMIC** | Rust / iced | Native Wayland (cosmic-comp) | Rust-based desktop shell, applets, Wayland fractional scaling, modern styling |
| **Cinnamon / MATE** | GTK 3 | X11 & Wayland | Traditional desktop paradigms, panel applets, notification daemons |

---

## 3. Detecting the Desktop Environment

When an application needs to adapt behavior (e.g. tuning UI layout or providing desktop-specific help):
- Inspect the `$XDG_CURRENT_DESKTOP` environment variable:
  - `KDE` for KDE Plasma.
  - `GNOME` for GNOME Shell.
  - `XFCE` for Xfce.
  - `COSMIC` for COSMIC Desktop.
- Format: Semicolon-separated list in case of desktop variants (e.g. `ubuntu:GNOME`).
- **Rule**: Never use proprietary compositor or desktop APIs directly if a standardized Freedesktop specification or XDG Portal interface exists.
