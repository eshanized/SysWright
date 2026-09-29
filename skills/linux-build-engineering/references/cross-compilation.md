# Cross-Compilation Toolchains & Sysroots

## 1. Scope & Cross-Compilation Concepts

Cross-compilation compiles software on a **host** system (e.g. x86_64 workstation) targeting a different **target** architecture (e.g. AArch64 or RISC-V embedded board).

### Key Terms:
- **Build Host**: Machine executing the compiler (e.g. `x86_64-pc-linux-gnu`).
- **Target Host**: Machine executing the final compiled binaries (e.g. `aarch64-unknown-linux-gnu`).
- **Sysroot**: A directory tree containing target headers (`/usr/include`) and libraries (`/usr/lib`) for the target architecture (`--sysroot=/path/to/sysroot`).

---

## 2. Cross-Compilation with CMake

Create a toolchain file `aarch64-toolchain.cmake`:
```cmake
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)

set(CMAKE_SYSROOT /opt/sysroots/aarch64)

set(CMAKE_C_COMPILER aarch64-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER) # Run build-host tools only
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)  # Link target-sysroot libraries only
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)  # Include target-sysroot headers only
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
```
Invoked via:
```bash
cmake -B build -G Ninja --toolchain aarch64-toolchain.cmake
```

---

## 3. Cross-Compilation with Cargo

Rust natively supports cross-compilation via target triples:
```bash
# Add target standard library
rustup target add aarch64-unknown-linux-gnu

# Build for target architecture using target linker
CARGO_TARGET_AARCH64_UNKNOWN_LINUX_GNU_LINKER=aarch64-linux-gnu-gcc \
cargo build --release --target aarch64-unknown-linux-gnu
```
