# Qt 6 Architecture & Module Subsystems

## 1. Scope & Qt 6 Foundation

Qt 6 is a modern, modular C++ application framework. Version 6 introduces major architectural improvements over Qt 5:
- Modern C++ baseline (requires C++17 minimum, leverages C++20 where available).
- Modern CMake build system integration with declarative `qt_add_qml_module()`.
- Modern Rendering Hardware Interface (RHI) abstracting Vulkan, OpenGL, and software rasterization.
- Clean separation of core, GUI, networking, IPC, and presentation engines.

---

## 2. Core Qt Subsystems & Module Boundaries

Avoid bloated linking by including only the required Qt modules in your build configuration:

| Module | Primary Responsibility | Common Classes | Target Use Case |
|---|---|---|---|
| **`Core`** | Foundation types, event loop, object model, signals/slots, I/O, timers, JSON | `QObject`, `QString`, `QByteArray`, `QTimer`, `QFile`, `QProcess`, `QThread` | All Qt applications (CLI and GUI) |
| **`Gui`** | Windowing, 2D graphics, fonts, clipboards, RHI abstraction, color management | `QWindow`, `QScreen`, `QPainter`, `QImage`, `QColorSpace`, `QPalette` | Base graphical layer |
| **`Widgets`** | Traditional desktop widget hierarchy and model/view framework | `QApplication`, `QWidget`, `QMainWindow`, `QPushButton`, `QTableView` | Data-dense desktop software |
| **`Qml`** | QML parsing engine, meta-type system, JavaScript runtime | `QQmlEngine`, `QQmlComponent`, `QQmlContext`, `QJSValue` | Declarative UI applications |
| **`Quick`** | Scene graph 2D visual primitives, items, animations, canvas | `QQuickWindow`, `QQuickItem`, `QQuickView`, `QSGNode` | Modern declarative GUIs |
| **`QuickControls2`** | Declarative desktop and mobile UI controls (Buttons, Sliders, Views) | QML controls: `Button`, `TextField`, `ScrollView`, `SplitView` | QML application interfaces |
| **`Network`** | Asynchronous TCP/UDP sockets, HTTP/2 client (`QNetworkAccessManager`), TLS | `QNetworkAccessManager`, `QNetworkReply`, `QTcpSocket`, `QSslSocket` | Network communication |
| **`DBus`** | Native Linux D-Bus IPC binding for session and system buses | `QDBusConnection`, `QDBusInterface`, `QDBusMessage`, `QDBusReply` | Linux desktop integration |
| **`Concurrent`** | High-level multi-threaded concurrency (Map/Reduce/Filter, `run`) | `QtConcurrent::run`, `QFuture`, `QFutureWatcher` | Background compute offload |
| **`Test`** | Unit testing framework and benchmarking | `QTest`, `QSignalSpy`, `QBENCHMARK` | Automated test suites |

---

## 3. CMake Integration in Modern Qt 6

Modern Qt 6 uses target-based CMake:
```cmake
cmake_minimum_required(VERSION 3.20)
project(MyQtApp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 6.5 REQUIRED COMPONENTS Core Gui Quick DBus)

qt_standard_project_setup()

add_executable(MyQtApp src/main.cpp)

target_link_libraries(MyQtApp PRIVATE
    Qt6::Core
    Qt6::Gui
    Qt6::Quick
    Qt6::DBus
)
```

> [!IMPORTANT]
> Always use `qt_standard_project_setup()` in Qt 6.5+. It automatically configures `CMAKE_AUTOMOC`, `CMAKE_AUTORCC`, `CMAKE_AUTOUIC`, and sets up resource prefixes and output directories.

---

## 4. The Meta-Object Compiler (MOC) Invariants

Qt's signals and slots mechanism, dynamic properties, and QML type registration depend on MOC:
1. Every class utilizing signals, slots, or `Q_PROPERTY` must directly or indirectly inherit from `QObject` and declare the `Q_OBJECT` macro as the very first line of its class body.
2. The class header must be included in CMake sources or targets so `AUTOMOC` can generate `moc_<name>.cpp`.
3. Never implement template classes with the `Q_OBJECT` macro; MOC cannot process class templates directly.
