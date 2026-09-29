# GLib & GObject Engineering Principles

## 1. Scope & The GObject Object Model

GObject provides object-oriented programming in pure C, featuring single inheritance, interface implementation, dynamic type registration (`GType`), signals, and properties. It powers the entire GTK, GIO, and GStreamer ecosystems.

---

## 2. Memory Management & Reference Counting

GObject uses reference counting for memory management:
- `g_object_ref(obj)`: Increments reference count.
- `g_object_unref(obj)`: Decrements reference count; when it reaches 0, the object is finalized and its memory freed.

### 2.1 Floating References & `GInitiallyUnowned`
Widgets in GTK inherit from `GInitiallyUnowned` rather than `GObject` directly:
- When a new widget is instantiated (`GtkWidget *btn = gtk_button_new()`), it starts with a **floating reference** (ref count = 1, marked floating).
- When you add the widget to a parent container (`gtk_box_append(box, btn)`), the container calls `g_object_ref_sink(btn)`:
  - This **sinks** the floating reference, converting it into a normal owning reference held by the container.
  - The caller does NOT need to call `g_object_unref(btn)`.
- If you create a widget but NEVER add it to any parent container, you MUST call `g_object_unref(btn)` to prevent a memory leak.

### 2.2 Modern C Memory Safety: `g_autoptr`
In modern C (GCC/Clang), use GLib's automatic cleanup macros to eliminate manual `unref` on exit paths:
```c
void load_user_profile(const char *path) {
    g_autoptr(GFile) file = g_file_new_for_path(path);
    g_autoptr(GError) error = NULL;
    g_autofree char *contents = NULL;
    gsize length = 0;

    if (!g_file_load_contents(file, NULL, &contents, &length, NULL, &error)) {
        g_warning("Failed to load file: %s", error->message);
        return; /* file, error, and contents automatically freed here! */
    }

    process_data(contents, length);
    /* Cleanly cleaned up on normal return */
}
```

---

## 3. Signals & Memory Cycles

When connecting signals via `g_signal_connect()`:
- **Reference Cycles**: If Object A connects to a signal on Object B, passing Object A as `user_data`, and Object B holds a strong reference to Object A, a circular reference cycle prevents both objects from ever being destroyed.
- **Remediation**: Use `g_signal_connect_object(emitter, "signal", handler, observer, G_CONNECT_DEFAULT)`. This automatically disconnects the signal handler as soon as the `observer` object is destroyed.
