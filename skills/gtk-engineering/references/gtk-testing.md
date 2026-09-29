# GTK 4 Testing & Inspector Quality Engineering

## 1. Scope & Quality Tooling

GTK 4 applications can be tested and debugged using built-in developer tools and standard GLib test harnesses:
- **GTK Inspector**: Interactive runtime inspection of widget trees, CSS styles, properties, and accessibility trees.
- **`GTest`**: The GLib unit testing harness integrated into Meson and CMake.
- **Headless Testing (`xvfb-run`)**: Running integration tests in headless CI environments.

---

## 2. Interactive Inspection: The GTK Inspector

To enable the GTK Inspector during development:
```bash
# Enable the key shortcut
gsettings set org.gtk.gtk4.Settings.Debug enable-inspector-keybinding true

# Launch application and press Ctrl+Shift+I (or Ctrl+Shift+D)
GTK_DEBUG=interactive ./my_app
```
### Inspector Capabilities:
- Inspect widget hierarchy, layout constraints, margins, and CSS class names in real time.
- Inspect the live **Accessibility Tree** (AT-SPI roles, labels, and focus status).
- Edit CSS properties live without recompiling the binary.

---

## 3. Automated Unit Testing with `GTest`

```c
#include <glib.h>
#include <gtk/gtk.h>

static void test_widget_creation(void) {
    GtkWidget *btn = gtk_button_new_with_label("Submit");
    g_assert_nonnull(btn);
    g_assert_cmpstr(gtk_button_get_label(GTK_BUTTON(btn)), ==, "Submit");
    g_assert_true(gtk_widget_get_visible(btn)); // GTK 4: visible by default!
}

int main(int argc, char *argv[]) {
    gtk_init(); // Initialize GTK
    g_test_init(&argc, &argv, NULL);

    g_test_add_func("/ui/button/creation", test_widget_creation);

    return g_test_run();
}
```

---

## 4. Headless CI Integration (`xvfb-run`)

When running automated test suites that require a display server on headless Linux build servers:
```bash
xvfb-run -a meson test -C build --verbose
```
`xvfb-run` initializes a virtual X11 display buffer in memory, allowing GTK applications to start and pass UI unit tests without a physical monitor.
