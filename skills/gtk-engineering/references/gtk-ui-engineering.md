# GTK 4 UI Engineering, Layouts & Templates

## 1. Scope & Declarative UI Composition

Modern GTK 4 applications compose user interfaces using declarative XML definitions compiled into binary resources with `glib-compile-resources` (`GResource`). Building complex widget hierarchies imperatively in C code is an anti-pattern.

---

## 2. Composite Widget Templates

Composite widget templates allow a custom `GtkWidget` subclass in C or Rust to bind directly to an XML template:

```xml
<!-- resources/my-window.ui -->
<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <template class="MyWindow" parent="GtkApplicationWindow">
    <property name="title" translatable="yes">My GTK 4 Application</property>
    <property name="default-width">800</property>
    <property name="default-height">600</property>
    <child type="titlebar">
      <object class="GtkHeaderBar" id="header_bar">
        <child type="end">
          <object class="GtkButton" id="btn_refresh">
            <property name="icon-name">view-refresh-symbolic</property>
            <property name="action-name">win.refresh</property>
          </object>
        </child>
      </object>
    </child>
  </template>
</interface>
```

In the C implementation:
```c
G_DEFINE_TYPE(MyWindow, my_window, GTK_TYPE_APPLICATION_WINDOW)

static void my_window_class_init(MyWindowClass *klass) {
    GtkWidgetClass *widget_class = GTK_WIDGET_CLASS(klass);

    gtk_widget_class_set_template_from_resource(widget_class, "/com/example/app/my-window.ui");
    gtk_widget_class_bind_template_child(widget_class, MyWindow, header_bar);
    gtk_widget_class_bind_template_child(widget_class, MyWindow, btn_refresh);
}

static void my_window_init(MyWindow *self) {
    gtk_widget_init_template(GTK_WIDGET(self));
}
```

---

## 3. High-Performance Lists: `GtkListView` & `GtkColumnView`

In GTK 4, legacy `GtkTreeView` and `GtkCellRenderer` are superseded by scalable list widgets:
- Driven by `GListModel` (providing data items).
- Uses `GtkListItemFactory` (or `GtkBuilderListItemFactory`) to instantiate visual widgets only for rows currently visible on screen.
- Supports sorting and filtering via `GtkSortListModel` and `GtkFilterListModel` without mutating source data.
