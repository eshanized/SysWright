# XDG Base Directory Specification Reference

## 1. Scope & The Specification Standard

The **XDG Base Directory Specification** defines the standard environment variables and default fallback paths for user-specific files across all compliant Linux desktop environments and command-line applications.

---

## 2. Definitive Path Resolution Table

| Environment Variable | Default Fallback Value | Access Mode & Permissions | Intended Content |
|---|---|---|---|
| **`XDG_CONFIG_HOME`** | `$HOME/.config` | `0700` (User read/write) | User configuration files (`.conf`, `.toml`, `.json`). Backed up. |
| **`XDG_DATA_HOME`** | `$HOME/.local/share` | `0700` (User read/write) | Persistent user data (databases, local mail stores, game progress). Backed up. |
| **`XDG_STATE_HOME`** | `$HOME/.local/state` | `0700` (User read/write) | Persistent state not critical to backups (recently opened files, window geometry, command history). |
| **`XDG_CACHE_HOME`** | `$HOME/.cache` | `0700` (User read/write) | Non-essential cached data (thumbnails, downloaded web assets). Safe to purge at any time. |
| **`XDG_RUNTIME_DIR`** | `/run/user/$UID` | `0700` (Ephemeral RAM disk) | Sockets, pipes, lockfiles. Wiped on user session termination. |
| **`XDG_CONFIG_DIRS`** | `/etc/xdg` | Semicolon/colon-separated list | System-wide configuration search paths. |
| **`XDG_DATA_DIRS`** | `/usr/local/share:/usr/share` | Semicolon/colon-separated list | System-wide static data search paths (icons, themes, desktop entries). |

---

## 3. Reference Implementation Algorithm (C / POSIX)

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

void get_app_config_dir(const char *app_name, char *out_path, size_t out_size) {
    const char *xdg_config = getenv("XDG_CONFIG_HOME");
    if (xdg_config && xdg_config[0] != '\0') {
        snprintf(out_path, out_size, "%s/%s", xdg_config, app_name);
        return;
    }

    const char *home = getenv("HOME");
    if (!home || home[0] == '\0') {
        /* Extreme fallback if HOME is unset */
        home = "/tmp";
    }
    snprintf(out_path, out_size, "%s/.config/%s", home, app_name);
}
```
