# Qt Testing, Linting & Quality Assurance

## 1. Scope & Tooling Suite

A professional Qt 6 application requires testing across both C++ logic and declarative QML interfaces:
- **`QTest`**: The official C++ testing framework for unit and benchmark tests.
- **`QSignalSpy`**: Introspects and verifies signal emissions, counts, and parameter types.
- **`qmllint`**: Official static analysis tool for QML files.
- **`qmlformat`**: Official code formatter for QML source code.

---

## 2. Unit Testing with `QTest` & `QSignalSpy`

```cpp
#include <QTest>
#include <QSignalSpy>
#include "TaskController.h"

class TestTaskController : public QObject {
    Q_OBJECT

private slots:
    void initTestCase() {
        // Runs once before all tests
    }

    void testStatusSignalEmission() {
        TaskController controller;
        QSignalSpy spy(&controller, &TaskController::statusTextChanged);

        QVERIFY(spy.isValid());
        controller.setStatusText("Running");

        // Verify signal was emitted exactly once
        QCOMPARE(spy.count(), 1);
        QCOMPARE(controller.statusText(), QString("Running"));
    }

    void testModelDataRetrieval() {
        DeviceListModel model;
        model.addDevice("dev-1", "Sensor Alpha");

        QModelIndex idx = model.index(0, 0);
        QVERIFY(idx.isValid());
        QCOMPARE(model.data(idx, DeviceListModel::NameRole).toString(), QString("Sensor Alpha"));
    }
};

QTEST_MAIN(TestTaskController)
#include "TestTaskController.moc"
```

---

## 3. QML Static Analysis (`qmllint`)

Run `qmllint` during CI to catch unbound properties, syntax errors, and missing imports:
```bash
qmllint qml/Main.qml qml/components/*.qml
```
- A clean `qmllint` run guarantees that all property names exist, types match, and modules are correctly located.
- Code style enforcement:
  ```bash
  qmlformat -i qml/**/*.qml
  ```

---

## 4. Headless Testing in CI (`QT_QPA_PLATFORM=offscreen`)

When running automated GUI test suites on headless Linux CI runners without a physical display:
```bash
export QT_QPA_PLATFORM=offscreen
ctest --output-on-failure
```
`offscreen` allows Qt GUI and Qt Quick scene graphs to initialize in memory without an active Wayland compositor or X11 server.
