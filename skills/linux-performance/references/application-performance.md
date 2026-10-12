# Native Application Performance: Startup, UI Responsiveness, and Event Loops

Technical reference for optimizing desktop application launch latency, rendering performance, and event loop responsiveness in C, C++, Rust, Qt, and GTK.

---

## 1. Deconstructing Cold Startup Time

Application startup is divided into three distinct phases:

```
[Exec / Kernel ELF Mapping] ──► [Dynamic Linker (ld.so)] ──► [Static Init / main()] ──► [First Frame Rendered]
```

### Phase 1: Dynamic Linking & Symbol Relocation
The dynamic linker (`ld-linux.so`) loads shared libraries and resolves symbols.
- Excessive shared libraries (`DT_NEEDED`) and symbols dramatically increase launch time.
- Measure linking overhead using `LD_DEBUG`:
  ```bash
  LD_DEBUG=statistics ./my_app
  ```
  Reports:
  - Total number of shared objects loaded.
  - Number of relocations processed (lazy vs immediate).
  - Time spent in symbol lookup and relocations.

### Optimizations:
1. **Reduce Direct Dependencies**: Audit linked libraries with `ldd` and link only required libraries (`--as-needed`).
2. **Enable RELRO with Lazy Binding**: Full RELRO (`-z relro -z now`) forces all relocations at launch; for CLI tools with hundreds of unused functions, partial RELRO (`-z relro -z lazy`) can speed startup, though full RELRO is preferred for security.
3. **Use LLD or Mold Linker**: Modern linkers deduplicate strings and optimize `.gnu.hash` tables for faster runtime lookup.

---

## 2. Event-Loop Latency and UI Responsiveness

Both Qt (`QEventLoop`) and GTK (`GMainLoop`) rely on an underlying event-driven reactor pattern powered by `epoll(7)` or `poll(2)`.

### The 16ms Rule (60 FPS):
To maintain smooth 60 frames per second rendering:
$$\text{Max Frame Time} = \frac{1000\text{ ms}}{60} \approx 16.66\text{ ms}$$
If any task on the main GUI thread takes longer than 16ms, the event loop stalls, dropping frames and causing visible UI freezing ("jank").

### Anti-Patterns on Main Thread:
| Anti-Pattern | Immediate Symptom | Remediation |
|---|---|---|
| Synchronous File I/O (`read()`, `fopen()`) | UI freezes while disk spins up or network mounts hang | Move I/O to background thread worker or use `io_uring` / `GTask` / `QThreadPool`. |
| Synchronous Network Request (`curl`, `socket`) | Complete UI freeze on network latency or DNS timeout | Use asynchronous HTTP clients (`QNetworkAccessManager`, `libsoup`). |
| Complex Database Queries (SQLite) | Stutter on table scroll | Offload database queries to background thread; pass immutable model slices. |
| Heavy JSON / XML Parsing | Stutter during data fetch | Parse payloads asynchronously in worker thread. |

---

## 3. Profiling Desktop Event Loops

### Qt QML Profiler:
```bash
# Launch Qt Quick app with QML profiling agent enabled
./my_qt_app -qmljsdebugger=port:3768,block
```
Inspects:
- Time spent compiling JavaScript/QML bindings.
- QML property binding re-evaluation count.
- Frame rate (FPS) and animation synchronization.

### GTK Inspector:
```bash
# Launch GTK application with inspector enabled
GTK_DEBUG=interactive ./my_gtk_app
```
Inspects widget tree layout recalculations, CSS re-parsing, and rendering draw cycles.
