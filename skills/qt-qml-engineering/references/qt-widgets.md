# Qt Widgets Desktop Engineering

## 1. Scope & Framework Selection

While Qt Quick is ideal for modern, fluid, or touch-friendly interfaces, **Qt Widgets** remains the premier choice for traditional, complex desktop workstation applications (such as IDEs, CAD systems, audio workstations, or scientific analysis tools).

### Framework Selection Decision Matrix:
| Architectural Factor | Choose Qt Widgets | Choose Qt Quick (QML) |
|---|---|---|
| **Primary Interaction** | Mouse and keyboard with dense controls | Fluid gestures, touchscreens, dynamic animations |
| **Window Layout Model** | Dockable panels, nested toolbars, MDI | Canvas, fluid reflow layouts, custom overlays |
| **Data Density** | Thousands of visible table cells / tree nodes | Visual cards, lists, media galleries |
| **Native Look & Feel** | Matches desktop platform theme (KDE Breeze, Windows) pixel-for-pixel via `QStyle` | Custom styled controls with custom shaders |
| **Accessibility (AT-SPI)** | Mature, comprehensive out of the box | Fully supported but requires explicit `Accessible` properties |
| **Technology Stack** | 100% standard C++ | Dual C++ engine + declarative QML |

---

## 2. Core Widget Architecture

### 2.1 The `QMainWindow` Standard Layout
A desktop workstation application typically subclasses `QMainWindow`:
```cpp
#include <QMainWindow>
#include <QMenuBar>
#include <QToolBar>
#include <QStatusBar>
#include <QDockWidget>

class EditorMainWindow : public QMainWindow {
    Q_OBJECT
public:
    explicit EditorMainWindow(QWidget *parent = nullptr) : QMainWindow(parent) {
        setupActions();
        setupMenus();
        setupToolBars();
        setupDocks();
        setupCentralWidget();
    }
private:
    void setupActions();
    void setupMenus();
    void setupToolBars();
    void setupDocks();
    void setupCentralWidget();
};
```

### 2.2 Reusable Actions with `QAction`
Never connect menu items or toolbar buttons independently. Centralize application commands into `QAction` objects:
- Set icons from the system theme via `QIcon::fromTheme("document-open")`.
- Assign standard keyboard shortcuts via `QKeySequence::Open`.
- Set status tips and tooltips.
- Add the single `QAction` to both the `QMenu` and the `QToolBar`.

---

## 3. Model/View Architecture in Qt Widgets

Qt Widgets separates data from presentation using the Model/View pattern:
- **Views**: `QTableView`, `QTreeView`, `QListView`.
- **Models**: Subclasses of `QAbstractItemModel` or `QAbstractTableModel`.
- **Delegates**: `QStyledItemDelegate` for custom cell rendering and editor widgets.

### Delegate Rule:
Never embed heavy full `QWidget` instances in thousands of table cells using `setIndexWidget()`. It exhausts X11/Wayland window IDs and consumes gigabytes of RAM. Implement a lightweight `QStyledItemDelegate` that paints cells using `QPainter` inside the `paint()` method.
