# GtkApplication & Application Lifecycle Architecture

## 1. Scope & The Application Singleton

In GTK 4, all desktop applications should center around `GtkApplication`. It integrates directly with the desktop session, enforces single-instance semantics, manages application window tracking, and dispatches actions.

---

## 2. Startup vs Activate Lifecycle

A common bug in GTK applications is confusing the `startup` and `activate` signal handlers:

| Signal | Execution Context | Proper Usage |
|---|---|---|
| **`startup`** | Emitted **once** when the primary instance initializes its core subsystems | Initialize global resources, register `GAction` entries, setup custom CSS providers, load GResources |
| **`activate`** | Emitted every time the application is launched (including secondary CLI invocations) | Create and present the main `GtkApplicationWindow` (`gtk_window_present()`). If the window already exists, bring it to the foreground! |

```c
static void on_app_startup(GApplication *app, gpointer user_data) {
    /* 1. Register application actions */
    const GActionEntry entries[] = {
        { "quit", on_action_quit, NULL, NULL, NULL },
        { "about", on_action_about, NULL, NULL, NULL },
    };
    g_action_map_add_action_entries(G_ACTION_MAP(app), entries, G_N_ELEMENTS(entries), app);

    /* 2. Bind keyboard accelerators */
    const char *quit_accels[] = { "<Primary>q", NULL };
    gtk_application_set_accels_for_action(GTK_APPLICATION(app), "app.quit", quit_accels);
}

static void on_app_activate(GApplication *app, gpointer user_data) {
    /* Present existing window if already open (single-instance handling) */
    GList *windows = gtk_application_get_windows(GTK_APPLICATION(app));
    if (windows != NULL) {
        gtk_window_present(GTK_WINDOW(windows->data));
        return;
    }

    /* Otherwise, construct and display new application window */
    GtkWidget *win = my_app_window_new(GTK_APPLICATION(app));
    gtk_window_present(GTK_WINDOW(win));
}
```

---

## 3. Application IDs & Reverse-Domain Naming

`GtkApplication` requires an `application-id` adhering to D-Bus bus name syntax:
- Format: `org.company.AppName` (all lowercase elements recommended, e.g. `org.gnome.TextEditor`, `com.example.systemmonitor`).
- It binds the application to:
  - Its D-Bus service name (`org.example.App`).
  - Its desktop file path (`/usr/share/applications/org.example.App.desktop`).
  - Its GSettings schema (`/org/example/App/`).
  - Its AppStream metadata ID (`org.example.App.metainfo.xml`).
