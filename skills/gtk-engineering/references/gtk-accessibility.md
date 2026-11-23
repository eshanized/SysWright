# GTK 4 Accessibility Engineering (AT-SPI)

## 1. Scope & The Accessibility Imperative

In Syswright, accessibility is an uncompromising engineering requirement. Software that only functions with a mouse and fails for keyboard or screen reader users is defective.
GTK 4 implements native accessibility through the **Assistive Technology Service Provider Interface (AT-SPI v2)** using the `GtkAccessible` interface.

---

## 2. Core Accessibility Properties

Every user-interactive widget in GTK 4 implements `GtkAccessible`. Developers must ensure:

1. **Accessible Roles (`GtkAccessibleRole`)**:
   - Widgets have explicit semantic roles (`GTK_ACCESSIBLE_ROLE_BUTTON`, `GTK_ACCESSIBLE_ROLE_CHECKBOX`, `GTK_ACCESSIBLE_ROLE_HEADING`, `GTK_ACCESSIBLE_ROLE_STATUS`).
2. **Accessible Names (`label` or `labelled-by`)**:
   - For icon-only buttons (e.g. a search button containing only a magnifying glass icon), a screen reader has no text to announce. You **must** set an accessible label:
     ```c
     GtkWidget *btn = gtk_button_new_from_icon_name("edit-find-symbolic");
     gtk_accessible_update_property(
         GTK_ACCESSIBLE(btn),
         GTK_ACCESSIBLE_PROPERTY_LABEL, "Search files",
         -1
     );
     ```
3. **Keyboard Navigation & Focus Chains**:
   - Every interactive control must be reachable via the `Tab` and `Shift+Tab` keys.
   - Set `gtk_widget_set_focusable(widget, TRUE)` on interactive elements.
   - Verify keyboard activation: buttons must activate on `Return` and `Space`.

---

## 3. High Contrast & Reduced Motion

Respect user desktop settings for assistive visual profiles:
- **Reduced Motion**: Check `gtk_widget_get_settings()` for `gtk-enable-animations`. If false, skip non-essential layout sliding or spinning animations.
- **High Contrast**: Ensure text contrast meets WCAG AA standards (minimum 4.5:1 ratio against background).
