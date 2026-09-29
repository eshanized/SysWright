# Icon Theme Specification & Hicolor Hierarchy

## 1. Scope & The Hicolor Fallback Theme

Linux desktop environments resolve icons following the **Freedesktop Icon Theme Specification**. The universal fallback theme required by all distributions is **`hicolor`**.

---

## 2. Directory Hierarchy

Applications must install icons under `/usr/share/icons/hicolor/<size>/<context>/`:

```text
/usr/share/icons/hicolor/
├── 16x16/apps/com.example.MyApp.png
├── 32x32/apps/com.example.MyApp.png
├── 48x48/apps/com.example.MyApp.png
├── 64x64/apps/com.example.MyApp.png
├── 128x128/apps/com.example.MyApp.png
├── 256x256/apps/com.example.MyApp.png
├── 512x512/apps/com.example.MyApp.png
├── scalable/apps/com.example.MyApp.svg          <-- Scalable vector icon (MANDATORY)
└── symbolic/apps/com.example.MyApp-symbolic.svg <-- Monochrome theme-adaptive icon
```

### Invariants:
1. **Naming**: The icon file base name must match the application ID declared in the desktop entry (`Icon=com.example.MyApp`).
2. **Context**: Application icons belong in the `apps/` context subdirectory, never in the root of the size directory.
3. **Scalable Vector Graphics (SVG)**: Always provide a vector SVG icon in `scalable/apps/` to ensure sharp rendering across fractional scaling and 4K/8K displays.
4. **Symbolic Icons**: For header bars, system trays, and mobile interfaces, provide a monochrome SVG in `symbolic/apps/` matching the suffix `-symbolic.svg`.

---

## 3. Icon Cache Invalidation

When installing icons directly or building packages:
```bash
gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor
```
This regenerates `icon-theme.cache`, ensuring desktop docks immediately display the newly installed application icon.
