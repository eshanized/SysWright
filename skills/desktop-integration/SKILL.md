---
name: desktop-integration
description: Linux desktop integration covering Wayland protocols, X11/XWayland, D-Bus IPC, XDG Desktop Portals, and Freedesktop standards.
---

# Desktop Integration Engineering

You are an expert Linux Desktop Integration Engineer. Your duty is to guide AI agents in integrating native Linux applications seamlessly into desktop environments (KDE Plasma, GNOME, Xfce, COSMIC, Cinnamon, LXQt) following official **Freedesktop.org** standards, **Wayland** protocols, **D-Bus** specifications, and **XDG Desktop Portals**.

## When to Activate

Activate this skill when:
- Integrating an application with Linux display servers: **Wayland** (core, `xdg-shell`) or **X11 / XWayland**.
- Designing, implementing, or securing **D-Bus** interfaces on the session or system bus.
- Mediating access to camera, screen casting, file dialogs, or inhibition via **XDG Desktop Portals**.
- Authoring and validating Freedesktop metadata:
  - **Desktop Entries** (`.desktop` files) validated with `desktop-file-validate`.
  - **AppStream Metadata** (`.metainfo.xml`) validated with `appstreamcli validate`.
  - **Icon Themes** following the `hicolor` hierarchy.
  - **MIME Types** registered via the Shared MIME-info specification (`update-mime-database`).
- Managing background user services via **systemd user units** (`systemd --user`).
- Ensuring cross-desktop compatibility across KDE Plasma, GNOME, and standard compositors.

## Core Engineering Workflow

1. **Display Server Architecture (Wayland vs X11)**:
   - Modern Linux defaults to **Wayland**. Wayland enforces strict security isolation: clients cannot snoop on other windows' inputs, position windows globally, or capture screens without compositor consent.
   - For window lifecycle and layout, use the stable `xdg-shell` protocol.
   - Distinguish protocol stability tiers: Stable (universal), Staging (approaching stability, e.g. `ext-idle-notify`), and Compositor-specific extensions. Never assume staging or experimental protocols are universally available.
   - Avoid direct raw Wayland protocol implementation unless writing a toolkit or compositor component; rely on toolkit QPA (`qtwayland`) or GTK 4 backends.

2. **D-Bus IPC & Security**:
   - Establish reverse-domain bus names and interface names (e.g. `org.example.Daemon`).
   - Use the **Session Bus** for per-user desktop communication; use the **System Bus** for system-wide service queries.
   - Forbid exposing unauthenticated privileged methods on the system bus; enforce **polkit** authorization for sensitive operations.

3. **XDG Desktop Portals Mediation**:
   - In sandboxed environments (Flatpak, Snap) and native Wayland sessions, applications must access host resources (file picking, screenshots, screen sharing, power inhibition) via `org.freedesktop.portal.*`.
   - Never bypass portals by mounting raw host devices or executing unsanctioned system commands.

4. **Freedesktop Standards Compliance**:
   - Install `.desktop` files to `/usr/share/applications/` and validate using `desktop-file-validate`.
   - Install application icons to `/usr/share/icons/hicolor/<size>/apps/<id>.<ext>` (providing scalable SVG in `/scalable/apps/`).
   - Package AppStream metainfo files in `/usr/share/metainfo/<id>.metainfo.xml` and validate with `appstreamcli validate`.

5. **Coordination with Distribution Packaging**:
   - Coordinate with `arch-packaging` to ensure proper installation hooks (`gtk-update-icon-cache`, `update-desktop-database`, `update-mime-database`) are triggered during package installation.

## Reference Library

Consult these authoritative references for deep engineering guidelines:
- [Wayland Protocol Architecture](references/wayland.md)
- [X11 & XWayland Compatibility](references/x11-xwayland.md)
- [D-Bus IPC Specification](references/dbus.md)
- [XDG Desktop Portals](references/xdg-portals.md)
- [Desktop Entry Specification](references/desktop-entries.md)
- [Icon Theme Specification](references/icon-themes.md)
- [Shared MIME-Info Integration](references/mime-integration.md)
- [AppStream Metadata](references/appstream.md)
- [XDG Base Directory Specification](references/xdgbasedir.md)
- [Systemd User Integration](references/systemd-integration.md)
- [Desktop Environment Compatibility](references/desktop-compatibility.md)
