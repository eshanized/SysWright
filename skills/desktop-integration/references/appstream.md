# AppStream Specification & Software Center Metadata

## 1. Scope & The AppStream Standard

The **AppStream Specification** provides rich metadata (human-readable descriptions, screenshots, release history, categories, hardware requirements) consumed by modern Linux software centers (GNOME Software, KDE Discover).

---

## 2. Standard Structure (`metainfo.xml`)

AppStream metadata files must be installed to `/usr/share/metainfo/<app-id>.metainfo.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>com.example.MyEditor</id>
  <metadata_license>FSFAP</metadata_license>
  <project_license>GPL-3.0-or-later</project_license>
  <name>Code Editor</name>
  <summary>A fast and lightweight code editor for Linux</summary>
  <description>
    <p>
      Code Editor is an extensible, high-performance source code editor built
      specifically for modern Linux desktops.
    </p>
    <ul>
      <li>Syntax highlighting for over 50 languages</li>
      <li>Integrated terminal and git management</li>
      <li>Vim and Emacs keybinding support</li>
    </ul>
  </description>
  <launchable type="desktop-id">com.example.MyEditor.desktop</launchable>
  <url type="homepage">https://example.com/editor</url>
  <url type="bugtracker">https://example.com/editor/issues</url>
  <screenshots>
    <screenshot type="default">
      <image>https://example.com/screenshots/main.png</image>
      <caption>The main code editing interface with sidebar</caption>
    </screenshot>
  </screenshots>
  <releases>
    <release version="1.2.0" date="2026-11-20">
      <description>
        <p>Introduced Wayland fractional scaling improvements and faster syntax highlighting.</p>
      </description>
    </release>
  </releases>
  <content_rating type="oars-1.1" />
</component>
```

---

## 3. Automated Validation

Validate AppStream metadata files during build and CI using `appstreamcli`:
```bash
appstreamcli validate --strict /usr/share/metainfo/com.example.MyEditor.metainfo.xml
```
Verification passes only when return code is 0 and no fatal validation errors are reported.
