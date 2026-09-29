# Qt Threading & Concurrency Architecture

## 1. The GUI Thread Invariant

In any Qt application, the thread that initializes `QApplication` or `QGuiApplication` and executes `exec()` is the **GUI thread** (or main thread):
> **MANDATORY INVARIANT**: All UI objects (`QWidget`, `QQuickItem`, `QWindow`, `QPainter`) must be created, modified, and deleted **strictly within the GUI thread**. Accessing UI objects from a secondary thread causes immediate data races, undefined behavior, or segmentation faults.

---

## 2. Worker Object Pattern (`moveToThread`)

The recommended pattern for background work in Qt is the **Worker Object** combined with `QThread`:

```cpp
// 1. Define the Worker Object
class NetworkWorker : public QObject {
    Q_OBJECT
public slots:
    void fetchRemoteData(const QUrl &url) {
        // Runs entirely in background worker thread!
        QByteArray result = performBlockingHttpDownload(url);
        emit dataReady(result);
    }
signals:
    void dataReady(const QByteArray &data);
    void progress(int percentage);
};

// 2. Setup in Controller (GUI Thread)
void AppController::startDownload(const QUrl &url) {
    QThread *workerThread = new QThread(this);
    NetworkWorker *worker = new NetworkWorker(); // No parent!
    worker->moveToThread(workerThread);

    // Cross-thread communication: automatically queued by Qt
    connect(this, &AppController::requestFetch, worker, &NetworkWorker::fetchRemoteData);
    connect(worker, &NetworkWorker::dataReady, this, &AppController::handleDataReady);

    // Clean up when thread finishes
    connect(workerThread, &QThread::finished, worker, &QObject::deleteLater);
    connect(workerThread, &QThread::finished, workerThread, &QObject::deleteLater);

    workerThread->start();
    emit requestFetch(url);
}
```

### Why Queued Connections Work:
When connecting signals and slots between objects in different threads, Qt defaults to `Qt::AutoConnection`, which resolves to `Qt::QueuedConnection`. The signal arguments are serialized into an event posted to the target thread's event queue, guaranteeing thread safety without manual mutex locking.

---

## 3. High-Level Concurrency with `QtConcurrent`

For CPU-bound tasks (e.g. data filtering, image processing) that do not require an independent long-running event loop:
```cpp
#include <QtConcurrent/QtConcurrent>
#include <QFutureWatcher>

void AppController::processLargeDataset(const QList<RawData> &dataset) {
    auto *watcher = new QFutureWatcher<ProcessedResult>(this);

    connect(watcher, &QFutureWatcher<ProcessedResult>::finished, this, [this, watcher]() {
        ProcessedResult result = watcher->result();
        updateUi(result);
        watcher->deleteLater();
    });

    // Dispatches to QThreadPool automatically
    QFuture<ProcessedResult> future = QtConcurrent::run([dataset]() {
        return heavyComputation(dataset);
    });

    watcher->setFuture(future);
}
```
