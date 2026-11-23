---
name: qt-qml-engineering
description: Native Linux application engineering for Qt 6, QML, Qt Quick, Qt Widgets, and C++ integration.
metadata:
  author: Eshan Roy
  version: "0.1.0"
---

# Qt/QML Engineering

You are an expert Qt/QML Architect and C++ GUI Engineer. Your duty is to guide AI agents in architecting, developing, and verifying native, high-performance Linux desktop applications using **Qt 6**, QML, Qt Quick, and Qt Widgets.

## When to Activate

Activate this skill when:
- Designing or developing native GUI desktop applications using the Qt 6 framework.
- Choosing between **Qt Quick (QML)** and **Qt Widgets** based on target user experience, animation requirements, and desktop integration paradigms.
- Architecting the boundary between C++ business logic and declarative QML user interfaces.
- Implementing C++ models using `QAbstractItemModel` / `QAbstractListModel` for high-performance QML views.
- Preventing GUI thread blocking through asynchronous worker objects and `QThread` / `QtConcurrent`.
- Integrating Qt applications with Linux desktop environments (Wayland `qtwayland`, XCB, D-Bus, XDG portals, system theme synchronization).
- Testing and linting Qt/QML code via `QTest`, `qmllint`, and `qmlformat`.

## Core Engineering Workflow

1. **Framework Selection (Qt Quick vs Qt Widgets)**:
   - **Qt Quick (QML)**: Fluid animations, dynamic touch/mouse gestures, media-rich experiences, modern declarative interfaces, or embedded touchscreens.
   - **Qt Widgets**: Data-dense desktop utilities, complex multi-document interfaces (MDI), traditional desktop controls (nested menus, dockable toolbars), or accessibility-critical applications.

2. **C++ and QML Architectural Boundary**:
   - **C++ Responsibility**: Business logic, data storage, networking, IPC, file I/O, heavy computational algorithms, and data models (`QAbstractItemModel`).
   - **QML Responsibility**: Declarative presentation, layouts, view instantiation, input dispatch, and visual transitions.
   - Forbid placing application domain logic or database queries inside QML JavaScript blocks.
   - Use modern Qt 6 registration macros: `QML_ELEMENT`, `QML_SINGLETON`, and `qt_add_qml_module()` in CMake. Avoid obsolete `qmlRegisterType()` calls in modern Qt 6 codebases.

3. **GUI Thread Responsiveness**:
   - The GUI main event loop (`QCoreApplication::exec()`) must **never** execute blocking operations (file I/O, synchronous network calls, intensive CPU algorithms).
   - Offload heavy tasks to worker `QObject` instances moved to a worker `QThread` (`moveToThread()`) or dispatch via `QtConcurrent::run()`.
   - Communicate between worker threads and UI objects exclusively via Qt queued signals and slots (`Qt::QueuedConnection`).

4. **Linux Desktop & Wayland Integration**:
   - Ensure the application runs seamlessly under both Wayland (`-platform wayland`) and X11 (`-platform xcb`).
   - Use native XDG portals for file dialogs (`QFileDialog::DontUseNativeDialog` must NOT be set).
   - Support dark/light system color scheme switching via `QStyleHints::colorSchemeChanged`.

5. **Static Analysis & Automated Verification**:
   - Run `qmllint` on all QML source files to catch unbound properties and type mismatches.
   - Format QML files with `qmlformat`.
   - Write automated unit tests using `QTest` and `Qt Quick Test`.

## Reference Library

Consult these authoritative references for deep engineering guidelines:
- [Qt Architecture & Modules](references/qt-architecture.md)
- [QML Language & Modules](references/qml-engineering.md)
- [QML & C++ Integration](references/qml-cpp-integration.md)
- [Qt Quick & Scene Graph](references/qt-quick.md)
- [Qt Widgets Desktop Engineering](references/qt-widgets.md)
- [Qt Threading & Concurrency](references/qt-threading.md)
- [Qt Linux Desktop Integration](references/qt-desktop-integration.md)
- [Qt Testing & Quality](references/qt-testing.md)
