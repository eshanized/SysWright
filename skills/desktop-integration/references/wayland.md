# Wayland Protocol Architecture & Ecosystem

## 1. Scope & The Wayland Architecture

Wayland is the modern display server protocol for Linux, replacing the legacy X11 architecture. In Wayland:
- The **Compositor is the Display Server**: The compositor (e.g. KWin in KDE, Mutter in GNOME, wlroots in Sway/Hyprland) directly receives input from the kernel (`libinput`) and composites client buffers onto screen outputs via KMS/DRM.
- **Every Frame is Perfect**: Double-buffering and presentation timing eliminate visual tearing.
- **Isolation by Default**: Clients have no global coordinate knowledge, cannot position windows arbitrarily, cannot snoop on global keystrokes, and cannot capture screen buffers without compositor consent.

---

## 2. Protocol Stability Tiers (`wayland-protocols`)

Wayland protocol specifications are partitioned into strict stability tiers:

| Tier | Namespace / Prefix | Guarantees | Example Protocols |
|---|---|---|---|
| **Core Protocol** | `wl_*` | Immutable, backward-compatible forever | `wl_compositor`, `wl_surface`, `wl_seat`, `wl_output`, `wl_shm` |
| **Stable Protocols** | `xdg_*` | Finalized, standardized across all modern compositors | `xdg-shell` (desktop window management: `xdg_toplevel`, `xdg_popup`) |
| **Staging Protocols** | `ext_*` or `xdg_*` | Feature-complete, ready for widespread deployment; backward compatibility expected | `ext-idle-notify-v1`, `ext-session-lock-v1`, `xdg-activation-v1` |
| **Unstable Protocols** | `zwp_*` or `zext_*` | Experimental; subject to breaking changes across versions | `zwp_linux_dmabuf_v1`, `zwp_text_input_v3` |
| **Compositor-Specific** | `wlr_*`, `kde_*`, `gnome_*` | Proprietary to specific compositors (wlroots, KWin, Mutter) | `wlr-layer-shell-unstable-v1` |

> [!WARNING]
> Never assume that an unstable (`zwp_`) or compositor-specific (`wlr_`) protocol is universally available. Standard desktop applications should rely on stable protocols (`xdg-shell`) or utilize XDG Portals for features requiring compositor cooperation (such as screen recording or global shortcuts).

---

## 3. The `xdg-shell` Protocol

For standard desktop applications, window management is governed by `xdg-shell`:
- **`xdg_wm_base`**: Global interface for creating shell surfaces.
- **`xdg_toplevel`**: Top-level application window. Supports states: `maximized`, `fullscreen`, `resizing`, `activated`. Window positioning is strictly determined by the compositor.
- **`xdg_popup`**: Menus, tooltips, and context dropdowns tied to a parent surface via `xdg_positioner`.
- **Buffer Flow**:
  1. Client renders to a shared memory buffer (`wl_shm`) or GPU DMA-BUF (`linux-dmabuf`).
  2. Client attaches the buffer to `wl_surface`.
  3. Client informs the compositor of damaged regions (`wl_surface.damage_buffer`).
  4. Client commits the surface state (`wl_surface.commit`).
