# Ninja & Make Build Executors

## 1. Build Generator vs Build Executor

A fundamental architectural distinction in Linux build engineering:
- **Build Generators** (CMake, Meson): High-level systems that inspect the host environment, resolve dependencies (`find_package`, `pkg-config`), and evaluate conditional configuration logic.
- **Build Executors** (Ninja, GNU Make): Low-level engines that parse flat dependency graphs and execute compiler commands in parallel.

---

## 2. Ninja: The Standard Modern Executor

Ninja was designed specifically to execute build graphs with maximum possible speed:
- Stripped of conditional statements, globbing, and programming constructs.
- Evaluates dependency timestamps instantaneously without overhead.
- Maximizes multi-core CPU saturation automatically based on available hardware threads (`-j $(nproc)`).
- Both modern CMake (`cmake -G Ninja`) and Meson default to Ninja.

---

## 3. GNU Make: Legacy & Direct Builds

GNU Make remains prevalent in the Linux kernel source tree (`Kbuild`) and minimal legacy utilities:
- **Tab Sensitivity**: Make recipes MUST be indented with actual Tab characters (`\t`), never spaces.
- **Phony Targets**: Always declare non-file targets as `.PHONY`:
  ```makefile
  .PHONY: all clean test
  ```
- **Parallel Builds**: When invoking make in packaging scripts or CLI:
  ```bash
  make -j$(nproc)
  ```
