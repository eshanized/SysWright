# Libadwaita Engineering & Platform Conventions

## 1. Scope & The Role of Libadwaita

`libadwaita` is an official GNOME library built on top of GTK 4. It implements the GNOME Human Interface Guidelines (HIG) and provides adaptive patterns for modern Linux applications:
- **Adaptive Widgets**: Reflow UI across mobile (touch/narrow width) and wide desktop monitors.
- **Consistent GNOME Styling**: Clean, modern stylesheets with native dark/light mode switching.
- **Standard HIG Patterns**: Header bars, preferences windows, split-view navigation, and status pages.

---

## 2. When to Use (and When NOT to Use) Libadwaita

| Consideration | Use Libadwaita (`libadwaita-1`) | Use Standard GTK 4 (`gtk4`) |
|---|---|---|
| **Target Platform** | GNOME, Phosh, GNOME OS, Flatpak apps | Cross-desktop (KDE Plasma, Xfce, COSMIC, Cinnamon) |
| **Design Language** | Strictly adheres to GNOME HIG | Standard platform-neutral desktop controls |
| **Adaptivity** | Requires dynamic mobile-to-desktop reflow | Standard resizable desktop windows |
| **Theming** | Uses modern Adwaita theme, ignores custom desktop CSS themes | Respects system GTK themes configured by desktop environments |

> [!IMPORTANT]
> Never force `libadwaita` onto a utility that is meant to integrate natively across multiple desktop environments without GNOME styling. Use `libadwaita` deliberately when adopting GNOME platform conventions.

---

## 3. Core Libadwaita Components

### 3.1 `AdwApplication` & `AdwApplicationWindow`
When building an Adwaita application, subclass `AdwApplication` instead of `GtkApplication`. It automatically initializes the Adwaita styling engine:
```c
#include <adwaita.h>

int main(int argc, char *argv[]) {
    g_autoptr(AdwApplication) app = adw_application_new(
        "org.example.App",
        G_APPLICATION_DEFAULT_FLAGS
    );
    g_signal_connect(app, "activate", G_CALLBACK(on_activate), NULL);
    return g_application_run(G_APPLICATION(app), argc, argv);
}
```

### 3.2 Adaptive Layouts with `AdwBreakpoint`
Allows UI elements to morph dynamically when window width changes:
```xml
<object class="AdwBreakpoint">
  <condition>max-width: 500sp</condition>
  <setter target="split_view" property="collapsed">true</setter>
</object>
```
When window width drops below 500 pixels (e.g. snapping to a tile or on a mobile screen), the sidebar automatically collapses into an overlay drawer.
