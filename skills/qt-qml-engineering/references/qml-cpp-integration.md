# QML and C++ Integration Architecture (Qt 6)

## 1. Scope & The Separation of Concerns

The most critical architectural decision in a Qt Quick application is the boundary between C++ and QML:
- **C++ Responsibility**: Data persistence, network communication, hardware interfacing, cryptography, business logic rules, threading, and data models (`QAbstractItemModel`).
- **QML Responsibility**: Visual presentation, transitions, input event dispatch, layouts, and animations.
- **Forbid Business Logic in QML**: Never write database queries, file parsers, or complex algorithms in QML JavaScript. QML JavaScript is intended solely for UI state composition.

---

## 2. Modern Qt 6 Type Registration

In Qt 6, runtime registration calls like `qmlRegisterType<T>()` in `main.cpp` are deprecated in favor of declarative header macros:

### 2.1 The `QML_ELEMENT` Macro
To expose an instantiable C++ class to QML:
```cpp
// src/TaskController.h
#pragma once
#include <QObject>
#include <QtQml/qqmlregistration.h>

class TaskController : public QObject {
    Q_OBJECT
    QML_ELEMENT // Automatically registers TaskController in the target's QML module

    Q_PROPERTY(QString statusText READ statusText WRITE setStatusText NOTIFY statusTextChanged)
    Q_PROPERTY(bool isProcessing READ isProcessing NOTIFY isProcessingChanged)

public:
    explicit TaskController(QObject *parent = nullptr);

    QString statusText() const { return m_statusText; }
    void setStatusText(const QString &text);

    bool isProcessing() const { return m_isProcessing; }

    Q_INVOKABLE void startTask(const QString &inputPath);

signals:
    void statusTextChanged();
    void isProcessingChanged();
    void taskFinished(bool success, const QString &errorMessage);

private:
    QString m_statusText;
    bool m_isProcessing{false};
};
```

### 2.2 The `QML_SINGLETON` Macro
For application-wide shared state or controllers (replacing legacy `rootContext()->setContextProperty()`):
```cpp
class AppSettings : public QObject {
    Q_OBJECT
    QML_ELEMENT
    QML_SINGLETON
    // ...
};
```
In QML:
```qml
import MyCompany.App 1.0

Item {
    Component.onCompleted: {
        AppSettings.saveOnExit = true; // Direct singleton access with full compile-time validation
    }
}
```

> [!WARNING]
> Avoid `setContextProperty()`. Context properties inject untyped globals into the QML engine, disabling `qmllint` type verification, hindering AOT compilation, and causing maintenance headaches in large codebases. Use `QML_ELEMENT` or `QML_SINGLETON`.

---

## 3. High-Performance Models with `QAbstractListModel`

When displaying lists of data in QML (`ListView`, `GridView`, `Repeater`), never pass raw `QList<QString>` or JavaScript arrays for dynamic or large datasets. Subclass `QAbstractListModel`:

```cpp
class DeviceListModel : public QAbstractListModel {
    Q_OBJECT
    QML_ELEMENT

public:
    enum DeviceRoles {
        IdRole = Qt::UserRole + 1,
        NameRole,
        StatusRole
    };

    explicit DeviceListModel(QObject *parent = nullptr);

    int rowCount(const QModelIndex &parent = QModelIndex()) const override;
    QVariant data(const QModelIndex &index, int role = Qt::DisplayRole) const override;
    QHash<int, QByteArray> roleNames() const override;

    void addDevice(const QString &id, const QString &name);
    void removeDevice(int index);
};
```

### Benefits of `QAbstractListModel`:
- **Fine-Grained UI Updates**: Calling `beginInsertRows()` / `endInsertRows()` updates only the affected row in the QML view, enabling smooth add/remove animations without rebuilding the entire list.
- **Minimal Memory Overhead**: Views virtualize delegates, instantiating only items currently visible on screen.
