# Qt Linux Desktop Integration & Wayland

## 1. Scope & The Qt Platform Abstraction (QPA)

Qt abstracts underlying windowing systems via QPA plugins:
- **`wayland` (`qtwayland`)**: Native Wayland protocol integration on modern Linux desktop environments (KDE Plasma, GNOME, Sway, Hyprland).
- **`xcb`**: Native X11 protocol integration for legacy X11 sessions and XWayland.
- Automatic Fallback: Qt automatically negotiates the session type based on `$WAYLAND_DISPLAY` or `$XDG_SESSION_TYPE`.

---

## 2. Desktop Portals & Native Dialogs

On modern Linux desktops (especially in sandboxed environments or under Wayland), applications must use the Freedesktop XDG Desktop Portal for file pickers, notifications, and URI opening:

```cpp
#include <QFileDialog>

// CORRECT: Uses native XDG Desktop Portal automatically
QString fileName = QFileDialog::getOpenFileName(
    parentWidget,
    tr("Open Document"),
    QDir::homePath(),
    tr("Images (*.png *.jpg *.svg)")
);

// ANTI-PATTERN: Disabling native portal dialogs
// QFileDialog::DontUseNativeDialog should NEVER be used in production Linux software
```

---

## 3. System Theme & Dark/Light Mode Synchronization

Modern desktop environments broadcast color scheme changes (dark vs light mode). In Qt 6.5+, query and observe `QStyleHints`:

```cpp
#include <QGuiApplication>
#include <QStyleHints>

void setupThemeListener() {
    QStyleHints *hints = QGuiApplication::styleHints();
    
    // Check initial color scheme
    bool isDark = (hints->colorScheme() == Qt::ColorScheme::Dark);
    applyTheme(isDark);

    // Listen for real-time desktop theme toggle
    QObject::connect(hints, &QStyleHints::colorSchemeChanged, [](Qt::ColorScheme scheme) {
        applyTheme(scheme == Qt::ColorScheme::Dark);
    });
}
```

---

## 4. D-Bus Integration in Qt

Qt provides the `QtDBus` module for IPC on the session bus:
- Generate C++ proxy interfaces from D-Bus introspection XML using `qdbusxml2cpp`.
- Connect directly to desktop service signals:
  ```cpp
  QDBusConnection::sessionBus().connect(
      "org.freedesktop.Notifications",
      "/org/freedesktop/Notifications",
      "org.freedesktop.Notifications",
      "NotificationClosed",
      this,
      SLOT(handleNotificationClosed(uint,uint))
  );
  ```
