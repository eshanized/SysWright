# X11 & XWayland Compatibility Architecture

## 1. Scope & The Legacy X11 Architecture

The X Window System (X11) has served as the Unix display architecture for decades. Understanding its operational model is critical for maintaining compatibility and diagnosing legacy issues:
- **Client-Server Model**: X11 clients communicate with the X server over Unix domain sockets (`/tmp/.X11-unix/X0`) using the X11 protocol.
- **Global Shared State**: In X11, any client can query the global root window geometry, grab all keyboard input globally (`XGrabKeyboard`), synthesize mouse events into other windows (`XTestFakeKeyEvent`), and capture arbitrary screen pixels (`XGetImage`).
- **Security Implications**: Because X11 lacks inter-client isolation, any unprivileged client can act as a keystroke logger or screen scraper.

---

## 2. XWayland: The Compatibility Bridge

To allow legacy X11 applications to run seamlessly inside a Wayland desktop session, compositors spawn **XWayland**:
- XWayland is an X server implementation where the display hardware is a Wayland surface.
- X11 applications connect to XWayland normally (via `$DISPLAY=:0`).
- XWayland translates X11 drawing requests and window maps into Wayland `wl_surface` buffers and passes them to the parent Wayland compositor.

### Operational Caveats in XWayland:
1. **Fractional Scaling**: XWayland applications may appear slightly blurry when running on high-DPI fractional scaling monitors (e.g. 125% or 150%) unless the compositor supports Wayland fractional scaling protocols.
2. **Global Hotkeys & Snooping**: Global hotkeys registered via raw X11 APIs (`XGrabKey`) only work when an X11 window has focus; they fail when a native Wayland window is active. Use the **Global Shortcuts Portal** instead.
