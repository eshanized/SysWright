# GIO Asynchronous Operations & D-Bus Integration

## 1. Scope & The Non-Blocking Main Loop

The GLib main loop (`GMainContext`) is single-threaded. Invoking blocking operations (e.g. synchronous disk reads `g_file_load_contents()`, network queries, or heavy CPU loops) freezes the GTK UI:
> **MANDATORY INVARIANT**: Every I/O operation exceeding a few milliseconds must use GIO asynchronous APIs (`*_async` / `*_finish`) or dispatch to background worker threads via `GTask`.

---

## 2. Asynchronous Programming with `GTask`

To implement an asynchronous function in GObject:
```c
/* 1. Asynchronous caller entry-point */
void calculate_hash_async(GFile *file, GCancellable *cancellable, GAsyncReadyCallback callback, gpointer user_data) {
    GTask *task = g_task_new(file, cancellable, callback, user_data);
    g_task_set_source_tag(task, calculate_hash_async);

    /* Run the heavy hash computation in a GLib thread-pool worker */
    g_task_run_in_thread(task, calculate_hash_thread_worker);
    g_object_unref(task);
}

/* 2. Worker executed in background thread */
static void calculate_hash_thread_worker(GTask *task, gpointer source_object, gpointer task_data, GCancellable *cancellable) {
    GFile *file = G_FILE(source_object);
    char *hash = compute_sha256(file); // Heavy blocking computation

    if (hash) {
        g_task_return_pointer(task, hash, g_free);
    } else {
        g_task_return_new_error(task, G_IO_ERROR, G_IO_ERROR_FAILED, "Failed to compute hash");
    }
}

/* 3. Finish function called on main thread by user's callback */
char *calculate_hash_finish(GFile *file, GAsyncResult *res, GError **error) {
    g_return_val_if_fail(g_task_is_valid(res, file), NULL);
    return g_task_propagate_pointer(G_TASK(res), error);
}
```

---

## 3. High-Level D-Bus Integration (`GDBusConnection` & `GDBusProxy`)

To communicate with desktop services (e.g. `org.freedesktop.Notifications`) using GIO:
```c
void send_desktop_notification(const char *summary, const char *body) {
    g_autoptr(GError) error = NULL;
    g_autoptr(GDBusProxy) proxy = g_dbus_proxy_new_for_bus_sync(
        G_BUS_TYPE_SESSION,
        G_DBUS_PROXY_FLAGS_NONE,
        NULL,
        "org.freedesktop.Notifications",
        "/org/freedesktop/Notifications",
        "org.freedesktop.Notifications",
        NULL,
        &error
    );

    if (!proxy) {
        g_warning("Could not connect to notification bus: %s", error->message);
        return;
    }

    /* Call the Notify method via D-Bus variant parameters */
    GVariant *params = g_variant_new(
        "(susssasa{sv}i)",
        "MyApp", 0, "dialog-information", summary, body, NULL, NULL, -1
    );

    g_dbus_proxy_call(proxy, "Notify", params, G_DBUS_CALL_FLAGS_NONE, -1, NULL, NULL, NULL);
}
```
