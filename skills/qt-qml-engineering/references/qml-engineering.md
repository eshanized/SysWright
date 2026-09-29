# QML Language & Module Engineering (Qt 6)

## 1. Scope & Modern QML Architecture

QML is a declarative, JSON-like language for composing fluid, reactive user interfaces in Qt Quick. In Qt 6, QML architecture centers on **QML Modules** defined with CMake, enabling ahead-of-time (AOT) compilation to C++ via `qmlcachegen` and strict compile-time verification with `qmllint`.

---

## 2. Declarative QML Modules via `qt_add_qml_module`

In Qt 6, manual resource files (`.qrc`) and runtime `qmlRegisterType` calls are superseded by declarative CMake QML modules:

```cmake
qt_add_qml_module(MyQtApp
    URI MyCompany.App
    VERSION 1.0
    QML_FILES
        qml/Main.qml
        qml/components/CustomButton.qml
        qml/views/DashboardView.qml
    SOURCES
        src/AppController.h src/AppController.cpp
        src/ItemModel.h src/ItemModel.cpp
)
```

### Benefits:
- Compiles QML to native C++ bytecode ahead-of-time (AOT).
- Provides deterministic module namespaces (`import MyCompany.App 1.0`).
- Embeds resources into the binary without manual XML `.qrc` files.
- Generates `qmldir` and type info files for IDE tooling and `qmllint`.

---

## 3. Property Bindings & Reactive Programming

The core strength of QML is automatic property bindings. A property binding is an expression that automatically re-evaluates whenever any of its dependencies change:

```qml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    width: 600
    height: 400
    color: palette.window

    property int itemCount: 0
    // Reactive binding: automatically updates when itemCount changes
    property bool hasItems: itemCount > 0

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        Label {
            text: root.hasItems ? qsTr("Items: %1").arg(root.itemCount) : qsTr("No items available")
            font.bold: true
        }

        Button {
            text: qsTr("Add Item")
            onClicked: root.itemCount += 1
        }
    }
}
```

### Invariant: Do Not Break Property Bindings
Assigning a value directly to a bound property breaks the binding permanently:
```qml
// ANTI-PATTERN: Breaking the binding
width: parent.width / 2
onClicked: width = 200 // Destroys the reactive binding to parent.width!

// CORRECT: Use conditional ternary binding or Binding object
width: customWidthSet ? 200 : parent.width / 2
```

---

## 4. Layouts vs Anchors

- **`QtQuick.Layouts` (`RowLayout`, `ColumnLayout`, `GridLayout`)**:
  - Use when elements must reflow dynamically, wrap, or distribute available space using `Layout.fillWidth: true` and `Layout.preferredHeight`.
  - Ideal for resizable desktop application windows and dialogs.
- **Anchors (`anchors.fill`, `anchors.centerIn`, `anchors.left`)**:
  - Use for positioning an element relative to its direct parent or sibling within simple visual items.
  - **Invariant**: Never mix anchors with layouts on the same item. Using `anchors.fill: parent` inside a `RowLayout` causes layout engine conflicts.

---

## 5. High-DPI Scaling & Theme Synchronization

- **High-DPI**: Qt 6 enables fractional high-DPI scaling automatically by default. Never hardcode absolute pixel coordinates assuming a standard 96 DPI screen; use relative layouts or font metrics (`fontMetrics.averageCharacterWidth`).
- **Theme Synchronization**: Use `SystemPalette` or access `Application.styleHints.colorScheme` to adapt colors dynamically between dark and light desktop themes.
- **Localization**: Wrap every user-visible string in `qsTr("...")` or `qsTrId("...")` to enable translation via Qt Linguist (`lupdate` / `lrelease`).
