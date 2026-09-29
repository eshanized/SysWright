# Cargo Workspaces, Profiles & Packaging

## 1. Scope & The Cargo Build Engine

Cargo is the official build system and package manager for Rust. It orchestrates compilation, manages dependencies, executes test suites, and generates release artifacts.

---

## 2. Multi-Crate Cargo Workspaces

For large applications with shared internal libraries or modular architectures:
```toml
# /Cargo.toml (Workspace Root)
[workspace]
resolver = "2"
members = [
    "crates/cli",
    "crates/core",
    "crates/daemon",
]

[workspace.package]
version = "1.0.0"
edition = "2021"
license = "MIT OR Apache-2.0"
repository = "https://github.com/example/myproject"

[workspace.dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1.35", features = ["rt-multi-thread", "macros"] }
thiserror = "1.0"
```

---

## 3. Profiles for Release Optimization

Configure release profiles in the workspace root `Cargo.toml`:
```toml
[profile.release]
opt-level = 3
lto = "thin"         # Link-Time Optimization for performance
codegen-units = 1    # Maximizes optimization across crate boundaries
panic = "abort"      # Strips unwinding tables, reducing binary size
strip = "debuginfo"  # Removes debug symbols from final release executable
```

---

## 4. Offline & Distribution Packaging (`--frozen`)

When building packages in isolated environments (e.g. clean chroots):
- **Pre-fetch in prepare()**: Run `cargo fetch --locked` while network access is permitted.
- **Build with `--frozen`**: In `build()`, compile with `cargo build --frozen --release`. The `--frozen` flag guarantees that Cargo will not access the network and will fail immediately if `Cargo.lock` does not match dependencies.
