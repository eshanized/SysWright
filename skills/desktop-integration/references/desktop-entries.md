# Desktop Entry Specification (Freedesktop Standard)

## 1. Scope & Standards Compliance

Desktop entries (`.desktop` files) provide application launchers, icons, MIME bindings, and menu entries on Linux desktops following the **Freedesktop Desktop Entry Specification (v1.5)**.

---

## 2. Standard Structure & Field Invariants

Desktop entries are installed to `/usr/share/applications/<app-id>.desktop`:

```ini
[Desktop Entry]
Version=1.5
Type=Application
Name=Code Editor
GenericName=Text and Source Code Editor
Comment=Edit code and text documents with high performance
Exec=myeditor %F
Icon=com.example.MyEditor
Terminal=false
Categories=Development;TextEditor;Utility;
Keywords=text;editor;code;development;
MimeType=text/plain;application/json;application/xml;
StartupNotify=true
StartupWMClass=com.example.MyEditor
Actions=NewWindow;ProfileMode;

[Desktop Action NewWindow]
Name=Open New Window
Exec=myeditor --new-window

[Desktop Action ProfileMode]
Name=Open in Profile Mode
Exec=myeditor --profile
```

### Critical Field Invariants:
1. **`Type`**: Must be `Application` for standard desktop programs (other valid values: `Link`, `Directory`).
2. **`Exec`**: The command line to execute. Field codes must be capitalized properly:
   - `%f`: A single local file name.
   - `%F`: A list of files (multiple arguments).
   - `%u`: A single URL.
   - `%U`: A list of URLs.
   - Never use unescaped shell pipes or redirections in `Exec=`.
3. **`Icon`**: The icon name without extension or path (e.g. `com.example.MyEditor`). The desktop environment resolves this icon through the Hicolor icon theme.
4. **`Categories`**: Semicolon-separated list ending with a semicolon (e.g. `Development;IDE;`).
5. **`StartupWMClass`**: Matches the Wayland `app_id` or X11 `WM_CLASS` to bind running windows to the launcher icon in desktop docks.

---

## 3. Automated Validation

Every `.desktop` file must be validated during development and CI using the official tool:
```bash
desktop-file-validate myapp.desktop
```
If errors or warnings are emitted, the file must be corrected before packaging.
