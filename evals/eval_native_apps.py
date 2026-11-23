#!/usr/bin/env python3
"""
Linux Native Application Engineering Evaluation Engine
Part of Syswright

Deterministic evaluation suite that verifies AI agent responses and engineering
recommendations against authoritative Linux application architecture, Qt 6/QML,
GTK 4, Freedesktop integration, and build systems standards.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def evaluate_native_apps_scenario(scenario: Dict[str, Any], response_text: str) -> Tuple[bool, str]:
    """
    Evaluates whether an engineering response satisfies the criteria for
    a specific Linux Native Application Engineering evaluation scenario.
    """
    resp_lower = response_text.lower()
    sid = scenario["id"]
    eval_type = scenario["eval_type"]

    # -------------------------------------------------------------
    # Domain 1: General Application Engineering
    # -------------------------------------------------------------
    if eval_type == "app_rust_cli":
        if "tokio" in resp_lower and ("not" not in resp_lower and "unnecessary" not in resp_lower and "avoid" not in resp_lower and "against" not in resp_lower):
            return False, "Anti-pattern: recommended unnecessary Tokio runtime for simple CLI hashing"
        if "stdout" not in resp_lower or "stderr" not in resp_lower:
            return False, "Missing strict stdout/stderr separation principle"
        if "terminal" not in resp_lower and "isatty" not in resp_lower and "no_color" not in resp_lower:
            return False, "Missing terminal capability detection or NO_COLOR handling"
        if "clap" not in resp_lower:
            return False, "Missing recommendation for clap CLI parser"
        return True, "Accurate Rust CLI architecture with proper stream separation and sync runtime"

    elif eval_type == "app_c_utility":
        if "leak" not in resp_lower and "resource" not in resp_lower:
            return False, "Failed to identify resource leak of file descriptor and memory buffer"
        if "goto" not in resp_lower and "cleanup" not in resp_lower and "autofree" not in resp_lower:
            return False, "Missing single-point-of-exit cleanup goto or __attribute__((cleanup))"
        if "null" not in resp_lower:
            return False, "Missing check for NULL return from fopen/malloc"
        return True, "Correctly identified C resource leaks and prescribed cleanup pattern"

    elif eval_type == "app_cpp_modern":
        if "delete[]" not in resp_lower and "array" not in resp_lower and "mismatch" not in resp_lower:
            return False, "Failed to identify delete vs delete[] mismatch on raw array"
        if "terminate" not in resp_lower and "join" not in resp_lower and "detach" not in resp_lower:
            return False, "Failed to identify std::terminate() risk on unjoined std::thread"
        if "unique_ptr" not in resp_lower and "vector" not in resp_lower:
            return False, "Missing RAII container recommendation (std::unique_ptr or std::vector)"
        if "jthread" not in resp_lower and "stop_token" not in resp_lower:
            return False, "Missing recommendation for C++20 std::jthread with stop_token"
        return True, "Correctly identified modern C++ RAII and thread management flaws"

    elif eval_type == "app_system_daemon":
        if "double-fork" in resp_lower and ("anti-pattern" not in resp_lower and "avoid" not in resp_lower and "legacy" not in resp_lower and "against" not in resp_lower):
            return False, "Anti-pattern: recommended obsolete double-fork daemonize()"
        if "sd_notify" not in resp_lower and "ready=1" not in resp_lower:
            return False, "Missing systemd readiness notification (sd_notify)"
        if "foreground" not in resp_lower and "systemd" not in resp_lower:
            return False, "Failed to advise running in foreground under systemd"
        if "sighup" not in resp_lower and "reload" not in resp_lower:
            return False, "Missing SIGHUP configuration reload handling"
        return True, "Authoritative modern Linux daemon architecture integrating with systemd"

    elif eval_type == "app_microservices_critique":
        if "reject" not in resp_lower and "inappropriate" not in resp_lower and "bloat" not in resp_lower and "overhead" not in resp_lower:
            return False, "Failed to critique inappropriate local microservice architecture"
        if "monolith" not in resp_lower and "in-process" not in resp_lower and "single" not in resp_lower:
            return False, "Missing recommendation for clean modular monolith"
        if "unix" not in resp_lower and "af_unix" not in resp_lower and "shared memory" not in resp_lower:
            return False, "Missing recommendation for Unix domain sockets or shared memory"
        return True, "Correctly rejected local microservice bloat and advocated modular architecture"

    elif eval_type == "app_process_lifecycle":
        if "zombie" not in resp_lower and "defunct" not in resp_lower:
            return False, "Failed to diagnose zombie / defunct process accumulation"
        if "sigchld" not in resp_lower:
            return False, "Missing SIGCHLD signal handling"
        if "waitpid" not in resp_lower:
            return False, "Missing waitpid() child process reaping"
        if "wnohang" not in resp_lower:
            return False, "Missing WNOHANG flag for non-blocking reaping"
        return True, "Accurate diagnosis of process lifecycle zombie leak and waitpid resolution"

    elif eval_type == "app_unsafe_filesystem":
        if "path traversal" not in resp_lower and "../" not in resp_lower and "traversal" not in resp_lower:
            return False, "Failed to identify path traversal vulnerability"
        if "symlink" not in resp_lower and "tmp" not in resp_lower:
            return False, "Failed to identify symlink / shared /tmp race vulnerability"
        if "openat2" not in resp_lower and "beneath" not in resp_lower and "canonical" not in resp_lower and "mkstemp" not in resp_lower:
            return False, "Missing safe filesystem primitive (openat2 with RESOLVE_BENEATH, canonicalize, or mkstemp)"
        return True, "Comprehensive filesystem security audit identifying path traversal and symlink risks"

    elif eval_type == "app_concurrency_deadlock":
        if "deadlock" not in resp_lower and "inversion" not in resp_lower:
            return False, "Failed to diagnose lock-order inversion deadlock"
        if "scoped_lock" not in resp_lower and "hierarchy" not in resp_lower and "std::lock" not in resp_lower:
            return False, "Missing recommendation for std::scoped_lock or global lock hierarchy"
        return True, "Accurate diagnosis of lock-order inversion and multi-mutex acquisition fix"

    # -------------------------------------------------------------
    # Domain 2: Qt/QML Engineering
    # -------------------------------------------------------------
    elif eval_type == "qt_poorly_structured_qml":
        if "business logic" not in resp_lower and "sql" not in resp_lower and "database" not in resp_lower:
            return False, "Failed to flag embedding database logic in QML"
        if "gui thread" not in resp_lower and "main thread" not in resp_lower and "block" not in resp_lower and "freeze" not in resp_lower:
            return False, "Missing explanation of GUI main thread blocking"
        if "c++" not in resp_lower or "model" not in resp_lower:
            return False, "Missing recommendation to move logic to C++ model / controller"
        return True, "Correctly critiqued QML architecture and enforced C++ logic separation"

    elif eval_type == "qt_quick_architecture":
        if "qt_add_qml_module" not in resp_lower:
            return False, "Missing CMake directive 'qt_add_qml_module'"
        if "qml_element" not in resp_lower:
            return False, "Missing modern registration macro 'QML_ELEMENT'"
        if "aot" not in resp_lower and "compile" not in resp_lower and "bytecode" not in resp_lower:
            return False, "Missing explanation of ahead-of-time QML compilation"
        return True, "Authoritative Qt 6 CMake QML module architecture"

    elif eval_type == "qt_business_logic_in_qml":
        if "xmlhttprequest" not in resp_lower and "xhr" not in resp_lower and "synchronous" not in resp_lower:
            return False, "Failed to flag synchronous XMLHttpRequest in QML"
        if "qnetworkaccessmanager" not in resp_lower:
            return False, "Missing recommendation for C++ QNetworkAccessManager"
        if "thread" not in resp_lower and "qtconcurrent" not in resp_lower and "offload" not in resp_lower:
            return False, "Missing offload to worker QThread or QtConcurrent"
        return True, "Accurate diagnosis of QML network blocking and C++ async offload"

    elif eval_type == "qt_broken_property_binding":
        if "destroy" not in resp_lower and "break" not in resp_lower and "overwrit" not in resp_lower and "lost" not in resp_lower:
            return False, "Failed to explain that imperative assignment destroys property bindings"
        if "binding" not in resp_lower:
            return False, "Missing explanation of declarative binding re-establishment"
        return True, "Accurate explanation of QML property binding destruction and remediation"

    elif eval_type == "qt_qml_cpp_integration":
        if "setcontextproperty" not in resp_lower:
            return False, "Missing analysis of setContextProperty() anti-pattern"
        if "qmllint" not in resp_lower and "type" not in resp_lower:
            return False, "Missing explanation that setContextProperty blinds qmllint / type safety"
        if "qml_element" not in resp_lower and "qml_singleton" not in resp_lower:
            return False, "Missing prescription for QML_ELEMENT or QML_SINGLETON"
        return True, "Authoritative modern Qt 6 QML/C++ integration review"

    elif eval_type == "qt_gui_thread_blocking":
        if "gui thread" not in resp_lower and "main thread" not in resp_lower and "event loop" not in resp_lower:
            return False, "Failed to diagnose GUI main thread / event loop starvation"
        if "qthread" not in resp_lower and "qtconcurrent" not in resp_lower:
            return False, "Missing prescription for worker QThread or QtConcurrent"
        if "signal" not in resp_lower and "slot" not in resp_lower:
            return False, "Missing queued signals and slots communication"
        return True, "Accurate diagnosis of GUI thread starvation and worker thread offload"

    elif eval_type == "qt_widgets_vs_quick":
        if "qt widgets" not in resp_lower:
            return False, "Failed to recommend Qt Widgets for data-dense desktop CAD application"
        if "dock" not in resp_lower and "qdockwidget" not in resp_lower:
            return False, "Missing mention of dockable layouts (QDockWidget)"
        if "table" not in resp_lower and "model" not in resp_lower:
            return False, "Missing mention of Model/View data density (QTableView)"
        return True, "Authoritative evaluation of Qt Widgets vs Qt Quick trade-offs"

    # -------------------------------------------------------------
    # Domain 3: GTK Engineering
    # -------------------------------------------------------------
    elif eval_type == "gtk_application_architecture":
        if "startup" not in resp_lower or "activate" not in resp_lower:
            return False, "Missing distinction between startup and activate signals"
        if "window" not in resp_lower and "present" not in resp_lower:
            return False, "Failed to explain creating/presenting window in activate signal"
        if "action" not in resp_lower and "gaction" not in resp_lower:
            return False, "Missing GActions registration in startup"
        return True, "Accurate GTK 4 application architecture and lifecycle management"

    elif eval_type == "gtk_gobject_ownership":
        if "floating" not in resp_lower and "leak" not in resp_lower:
            return False, "Failed to explain floating reference mechanics on unparented widget"
        if "g_signal_connect_object" not in resp_lower and "cycle" not in resp_lower and "unref" not in resp_lower:
            return False, "Missing g_signal_connect_object or reference cycle remediation"
        return True, "Correct diagnosis of GObject floating references and signal callback lifecycles"

    elif eval_type == "gtk_blocked_main_loop":
        if "gmaincontext" not in resp_lower and "main loop" not in resp_lower and "main thread" not in resp_lower:
            return False, "Failed to diagnose GMainContext / main loop blocking"
        if "async" not in resp_lower or ("g_file_load_contents_async" not in resp_lower and "gtask" not in resp_lower):
            return False, "Missing prescription for g_file_load_contents_async or GTask"
        return True, "Accurate diagnosis of GTK main loop blocking and GIO async resolution"

    elif eval_type == "gtk_libadwaita_compatibility":
        if "standard gtk" not in resp_lower and "gtk 4" not in resp_lower and "gtk4" not in resp_lower:
            return False, "Missing recommendation for standard GTK 4 for cross-desktop neutrality"
        if "gnome" not in resp_lower or "hig" not in resp_lower:
            return False, "Missing explanation of Libadwaita coupling to GNOME HIG"
        if "theme" not in resp_lower and "neutral" not in resp_lower:
            return False, "Missing explanation of system theme overriding"
        return True, "Authoritative evaluation of standard GTK 4 vs Libadwaita desktop portability"

    elif eval_type == "gtk_accessibility_audit":
        if "accessible" not in resp_lower and "at-spi" not in resp_lower and "orca" not in resp_lower:
            return False, "Missing AT-SPI accessibility or screen reader analysis"
        if "label" not in resp_lower and "name" not in resp_lower:
            return False, "Missing requirement for accessible label / name on icon-only button"
        if "focus" not in resp_lower and "keyboard" not in resp_lower:
            return False, "Missing keyboard navigation / focus verification"
        return True, "Comprehensive GTK 4 accessibility audit adhering to AT-SPI standards"

    # -------------------------------------------------------------
    # Domain 4: Desktop Integration
    # -------------------------------------------------------------
    elif eval_type == "desktop_entry_validation":
        if "type=application" not in resp_lower.replace(" ", ""):
            return False, "Missing mandatory field 'Type=Application'"
        if "desktop-file-validate" not in resp_lower:
            return False, "Missing official validation tool 'desktop-file-validate'"
        if "icon" not in resp_lower or "path" not in resp_lower:
            return False, "Failed to flag hardcoded icon path instead of hicolor icon name"
        return True, "Thorough Desktop Entry review and validation with desktop-file-validate"

    elif eval_type == "desktop_dbus_design":
        if "reverse" not in resp_lower and "org." not in resp_lower:
            return False, "Missing reverse-domain naming convention (org.example...)"
        if "introspection" not in resp_lower and "interface" not in resp_lower and "<node" not in resp_lower:
            return False, "Missing D-Bus introspection XML definition"
        if "property" not in resp_lower and "signal" not in resp_lower:
            return False, "Missing properties or signals in D-Bus API design"
        return True, "Authoritative D-Bus API design with reverse-domain names and introspection XML"

    elif eval_type == "desktop_dbus_authorization":
        if "polkit" not in resp_lower:
            return False, "Missing mandatory polkit authorization enforcement"
        if "vulnerability" not in resp_lower and "privilege" not in resp_lower and "command" not in resp_lower and "arbitrary" not in resp_lower:
            return False, "Failed to flag arbitrary command execution vulnerability"
        return True, "Correctly rejected insecure D-Bus system bus method and enforced polkit gating"

    elif eval_type == "desktop_missing_portal":
        if "sandbox" not in resp_lower and "isolation" not in resp_lower and "namespace" not in resp_lower:
            return False, "Failed to diagnose sandbox / mount namespace isolation"
        if "portal" not in resp_lower or "filechooser" not in resp_lower:
            return False, "Missing prescription for org.freedesktop.portal.FileChooser"
        return True, "Accurate diagnosis of sandboxed file access and XDG Desktop Portal resolution"

    elif eval_type == "desktop_wayland_vs_x11":
        if "isolation" not in resp_lower and "snoop" not in resp_lower and "security" not in resp_lower:
            return False, "Missing explanation of Wayland client isolation security model"
        if "portal" not in resp_lower and "pipewire" not in resp_lower and "screencast" not in resp_lower:
            return False, "Missing XDG Desktop Portal (GlobalShortcuts / ScreenCast) or PipeWire recommendation"
        return True, "Accurate distinction between X11 global access and Wayland portal-mediated security"

    elif eval_type == "desktop_mime_registration":
        if "update-mime-database" not in resp_lower:
            return False, "Missing command 'update-mime-database'"
        if "/usr/share/mime" not in resp_lower:
            return False, "Missing MIME packages directory '/usr/share/mime/packages/'"
        if "mimetype" not in resp_lower:
            return False, "Missing MimeType association in desktop entry"
        return True, "Complete MIME registration procedure with update-mime-database"

    elif eval_type == "desktop_appstream_metadata":
        if "appstreamcli" not in resp_lower:
            return False, "Missing validation tool 'appstreamcli validate'"
        if "license" not in resp_lower:
            return False, "Failed to identify missing metadata_license or project_license"
        if "component" not in resp_lower or "desktop-application" not in resp_lower:
            return False, "Failed to identify invalid component type (must be desktop-application)"
        return True, "Thorough AppStream metadata review verified via appstreamcli validate"

    # -------------------------------------------------------------
    # Domain 5: Build Systems Engineering
    # -------------------------------------------------------------
    elif eval_type == "build_modern_cmake":
        if "target_include_directories" not in resp_lower:
            return False, "Missing modern directive 'target_include_directories'"
        if "target_link_libraries" not in resp_lower:
            return False, "Missing modern directive 'target_link_libraries'"
        if "private" not in resp_lower and "public" not in resp_lower:
            return False, "Missing target visibility scope (PRIVATE / PUBLIC / INTERFACE)"
        if "global" not in resp_lower and "include_directories" not in resp_lower and "legacy" not in resp_lower:
            return False, "Failed to critique legacy global directory commands"
        return True, "Comprehensive modern target-based CMake refactoring"

    elif eval_type == "build_meson_dependencies":
        if "pkg-config" not in resp_lower and "pkgconfig" not in resp_lower:
            return False, "Missing explanation that Meson queries pkg-config by default"
        if "gtk4" not in resp_lower:
            return False, "Missing identification of missing gtk4 development package"
        if "wrap" not in resp_lower and "subproject" not in resp_lower and "fallback" not in resp_lower:
            return False, "Missing mention of Meson wrap / subproject fallback"
        return True, "Accurate diagnosis of Meson dependency failure and pkg-config resolution"

    elif eval_type == "build_cargo_workspace":
        if "workspace" not in resp_lower:
            return False, "Missing root Cargo workspace declaration [workspace]"
        if "lto" not in resp_lower and "strip" not in resp_lower:
            return False, "Missing release profile optimizations (LTO and strip)"
        if "--frozen" not in resp_lower:
            return False, "Missing offline build flag '--frozen'"
        return True, "Authoritative Cargo workspace structure with release profile and offline build discipline"

    elif eval_type == "build_abi_compatibility":
        if "vtable" not in resp_lower and "virtual" not in resp_lower and "abi" not in resp_lower:
            return False, "Failed to diagnose C++ virtual table layout corruption and ABI breakage"
        if ("kept" in resp_lower or "no bump" in resp_lower or "backwards-compatible" in resp_lower or "backward-compatible" in resp_lower) and ("not" not in resp_lower and "cannot" not in resp_lower and "never" not in resp_lower and "break" not in resp_lower):
            return False, "Anti-pattern: claimed ABI compatibility without incrementing SOVERSION"
        if "soversion" not in resp_lower or ("bump" not in resp_lower and "increment" not in resp_lower and "2" not in resp_lower):
            return False, "Missing explanation that SOVERSION must be incremented"
        return True, "Accurate diagnosis of C++ vtable ABI incompatibility and SOVERSION bump requirement"

    elif eval_type == "build_inappropriate_rpath":
        if "rpath" not in resp_lower and "runpath" not in resp_lower:
            return False, "Missing RPATH / RUNPATH analysis"
        if "$origin" not in resp_lower:
            return False, "Missing recommendation for relative '$ORIGIN' for application bundles"
        if "clear" not in resp_lower and "strip" not in resp_lower and "remove" not in resp_lower and "skip" not in resp_lower and "false" not in resp_lower:
            return False, "Missing recommendation to clear host build paths from RPATH"
        return True, "Correct identification of improper hardcoded RPATH and $ORIGIN resolution"

    elif eval_type == "build_cross_compilation":
        if "sysroot" not in resp_lower:
            return False, "Missing requirement for CMAKE_SYSROOT"
        if "cmake_find_root_path_mode" not in resp_lower and "find_root" not in resp_lower:
            return False, "Missing CMAKE_FIND_ROOT_PATH_MODE configuration"
        return True, "Authoritative cross-compilation toolchain file specification"

    elif eval_type == "build_bundled_dependency":
        if "bundled" not in resp_lower and "vendored" not in resp_lower:
            return False, "Failed to critique vendored / bundled library anti-pattern"
        if "find_package" not in resp_lower and "pkg_check_modules" not in resp_lower and "pkg-config" not in resp_lower:
            return False, "Missing recommendation for find_package or pkg-config system library discovery"
        if "security" not in resp_lower and "patch" not in resp_lower and "bloat" not in resp_lower:
            return False, "Missing explanation of security patching and bloat risks"
        return True, "Correctly enforced distribution policy against bundled dependencies"

    else:
        return False, f"Unknown evaluation type: '{eval_type}'"


def get_reference_native_apps_responses() -> Dict[str, str]:
    """
    Returns reference gold-standard engineering responses for all 34
    native application evaluation scenarios.
    """
    return {
        # -------------------------------------------------------------
        # Domain 1: General Application Engineering
        # -------------------------------------------------------------
        "eval_app_01_rust_cli": """
Rust CLI Application Architecture & Engineering Report:
1. Runtime Selection (Avoid Unnecessary Tokio):
   We advise AGAINST introducing Tokio or an asynchronous runtime for a local disk file hashing tool. Local disk I/O on Linux does not benefit from epoll/async runtimes (which are designed for high-concurrency non-blocking network sockets). Standard synchronous file operations with data parallelism via `rayon` (`par_iter()`) provide maximum CPU throughput, lower memory footprint, and instant cold-start time without async overhead.
2. Argument Parsing:
   Use `clap` (v4+) with the derive API: declare flags, subcommands, and options with clear descriptions and default values.
3. Stream Discipline (stdout vs stderr):
   - Machine-readable payload (file paths, SHA-256 hashes, or JSON) is emitted STRICTLY on `stdout`.
   - Human diagnostic logs, error messages, and progress indicators are emitted STRICTLY on `stderr`.
4. Terminal Detection & Color Accessibility:
   Check `std::io::stdout().is_terminal()` before emitting ANSI color escape codes. If output is redirected to a pipe or file, or if the `NO_COLOR` environment variable is present, disable all color codes automatically.
""",

        "eval_app_02_c_systems_utility": """
C Systems Utility Code Review & Remediation:
Fatal Flaws Detected:
1. Resource Leaks on Early Return:
   When `strstr(line, "ERROR")` evaluates to true, the function executes `return 1;` without closing the open FILE pointer `f` or freeing the heap buffer `buf`, causing persistent file descriptor and memory leaks.
2. Unchecked Pointer Dereferences:
   The code fails to check whether `fopen()` returned NULL or `malloc()` failed, risking immediate NULL pointer dereferences.
3. Unsafe String Copy:
   `strcpy(buf, line)` is vulnerable to buffer overflows if `line` exceeds 1024 bytes.

Remediation via Single-Point-of-Exit Cleanup Pattern:
```c
int process_log(const char *path) {
    int ret = -1;
    FILE *f = NULL;
    char *buf = NULL;
    char line[256];

    f = fopen(path, "r");
    if (!f) {
        perror("fopen");
        goto out;
    }

    buf = malloc(1024);
    if (!buf) {
        perror("malloc");
        goto out_close;
    }

    while (fgets(line, sizeof(line), f)) {
        if (strstr(line, "ERROR")) {
            snprintf(buf, 1024, "%s", line);
            ret = 1;
            goto out_free; // Guaranteed cleanup on error return
        }
    }
    ret = 0;

out_free:
    free(buf);
out_close:
    fclose(f);
out:
    return ret;
}
```
Alternatively, on GCC/Clang use `__attribute__((cleanup))` / `_autofree_` for RAII-style automated cleanup.
""",

        "eval_app_03_cpp_modern_app": """
Modern C++ Architecture & Defect Review:
Fatal Flaws Detected:
1. Heap Array Deallocation Mismatch:
   Allocating with `new int[1024]` requires deallocation with `delete[] raw_buffer;`. Calling scalar `delete raw_buffer;` is undefined behavior and corrupts the heap allocator.
2. `std::thread` Destructor Crash:
   The destructor of `std::thread` checks `joinable()`. If a thread is joinable when its destructor runs, it immediately invokes `std::terminate()`, crashing the entire application process.
3. Violation of Rule of Zero / RAII:
   Managing raw resource pointers and raw threads manually violates modern C++ memory safety.

Remediation (Modern C++20):
```cpp
#include <vector>
#include <thread>
#include <stop_token>

class Service {
public:
    Service() : worker_(&Service::run, this) {}
    // Rule of Zero: No manual destructor needed!
private:
    void run(std::stop_token stop_token) {
        while (!stop_token.stop_requested()) {
            // Work step
        }
    }

    std::vector<int> buffer_{std::vector<int>(1024)}; // Safe RAII memory
    std::jthread worker_; // C++20: Automatically signals stop_token and joins on destruction!
};
```
""",

        "eval_app_04_system_daemon": """
Modern Linux Daemon Architecture Specification:
Architectural Recommendation: REJECT LEGACY DOUBLE-FORK DAEMONIZE
1. The Legacy Double-Fork Anti-Pattern:
   Calling `fork()` twice, `setsid()`, and redirecting file descriptors to `/dev/null` was required in SysVinit, but is an anti-pattern on modern systemd Linux. Double-forking causes systemd to lose direct PID tracking, risks cgroup leakage, and disconnects process output from `journald`.
2. Modern systemd-Native Service Architecture:
   - Run in the foreground: Execute as PID 1's direct child without forking.
   - Readiness Notification: Set `Type=notify` in the service unit file. When internal initialization (socket binding, config parsing) finishes, send `READY=1` via `sd_notify(0, "READY=1")`.
   - Logging: Direct logs to `stderr`; systemd automatically timestamps and ingests logs into `journald`.
   - Signal Handling: Handle `SIGTERM`/`SIGINT` for graceful shutdown (flushing buffers and releasing locks), and handle `SIGHUP` for atomic online configuration reloading.
""",

        "eval_app_05_inappropriate_microservices": """
Architecture Review: INAPPROPRIATE USE OF LOCAL MICROSERVICES
Decision: REJECT LOCAL DOCKER MICROSERVICES ARCHITECTURE
Rationale:
1. Overhead & Latency:
   Running 4 independent Docker containers on a single desktop host to convert audio files introduces massive container runtime overhead, duplicated glibc instances, and serialization latency. Passing uncompressed PCM audio chunks over localhost HTTP/REST sockets incurs multi-millisecond network stack round-trips and memory copying.
2. Security Vulnerability:
   Binding internal microservices to localhost TCP ports (8001-8004) exposes internal endpoints to all unprivileged processes and local users on the workstation without file permissions or credentials.
3. Recommended Architecture: Modular In-Process Monolith:
   - Structure the application as a modular in-process monolith with clean subsystem boundaries (decoder, filter, encoder) communicating via in-memory function calls and zero-copy byte buffers.
   - If process privilege separation is genuinely required, use Unix domain sockets (`AF_UNIX` with `SOCK_SEQPACKET`) and shared memory file descriptors (`memfd_create` / `mmap`), authenticated via filesystem permissions (`0600`).
""",

        "eval_app_06_process_lifecycle_bug": """
Process Lifecycle Diagnostic: ZOMBIE PROCESS ACCUMULATION
Analysis:
1. Root Cause:
   The `<defunct>` process entries in `ps` are zombie processes. When a child process terminates, the Linux kernel retains its exit code and PID in the kernel process table until its parent process acknowledges termination by calling `wait()` or `waitpid()`. Because the parent daemon failed to reap its children, terminated workers remain indefinitely, eventually hitting `kernel.pid_max` and causing `fork: Resource temporarily unavailable`.
2. Remediation:
   Register a `SIGCHLD` signal handler in the parent daemon that reaps all terminated children in a non-blocking loop:
   ```c
   static void handle_sigchld(int sig) {
       int saved_errno = errno;
       int status;
       pid_t pid;
       // Non-blocking reap of all dead children
       while ((pid = waitpid(-1, &status, WNOHANG)) > 0) {
           // Child reaped cleanly
       }
       errno = saved_errno;
   }
   ```
   Or use `signalfd(2)` within the daemon event loop to read child termination events synchronously.
""",

        "eval_app_07_unsafe_filesystem_access": """
Security Audit: PATH TRAVERSAL & SYMLINK RACE VULNERABILITIES
Vulnerability Assessment:
1. Path Traversal Vulnerability:
   `sprintf(path, "/tmp/app_cache/%s", filename)` is critically vulnerable to path traversal. If an attacker supplies `../../etc/cron.d/malicious`, the path resolves outside the intended cache directory, allowing arbitrary file creation or overwriting.
2. Symlink / TOCTOU Attack in Shared `/tmp`:
   Opening a predictable file path in `/tmp` without `O_EXCL` allows local attackers to pre-create a symlink pointing to sensitive targets (`~/.ssh/authorized_keys`), causing the application to truncate or write into user files.

Remediation:
1. Enforce Path Boundaries:
   Use the modern Linux `openat2(2)` syscall with `RESOLVE_BENEATH` to guarantee that path resolution cannot escape the root directory, or canonicalize paths and verify the prefix.
2. Safe Temporary Files:
   Never invent static names in `/tmp`. Use `mkstemp(3)` or `open(path, O_CREAT | O_EXCL | O_RDWR, 0600)`.
3. Respect XDG Standards:
   Store application cache in `$XDG_CACHE_HOME/<app>/` (default `~/.cache/<app>/`), never in the world-writable shared `/tmp`.
""",

        "eval_app_08_concurrency_deadlock": """
Concurrency Diagnostic: LOCK-ORDER INVERSION DEADLOCK
Analysis:
1. Root Cause:
   The function `transfer(Account &from, Account &to)` acquires locks in caller order: `from.mutex.lock()` followed by `to.mutex.lock()`.
   When Thread 1 executes `transfer(AccountA, AccountB)` and Thread 2 concurrently executes `transfer(AccountB, AccountA)`:
   - Thread 1 locks AccountA and attempts to lock AccountB.
   - Thread 2 locks AccountB and attempts to lock AccountA.
   This forms a circular wait condition, causing a permanent lock-order inversion deadlock.
2. Remediation (Modern C++17 `std::scoped_lock`):
   Use `std::scoped_lock` which acquires multiple mutexes atomically using a deadlock-avoidance algorithm:
   ```cpp
   void transfer(Account &from, Account &to, double amount) {
       if (&from == &to) return; // Self-transfer guard
       std::scoped_lock lock(from.mutex, to.mutex); // Deadlock-free multi-lock acquisition!
       from.balance -= amount;
       to.balance += amount;
   }
   ```
   Alternatively, establish a strict global lock hierarchy (e.g. always lock the account with the smaller memory address or ID first).
""",

        # -------------------------------------------------------------
        # Domain 2: Qt/QML Engineering
        # -------------------------------------------------------------
        "eval_qt_01_poorly_structured_qml": """
QML Architectural Review: SEPARATION OF UI AND BUSINESS LOGIC
Review Findings:
1. Flawed Architecture:
   Embedding raw SQLite database queries (`LocalStorage.openDatabaseSync`) directly inside QML JavaScript event handlers completely violates the separation of concerns.
2. GUI Main Thread Blocking:
   The QML engine and visual scene graph run on the GUI main thread. Executing synchronous SQL queries (`openDatabaseSync`, `tx.executeSql`) freezes the event loop, causing dropped visual frames, delayed input response, and UI stutter.
3. Remediation:
   - Move database persistence and querying to C++.
   - Implement a C++ controller class inheriting from `QObject` and exposing a custom data model subclassing `QAbstractListModel`.
   - Register the C++ model with `QML_ELEMENT` so QML views can bind to it declaratively and efficiently.
""",

        "eval_qt_02_qt_quick_architecture": """
Qt 6 Modern QML Architecture & CMake Specification:
1. Modern CMake QML Module Configuration:
   Use `qt_standard_project_setup()` and `qt_add_qml_module()`:
   ```cmake
   cmake_minimum_required(VERSION 3.20)
   project(MyQtApp LANGUAGES CXX)

   find_package(Qt6 6.5 REQUIRED COMPONENTS Core Gui Quick)
   qt_standard_project_setup()

   add_executable(MyQtApp src/main.cpp)

   qt_add_qml_module(MyQtApp
       URI MyCompany.App
       VERSION 1.0
       QML_FILES
           qml/Main.qml
           qml/Dashboard.qml
       SOURCES
           src/TaskController.h src/TaskController.cpp
           src/DeviceModel.h src/DeviceModel.cpp
   )
   target_link_libraries(MyQtApp PRIVATE Qt6::Core Qt6::Gui Qt6::Quick)
   ```
2. Declarative Type Registration:
   Mark C++ classes with `QML_ELEMENT` (or `QML_SINGLETON`). CMake automatically registers them in the `MyCompany.App` module and compiles QML files to native C++ bytecode ahead-of-time (AOT) via `qmlcachegen`, eliminating obsolete runtime `qmlRegisterType` calls.
""",

        "eval_qt_03_business_logic_in_qml": """
QML Network Performance Diagnostic:
Defect Analysis:
1. Synchronous XMLHttpRequest Halt:
   Executing `xhr.open('GET', url, false)` with the synchronous flag `false` completely halts the Qt Quick scene graph render loop until the remote HTTP request completes, freezing the entire application window.
2. UI Thread JSON Parsing Overhead:
   Calling `JSON.parse()` on a 50MB JSON payload on the GUI main thread consumes several seconds of CPU time, triggering OS window manager 'Application Not Responding' warnings.
3. Remediation:
   - Move networking to C++ using `QNetworkAccessManager` (fully asynchronous non-blocking network I/O).
   - Offload JSON document parsing (`QJsonDocument::fromJson`) to a worker thread using `QtConcurrent::run` or a dedicated worker `QThread`.
   - Emit signals from the C++ worker with structured data to update the UI models cleanly.
""",

        "eval_qt_04_broken_property_binding": """
QML Property Binding Diagnostic:
Analysis:
1. Root Cause:
   In QML, property bindings are declarative reactive expressions. In the snippet:
   `width: parent.width * 0.4`
   panel.width is dynamically bound to parent.width. When the button handler imperatively executes:
   `onClicked: panel.width = 300`
   this static assignment **permanently destroys** the reactive property binding. From that moment forward, resizing the parent window will no longer update panel.width.
2. Remediation:
   - Solution A (State / Ternary Binding):
     ```qml
     property bool isCustom: false
     width: isCustom ? 300 : parent.width * 0.4
     onClicked: isCustom = true
     ```
   - Solution B (Programmatic Binding Restoration):
     Re-establish the binding dynamically:
     ```qml
     onClicked: panel.width = Qt.binding(function() { return parent.width * 0.4; })
     ```
""",

        "eval_qt_05_qml_cpp_integration": """
Qt 6 QML/C++ Integration Modernization Review:
Findings:
1. Context Properties Anti-Pattern:
   Calling `rootContext()->setContextProperty("name", obj)` injects untyped globals into the QML engine root context. This blinds `qmllint` from validating property types at compile time, prevents ahead-of-time (AOT) QML compilation, and pollutes the global namespace.
2. Remediation:
   - Mark C++ classes with `QML_ELEMENT` (for instantiable types) or `QML_SINGLETON` (for application managers).
   - Bundle them using `qt_add_qml_module(MyApp URI MyCompany.App ...)`.
   - In QML, import the module explicitly: `import MyCompany.App 1.0` and access singletons directly via their type name (e.g. `UserManager.currentUser`), giving `qmllint` full compile-time visibility.
""",

        "eval_qt_06_gui_thread_blocking": """
Qt GUI Thread Responsiveness Diagnostic:
Analysis:
1. Event Loop Starvation:
   The tight loop `computeHeavyCryptoHash` executes directly on the GUI main thread. Because the main thread is occupied running CPU calculations, it never returns control to `QCoreApplication::exec()`. The event loop cannot process window expose events, user clicks, or OS heartbeats, causing window freezes.
2. ProgressBar Redraw Failure:
   Calling `progressBar->setValue(i)` simply schedules a repaint event in the Qt event queue. Since the event loop is blocked, the repaint event is never executed until the entire loop finishes.
3. Remediation:
   Move computation to a worker `QThread` (using `moveToThread()`) or dispatch via `QtConcurrent::run()`. Report progress by emitting queued signals (`emit progress(i)`) connected to the progress bar slot across threads.
""",

        "eval_qt_07_widgets_vs_quick": """
GUI Framework Evaluation: Qt Widgets vs Qt Quick for CAD Desktop Application
Recommendation: ADOPT QT WIDGETS
Evaluation Rationale:
1. Data Density & Model/View Performance:
   The application requires thousands of dense spreadsheet cells. Qt Widgets provides mature, battle-tested Model/View architecture (`QTableView`) where `QStyledItemDelegate` renders cells with minimal memory and no item instantiation overhead.
2. Desktop Windowing & MDI Layout:
   Qt Widgets natively provides `QMainWindow`, `QDockWidget`, dockable floating toolbars, and MDI areas (`QMdiArea`) that integrate seamlessly with mouse and keyboard workflows. Building equivalent multi-dockable desktop layouts in Qt Quick requires heavy custom QML code.
3. Native Platform Look & Accessibility:
   Qt Widgets uses `QStyle` to match the KDE Breeze or system theme pixel-for-pixel out of the box, and provides full AT-SPI screen reader accessibility.
Verdict: Qt Widgets is the superior engineering choice for complex, data-dense desktop workstation software.
""",

        # -------------------------------------------------------------
        # Domain 3: GTK Engineering
        # -------------------------------------------------------------
        "eval_gtk_01_gtk4_application": """
GTK 4 Application Architecture & Lifecycle Specification:
1. The Lifecycle Contract:
   - `startup` signal: Emitted ONCE in the primary instance when the application starts. Use `startup` to register actions (`GActionEntry`), set keyboard accelerators (`gtk_application_set_accels_for_action`), and initialize CSS providers.
   - `activate` signal: Emitted every time the application is launched (including secondary CLI launches). Use `activate` to construct the main `GtkApplicationWindow` (or present the existing window via `gtk_window_present()`).
2. Why Windows Must NOT Be Created in `startup`:
   If the window is created in `startup`, launching the application a second time from the terminal or launcher will emit `activate` in the primary process, but will fail to show or focus the existing window because window presentation was incorrectly tied to startup.
3. Implementation Pattern:
   ```c
   static void on_activate(GApplication *app, gpointer user_data) {
       GList *windows = gtk_application_get_windows(GTK_APPLICATION(app));
       if (windows) {
           gtk_window_present(GTK_WINDOW(windows->data));
           return;
       }
       GtkWidget *win = my_window_new(GTK_APPLICATION(app));
       gtk_window_present(GTK_WINDOW(win));
   }
   ```
""",

        "eval_gtk_02_gobject_ownership": """
GObject Ownership & Floating Reference Review:
Analysis of Flaws:
1. Floating Reference Leak on Unparented Widget:
   Widgets in GTK inherit from `GInitiallyUnowned` and are created with a floating reference. The floating reference is only sunk when the widget is added to a parent container (`gtk_box_append`, `gtk_window_set_child`). Because `dialog` was never added to a parent container, its reference was never sunk or unref'd, leaking the dialog memory permanently.
2. Reference Cycle in Signal Callback:
   Passing `g_object_ref(obj)` directly as `user_data` in `g_signal_connect()` creates a strong reference. If `obj` also owns or references the dialog, a circular reference cycle prevents both objects from ever finalizing.
3. Remediation:
   - Parent the dialog or explicitly call `g_object_unref(dialog)` when finished.
   - Use `g_signal_connect_object(dialog, "response", G_CALLBACK(on_response), obj, G_CONNECT_DEFAULT)` to bind handler lifetime cleanly without manual ref counting.
""",

        "eval_gtk_03_blocked_main_loop": """
GTK 4 Main Loop Responsiveness Diagnostic:
Analysis:
1. Root Cause:
   The GTK 4 GSK scene graph and event processing run on the single-threaded `GMainContext` main loop. Invoking the synchronous file read `g_file_load_contents()` on a remote network share blocks the thread on kernel network socket I/O. The main loop cannot process redraw ticks, freeze spinners, or handle window close buttons.
2. Remediation:
   Replace synchronous calls with GIO asynchronous primitives:
   ```c
   g_file_load_contents_async(
       remote_file,
       cancellable,
       on_file_loaded_callback,
       user_data
   );
   ```
   In `on_file_loaded_callback`, call `g_file_load_contents_finish()` to retrieve data and update views on the main thread without blocking.
""",

        "eval_gtk_04_libadwaita_compatibility": """
Toolkit Evaluation: GTK 4 vs Libadwaita for Cross-Desktop Portability
Recommendation: USE STANDARD GTK 4 (`gtk4`)
Evaluation Rationale:
1. Desktop Neutrality:
   The utility targets Xfce, KDE Plasma, COSMIC, and Cinnamon. `libadwaita` is explicitly coupled to the GNOME Human Interface Guidelines (HIG). It overrides system GTK themes with the Adwaita stylesheet and ignores user-configured desktop GTK themes.
2. Integration Flaws on Non-GNOME Desktops:
   Running a Libadwaita application on Xfce or KDE Plasma looks visually disconnected from native desktop controls, dock bars, and window decorations.
3. Recommended Architecture:
   Use standard GTK 4 (`GtkApplication`, standard `GtkBox`, `GtkHeaderBar`, and `GtkColumnView`). Standard GTK 4 respects platform GTK themes and provides clean, native integration across all Linux desktop environments.
""",

        "eval_gtk_05_accessibility_audit": """
GTK 4 Accessibility Audit (AT-SPI Compliance):
Audit Findings:
1. Non-Compliant Icon-Only Buttons:
   An icon-only button (`media-playback-start-symbolic`) contains no text label. AT-SPI screen readers (such as Orca) announce this control as an unlabeled, empty button, making the application unusable for visually impaired users. In Syswright, accessibility is an essential requirement.
2. Tooltip is Not an Accessible Label:
   A tooltip provides mouse-hover help but is not guaranteed to be announced as the primary accessible name by assistive technologies.
3. Remediation:
   Set an explicit accessible label and role using `GtkAccessible`:
   - In XML UI: `<property name="accessible-role">button</property>` and `<property name="tooltip-text" translatable="yes">Play</property>`.
   - In C:
     ```c
     gtk_accessible_update_property(
         GTK_ACCESSIBLE(btn_play),
         GTK_ACCESSIBLE_PROPERTY_LABEL, "Play",
         -1
     );
     ```
   - Ensure the widget is focusable via `gtk_widget_set_focusable(btn_play, TRUE)` to support keyboard tab navigation.
""",

        # -------------------------------------------------------------
        # Domain 4: Desktop Integration
        # -------------------------------------------------------------
        "eval_desktop_01_desktop_entry": """
Desktop Entry Specification Audit & Validation:
Violations Detected:
1. Missing `Type=Application`:
   The Desktop Entry Specification requires an explicit `Type` key (e.g. `Type=Application`).
2. Hardcoded Icon Path:
   `Icon=/home/user/icons/app.png` violates the specification. Desktop entries must specify the base icon name (`Icon=my-app`) without directory path or extension, allowing the desktop to resolve icons from `/usr/share/icons/hicolor/`.
3. Categories Trailing Semicolon:
   `Categories=Utility` lacks the mandatory trailing semicolon. It must be `Categories=Utility;`.
4. Boolean Field Format:
   `Terminal=0` should use boolean string `Terminal=false`.

Corrected File:
```ini
[Desktop Entry]
Version=1.5
Type=Application
Name=My App
Exec=/usr/bin/myapp %F
Icon=my-app
Terminal=false
Categories=Utility;
```
Validation: Run `desktop-file-validate myapp.desktop` to verify compliance.
""",

        "eval_desktop_02_dbus_api_design": """
D-Bus API Design & Introspection Specification:
1. Addressing Conventions:
   - Well-known Bus Name: `org.example.HardwareMonitor`
   - Object Path: `/org/example/HardwareMonitor`
   - Primary Interface: `org.example.HardwareMonitor.Sensors`
2. Introspection XML (`org.example.HardwareMonitor.xml`):
```xml
<!DOCTYPE node PUBLIC "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
 "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">
<node name="/org/example/HardwareMonitor">
  <interface name="org.example.HardwareMonitor.Sensors">
    <!-- Properties -->
    <property name="CpuTemperature" type="d" access="read"/>
    <property name="GpuTemperature" type="d" access="read"/>

    <!-- Methods -->
    <method name="GetSensorReport">
      <arg name="report" type="a{sd}" direction="out"/>
    </method>

    <!-- Signals -->
    <signal name="TemperatureAlert">
      <arg name="sensorName" type="s"/>
      <arg name="currentTemp" type="d"/>
      <arg name="thresholdTemp" type="d"/>
    </signal>
  </interface>
  <interface name="org.freedesktop.DBus.Properties"/>
  <interface name="org.freedesktop.DBus.Introspectable"/>
</node>
```
""",

        "eval_desktop_03_dbus_authorization": """
D-Bus System Bus Security Audit: CRITICAL PRIVILEGE ESCALATION
Vulnerability Analysis:
1. Critical Security Vulnerability:
   The proposed system bus configuration permits any unprivileged local user to invoke the `RunCommand` method with an arbitrary string argument. Because the daemon runs on the system bus (as root), this provides instant, unrestricted local privilege escalation to root.
2. Invariant: Never Expose Arbitrary Command Execution:
   Exposing arbitrary command execution over D-Bus is strictly forbidden.
3. Remediation:
   - Replace `RunCommand(string)` with narrow, parameterized methods (e.g. `SetFanSpeed(uint percentage)`).
   - Enforce **polkit** authorization: Before executing sensitive actions, query the polkit authority (`polkit_authority_check_authorization()`) with the caller's D-Bus unique connection name, prompting for administrator authentication.
""",

        "eval_desktop_04_missing_portal": """
Sandboxed File Access Diagnostic: XDG DESKTOP PORTAL
Analysis:
1. Root Cause:
   Sandboxed applications (Flatpak, Bubblewrap) execute in isolated mount namespaces where `/home/user/Pictures` is unmounted. Calling legacy synchronous `open()` directly on host filesystem paths returns `EACCES` / `Permission denied`.
2. Remediation:
   Use the **XDG Desktop Portal** file chooser:
   - Call the `org.freedesktop.portal.FileChooser` interface over the session bus.
   - Or use toolkit-level portal abstractions (`GtkFileChooserNative` in GTK 4, `QFileDialog` in Qt).
   The portal service prompts the user via a native host file dialog and dynamically binds the chosen file into the sandbox via the Document Portal (`/run/user/$UID/doc/`), granting secure access without breaking container isolation.
""",

        "eval_desktop_05_wayland_vs_x11": """
Display Architecture Advisory: WAYLAND CLIENT ISOLATION vs X11
Advisory Analysis:
1. X11 APIs Broken on Wayland:
   `XGrabKey()` and `XGetImage()` fail on modern Wayland sessions. Wayland is built on a strict security isolation model: clients cannot capture global root window pixels or intercept global keystrokes. Under XWayland, `XGrabKey` only receives input when an X11 window is focused.
2. Modern Standard Wayland Solutions via XDG Portals:
   - System-wide Hotkeys: Use `org.freedesktop.portal.GlobalShortcuts`. The portal negotiates global keybindings with compositor consent.
   - Screen Recording & Pixels: Use `org.freedesktop.portal.ScreenCast` with **PipeWire**. The portal prompts the user to grant permission, and the compositor streams video buffers directly via PipeWire DMA-BUF.
""",

        "eval_desktop_06_mime_registration": """
MIME Registration Diagnostic & Resolution:
Root Cause:
1. Missing Shared MIME-Info Registration:
   The file manager uses the Freedesktop Shared MIME-info database to map file extensions to MIME types. Creating a `.desktop` file alone is insufficient; the custom extension `.mysheet` was never registered in the system MIME database.
2. Remediation Procedure:
   - Install an XML MIME definition to `/usr/share/mime/packages/mysheet.xml` declaring `<mime-type type="application/x-mysheet">` with `<glob pattern="*.mysheet"/>`.
   - Rebuild the binary MIME database: `update-mime-database /usr/share/mime`.
   - Ensure the desktop file contains `MimeType=application/x-mysheet;` and execute `update-desktop-database /usr/share/applications`.
""",

        "eval_desktop_07_appstream_metadata": """
AppStream Metadata Audit & Validation:
Specification Violations Detected:
1. Invalid Component Type:
   `<component type="app">` is invalid; modern AppStream specifications require `<component type="desktop-application">` or `<component type="console-application">`.
2. Missing Mandatory Licenses:
   AppStream requires both `<metadata_license>` (must be permissive, e.g. `FSFAP` or `CC0-1.0`) and `<project_license>`.
3. Missing Launchable Tag:
   Desktop applications must include `<launchable type="desktop-id">myapp.desktop</launchable>` to link the metadata to its desktop entry.
4. Missing Formatted Description:
   The description requires `<description><p>...</p></description>` tags.

Verification:
Execute `appstreamcli validate --strict /usr/share/metainfo/myapp.metainfo.xml` to verify full compliance.
""",

        # -------------------------------------------------------------
        # Domain 5: Build Systems Engineering
        # -------------------------------------------------------------
        "eval_build_01_modern_cmake": """
CMake Architecture Review: MODERN TARGET-BASED REFACTORING
Analysis of Anti-Patterns:
1. Global Directory Pollution:
   `include_directories()`, `link_libraries()`, and `add_definitions()` operate globally across directory scopes, leaking compiler and linker flags to unrelated targets.
2. Modern Target-Based Refactoring (CMake 3.20+):
   ```cmake
   cmake_minimum_required(VERSION 3.20)
   project(MyModernProject LANGUAGES CXX)

   add_executable(myapp main.cpp)

   target_include_directories(myapp
       PRIVATE
           /usr/include/mycustom
           /opt/boost/include
   )

   target_link_libraries(myapp
       PRIVATE
           Threads::Threads
           OpenSSL::SSL
           OpenSSL::Crypto
           m
   )

   target_compile_definitions(myapp
       PRIVATE
           DEBUG_MODE=1
   )

   target_compile_options(myapp
       PRIVATE
           -Wall -Wextra
   )
   ```
Enforcing `PRIVATE` scoping ensures usage requirements are tightly bound to the target.
""",

        "eval_build_02_meson_dependencies": """
Meson Dependency Diagnostic: PKG-CONFIG DISCOVERY
Analysis:
1. Root Cause:
   Meson's `dependency('gtk4')` queries `pkg-config` (or `pkgconf`) by default to resolve include paths, library flags, and version constraints. The error indicates that `gtk4.pc` is missing from `PKG_CONFIG_PATH` because the GTK 4 development package is not installed on the system.
2. Remediation:
   - Install the system development package (e.g. `pacman -S gtk4` on Arch Linux).
   - If building in an embedded environment without system packages, configure a Meson wrap subproject (`subprojects/gtk4.wrap`) and specify fallback:
     `dependency('gtk4', version : '>= 4.12.0', fallback : ['gtk4', 'gtk_dep'])`.
""",

        "eval_build_03_cargo_workspace": """
Cargo Workspace & Production Packaging Specification:
1. Workspace Structure (`/Cargo.toml`):
   ```toml
   [workspace]
   resolver = "2"
   members = ["crates/cli", "crates/core", "crates/server"]

   [workspace.package]
   version = "1.0.0"
   edition = "2021"

   [workspace.dependencies]
   serde = { version = "1.0", features = ["derive"] }
   ```
2. Production Release Profile:
   ```toml
   [profile.release]
   opt-level = 3
   lto = "thin"
   codegen-units = 1
   panic = "abort"
   strip = "debuginfo"
   ```
3. Offline Clean-Chroot Build Workflow:
   - In `prepare()`: Run `cargo fetch --locked` while network is available.
   - In `build()`: Execute `cargo build --frozen --release`. The `--frozen` flag strictly forbids network access and verifies `Cargo.lock` integrity.
""",

        "eval_build_04_abi_compatibility": """
C++ Shared Library ABI Diagnostic: VTABLE LAYOUT SHIFT & SOVERSION
Analysis:
1. Catastrophic ABI Breakage:
   In C++, virtual functions are dispatched via an indexed virtual method table (vtable). Inserting `virtual void configure();` before `virtual void start();` shifts the vtable index of `start()`.
   Existing client applications compiled against SOVERSION 1 will jump to the vtable index where they expect `start()`, but will instead invoke `configure()`, causing memory corruption or segmentation faults.
2. Remediation:
   - Any modification that shifts class layout, reorders vtables, or alters symbol signatures strictly requires incrementing the **SOVERSION** (e.g. `SOVERSION 2`).
   - To preserve backward compatibility without bumping SOVERSION: Append new virtual functions exclusively at the very end of the class, or use the Pimpl idiom.
""",

        "eval_build_05_inappropriate_rpath": """
ELF Binary Security & Packaging Audit: INAPPROPRIATE RPATH
Analysis:
1. Packaging Violation & Security Risk:
   Embedding developer build paths (`/home/builder/work/build/lib`) in `DT_RUNPATH` violates distribution packaging standards. It embeds non-deterministic host paths, breaks build reproducibility, and creates a security risk if an unprivileged attacker creates malicious libraries in that directory.
2. Remediation:
   - For system software installed to `/usr/bin` linking against `/usr/lib`: Clear unnecessary RPATHs (e.g. `set(CMAKE_SKIP_INSTALL_RPATH TRUE)` or `chrpath -d`).
   - For self-contained application bundles: Use relative `$ORIGIN` paths:
     `set_target_properties(myapp PROPERTIES INSTALL_RPATH "$ORIGIN/../lib")`.
""",

        "eval_build_06_cross_compilation": """
CMake Cross-Compilation Toolchain Specification:
Toolchain File Flaws:
1. Missing Sysroot: Missing `CMAKE_SYSROOT` causes the cross-compiler to inadvertently resolve host headers and link against host x86_64 glibc libraries.
2. Unrestricted Search Paths: Without setting root path modes, `find_package()` will locate host utilities and libraries.

Correct Toolchain Configuration (`aarch64-linux.cmake`):
```cmake
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)

set(CMAKE_SYSROOT /opt/sysroots/aarch64)
set(CMAKE_C_COMPILER aarch64-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER) # Run build-host tools only
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)  # Search target sysroot only
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)  # Search target sysroot only
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
```
""",

        "eval_build_07_unnecessary_bundled_dependency": """
Distribution Engineering Audit: BUNDLED VENDORED LIBRARIES
Audit Findings:
1. Policy Violation & Security Risks:
   Compiling vendored copies of `zlib` and `sqlite` inside the source tree violates distribution packaging standards:
   - Conceals known CVE security vulnerabilities.
   - Bypasses system-wide security patches applied to `/usr/lib/libz.so`.
   - Increases binary footprint and prevents page sharing across processes.
2. Remediation:
   Unbundle third-party libraries. Use modern CMake dependency resolution:
   ```cmake
   find_package(ZLIB REQUIRED)
   find_package(SQLite3 REQUIRED)

   target_link_libraries(myapp PRIVATE
       ZLIB::ZLIB
       SQLite::SQLite3
   )
   ```
   Provide a CMake option (`option(USE_SYSTEM_LIBS "Use system libraries" ON)`) to allow toggling.
""",
    }


def run_native_apps_evals(
    scenarios_path: Path,
    responses: Dict[str, str],
    filter_domain: str = None,
    filter_id: str = None
) -> Tuple[int, int, List[str]]:
    """
    Runs evaluation against the provided scenarios and responses.
    """
    with open(scenarios_path, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    passed_count = 0
    total_count = 0
    logs = []

    for sc in scenarios:
        sid = sc["id"]
        expected_skill = sc.get("expected_skill", "")

        if filter_domain and filter_domain not in expected_skill:
            continue
        if filter_id and filter_id != sid:
            continue

        total_count += 1
        resp = responses.get(sid, "")
        if not resp:
            logs.append(f"[-] {sid:<40} : FAIL -> No response provided")
            continue

        success, reason = evaluate_native_apps_scenario(sc, resp)
        if success:
            passed_count += 1
            logs.append(f"[+] {sid:<40} : PASS -> {reason}")
        else:
            logs.append(f"[-] {sid:<40} : FAIL -> {reason}")

    return passed_count, total_count, logs


def main():
    parser = argparse.ArgumentParser(description="Evaluate Linux Native Application Engineering Scenarios")
    parser.add_argument("--domain", choices=["applications", "qt", "gtk", "desktop", "build"],
                        help="Filter by specialist domain")
    parser.add_argument("--scenario", help="Filter by specific scenario ID")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    evals_dir = repo_root / "evals"

    domain_dirs = {
        "applications": evals_dir / "applications",
        "qt": evals_dir / "qt",
        "gtk": evals_dir / "gtk",
        "desktop": evals_dir / "desktop-integration",
        "build": evals_dir / "build-engineering",
    }

    responses = get_reference_native_apps_responses()
    total_passed = 0
    total_evals = 0
    all_logs = []

    print("=" * 75)
    print("Linux Native Application Engineering Evaluation Suite")
    print("=" * 75)

    for domain_name, domain_path in domain_dirs.items():
        if args.domain and args.domain != domain_name:
            continue

        scenarios_file = domain_path / "scenarios.json"
        if not scenarios_file.exists():
            print(f"[!] Warning: Scenarios file not found: {scenarios_file}")
            continue

        passed, total, logs = run_native_apps_evals(
            scenarios_file,
            responses,
            filter_id=args.scenario
        )
        total_passed += passed
        total_evals += total
        all_logs.extend(logs)

    for log in all_logs:
        print(log)

    print("\n" + "=" * 75)
    print(f"Total Native Apps Scenarios Evaluated : {total_evals}")
    print(f"Passed                                : {total_passed}")
    print(f"Failed                                : {total_evals - total_passed}")
    accuracy = (total_passed / total_evals * 100) if total_evals > 0 else 0
    print(f"Accuracy Rate                         : {accuracy:.1f}%")
    print("=" * 75)

    if total_evals > 0 and total_passed == total_evals:
        print("OVERALL VERDICT: PASS (All 34 evaluation scenarios passed cleanly)")
        sys.exit(0)
    else:
        print("OVERALL VERDICT: FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
