# Shared MIME-Info Specification & File Associations

## 1. Scope & The MIME Database

Linux systems identify file formats using the **Freedesktop Shared MIME-Info Database**, relying on magic numbers (content sniffing) and file extension glob patterns.

---

## 2. Registering Custom MIME Types

When an application introduces a custom file format (e.g. `.myproj`), it must install an XML definition to `/usr/share/mime/packages/<app-id>.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="application/x-myproject">
    <comment>MyProject Document</comment>
    <comment xml:lang="de">MyProject Dokument</comment>
    <icon name="application-x-myproject"/>
    <glob pattern="*.myproj"/>
    <magic priority="50">
      <match type="string" offset="0" value="MYPROJ\0"/>
    </magic>
  </mime-type>
</mime-info>
```

### Installation Hook:
```bash
update-mime-database /usr/share/mime
```

---

## 3. Binding Desktop Applications to MIME Types

To associate an application with file types:
1. In the `.desktop` file:
   ```ini
   MimeType=application/x-myproject;text/plain;
   ```
2. When the desktop database is refreshed via `update-desktop-database /usr/share/applications`, the file manager (Nautilus, Dolphin, Thunar) automatically lists the application in the "Open With..." menu.
3. User default associations are persisted in `$XDG_CONFIG_HOME/mimeapps.list`.
