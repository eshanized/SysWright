# Linux Application Configuration & State Management

## 1. The XDG Base Directory Specification

Native Linux applications must respect the Freedesktop.org **XDG Base Directory Specification (v0.8+)**. Hardcoding configuration or runtime state directly into the home directory (e.g., `~/.myapprc`) or the executable directory is strictly forbidden.

### 1.1 Directory Hierarchy & Environment Variables

| Variable | Fallback Default Path | Purpose & Lifecycle | Example Path |
|---|---|---|---|
| **`XDG_CONFIG_HOME`** | `$HOME/.config` | User-specific static configuration files; edited by user or UI; preserved across backups | `~/.config/myapp/config.toml` |
| **`XDG_DATA_HOME`** | `$HOME/.local/share` | User-specific persistent data files (databases, plugins, templates, game saves); preserved across backups | `~/.local/share/myapp/library.db` |
| **`XDG_STATE_HOME`** | `$HOME/.local/state` | State that should persist between application restarts but is not critical to back up (history, window geometry, recent files) | `~/.local/state/myapp/history.log` |
| **`XDG_CACHE_HOME`** | `$HOME/.cache` | Non-essential cached data (thumbnails, downloaded indices, pre-parsed ASTs); can be deleted at any time without data loss | `~/.cache/myapp/thumbnails/` |
| **`XDG_RUNTIME_DIR`** | `/run/user/$UID` | Ephemeral runtime communication sockets, lockfiles, named pipes; managed by `pam_systemd`; wiped upon session logout | `/run/user/1000/myapp.sock` |

### 1.2 System-Wide Configuration & Fallbacks
When reading configuration, applications should follow a layered cascade:
1. Active CLI flags (`--config=/path`).
2. User configuration: `$XDG_CONFIG_HOME/<app>/config.toml`.
3. System-wide configuration: `$XDG_CONFIG_DIRS/<app>/config.toml` (defaults to `/etc/xdg/<app>/config.toml`).
4. Hardcoded compiled-in defaults.

---

## 2. Atomic Configuration & State Persistence

Filesystem write operations are not atomic. A process crash or power loss during `write()` can corrupt configuration files, truncating them to 0 bytes.

### 2.1 The Atomic Replace Pattern
To write or update configuration files safely:
1. Create a temporary file in the **same directory and same filesystem** as the target file (ensuring `rename(2)` can execute atomically without cross-device `EXDEV` errors):
   ```c
   char temp_path[PATH_MAX];
   snprintf(temp_path, sizeof(temp_path), "%s.tmp.XXXXXX", target_path);
   int fd = mkstemp(temp_path);
   ```
2. Set strict file permissions (`0600` for user-private configuration or secrets).
3. Write the complete configuration content to `fd`.
4. Flush data and metadata to disk using `fsync(fd)`.
5. Close the file descriptor `close(fd)`.
6. Atomically replace the target file using `rename(temp_path, target_path)`.
7. Call `fsync(dir_fd)` on the containing parent directory to persist the directory entry update to non-volatile storage.

```rust
// Rust equivalent using tempfile crate
use std::io::Write;
use tempfile::NamedTempFile;

pub fn write_config_atomic(target: &std::path::Path, data: &[u8]) -> std::io::Result<()> {
    let parent = target.parent().unwrap_or(std::path::Path::new("."));
    std::fs::create_dir_all(parent)?;
    
    // Create temp file in same directory
    let mut temp = NamedTempFile::new_in(parent)?;
    temp.write_all(data)?;
    temp.as_file().sync_all()?; // fsync data
    
    // Atomic rename
    temp.persist(target).map_err(|e| e.error)?;
    
    // Sync directory entry
    let dir = std::fs::File::open(parent)?;
    dir.sync_all()?;
    Ok(())
}
```

---

## 3. Configuration Format Selection

| Format | Strengths | Weaknesses | Best Use Case |
|---|---|---|---|
| **TOML** | Human-readable, strict typing, native comments, hierarchical tables | Slower for massive payloads (>10MB) | Default choice for application configuration files (`config.toml`) |
| **JSON** | Universal, high-speed parsing, standardized | No comments allowed, verbose syntax | Inter-process IPC payloads, structured machine output |
| **INI / Desktop Entry** | Simple, native GLib/GKeyFile support, minimal syntax | Poor support for nested arrays and complex structures | System services, desktop entry metadata |
| **YAML** | Compact syntax, expressive | Ambiguous type coercion (e.g. Norway problem), complex parsers | Complex Kubernetes/CI specs; avoid for desktop application configs |

---

## 4. Configuration Migration & Versioning

- Store an explicit schema version integer inside the configuration file:
  ```toml
  schema_version = 2
  ```
- Upon startup, verify `schema_version`:
  - If equal to current: Load directly.
  - If older: Automatically execute a migration sequence ($1 \to 2$, $2 \to 3$), backup the original file to `config.toml.bak.<timestamp>`, and atomically write the updated configuration.
  - If newer: Refuse to overwrite; emit a clear error advising the user to update the application or inspect configuration compatibility.
