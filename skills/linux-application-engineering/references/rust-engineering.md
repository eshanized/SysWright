# Rust Systems Engineering for Linux

## 1. Scope & Core Tenets

Rust provides memory safety without garbage collection, making it the preferred language for modern Linux CLI utilities, daemons, and system services. This reference defines production engineering practices adhering to the official Rust API Guidelines and Linux system programming standards:
- **Zero-Cost Abstractions with Explicit Boundaries**: Leverage the type system to enforce invariants at compile time.
- **Controlled Unsafe Code**: Contain `unsafe` to audited, minimal primitives with safety contracts documented via `// SAFETY:`.
- **Deliberate Async vs Synchronous Runtime Selection**: Never introduce Tokio or asynchronous runtimes blindly.

---

## 2. Runtime Selection: Synchronous vs Asynchronous

A common failure mode in AI-generated Rust code is introducing `tokio` and `async` into simple CLI utilities or CPU-bound tools:

| Workload Type | Preferred Architecture | Crates / Rationale |
|---|---|---|
| **CLI File Processor / Batch Tool** | Synchronous + Thread Pool | Standard library `std::fs`, `std::thread`, or `rayon` for data parallelism. Zero runtime overhead, deterministic stack traces, instant cold-start time. |
| **High-Concurrency Network Daemon** | Asynchronous Event Loop | `tokio` (multi-thread flavor) or `smol`. Optimized for thousands of concurrent idle or I/O-waiting sockets. |
| **System Daemon (Low/Medium Traffic)** | Synchronous with `epoll` or Channels | `crossbeam-channel` or `polling` / `mio`. Minimal footprint (<5MB RAM), simple control flow, instant startup. |
| **Real-time / Embedded Linux Agent** | Synchronous Single-threaded | Standard library + `nix` crate. Deterministic latency, no runtime thread spawning. |

```rust
// ANTI-PATTERN: Pulling in full async runtime for simple CLI file copy
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tokio::fs::write("output.txt", b"data").await?; // Unnecessary overhead
    Ok(())
}

// CORRECT: Synchronous standard library for CLI tools
fn main() -> Result<(), std::io::Error> {
    std::fs::write("output.txt", b"data")?;
    Ok(())
}
```

---

## 3. Error Handling Architecture

Production Rust software strictly separates internal error propagation from user-facing error reporting:

1. **Libraries & Internal Modules**:
   - Use `thiserror` to define precise, strongly typed domain error enums.
   - Implement `std::error::Error` for all error types.
   - Never use `unwrap()` or `expect()` in library code unless guarding an unreachable invariant verified by previous assertions.
2. **Applications & Binaries (CLI / Daemons)**:
   - Use `anyhow` or `eyre` at the application entry point (`main.rs`) for rich contextual backtraces (`.context("Failed to load config")`).
   - Map domain errors to clear, standard POSIX exit codes at the application boundary:

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ConfigError {
    #[error("Configuration file not found at '{0}'")]
    NotFound(std::path::PathBuf),
    #[error("Syntax error in config file: {0}")]
    Parse(#[from] toml::de::Error),
    #[error("I/O error reading configuration: {0}")]
    Io(#[from] std::io::Error),
}
```

---

## 4. Linux Systems Integration & FFI Safety

### 4.1 Safe POSIX & Linux Syscalls via `nix`
Instead of writing raw `libc` bindings manually, use the audited, idiomatic `nix` crate for Linux system calls:
- File descriptor safety: `nix::unistd::pipe2`, `nix::fcntl::OFlag`.
- Signal handling: `nix::sys::signal::sigaction`.
- Process management: `nix::sys::wait::waitpid`.

### 4.2 Unsafe Code & FFI Encapsulation
When interacting with C libraries or kernel interfaces:
1. Every `unsafe` block must be preceded by a safety comment explaining why the invariants hold:
   ```rust
   // SAFETY: fd is valid and open for reading; buf points to an initialized slice of length len.
   let bytes_read = unsafe { libc::read(fd, buf.as_mut_ptr() as *mut libc::c_void, len) };
   ```
2. Wrap raw C pointers in safe RAII wrappers implementing `Drop` to ensure deterministic cleanup.
3. Mark exported C ABI functions with `#[no_mangle]` and `extern "C"`.

---

## 5. CLI Tool Engineering with `clap`

Use `clap` (v4+) with the derive API for declarative, accessible CLI interfaces:
- Use `#[command(author, version, about, long_about = None)]`.
- Support `--verbose` / `--quiet` flags integrating with `tracing` / `tracing-subscriber`.
- Detect terminal interactive capability via `std::io::stdout().is_terminal()` (or `is-terminal` crate) before emitting ANSI color codes.
- Provide shell completions using `clap_complete`.

---

## 6. Verification & Quality Checklist

Before completing Rust systems code, verify:
- [ ] `cargo check --workspace --all-targets` passes cleanly.
- [ ] `cargo clippy --workspace --all-targets -- -D warnings` emits zero warnings.
- [ ] `cargo test --workspace` passes all unit and integration tests.
- [ ] `cargo fmt --check` passes with zero formatting diffs.
- [ ] `cargo tree --duplicates` reveals no accidental duplicate major versions of dependencies.
- [ ] No `panic!`, `unwrap()`, or `expect()` in error paths handling external input.
