# Kbuild, Kconfig & Kernel Build Engineering Reference

## 1. Scope

This document details the configuration, build systems, out-of-tree module compilation, and compiler toolchains used in the Linux kernel.

---

## 2. Kconfig Configuration System

The kernel uses Kconfig to declare dependencies and generate `.config`:

### 2.1 Kconfig Directives
- `bool`: Tristate disabled (`n`) or built-in (`y`).
- `tristate`: Built-in (`y`), module (`m`), or disabled (`n`).
- `depends on <SYM>`: Direct dependency requirement. Symbol is hidden unless `<SYM>` is satisfied.
- `select <SYM>`: Forces `<SYM>` to enabled. **Warning**: Does not resolve `<SYM>`'s dependencies; misuse causes invalid configurations.
- `imply <SYM>`: Weak dependency. Enables `<SYM>` if its dependencies permit, but allows user override.

### 2.2 Managing Configurations
```bash
# Generate architecture default config
make defconfig

# Interactive terminal menu
make menuconfig

# Validate and apply non-interactive updates
make olddefconfig

# Merge modular configuration fragments
./scripts/kconfig/merge_config.sh .config arch/x86/configs/kvm_guest.config fragment.config
```

---

## 3. Kbuild Build System

### 3.1 Kernel In-Tree Compilation
```bash
# Standard parallel compilation
make -j$(nproc) bzImage modules

# Compile specific subsystem or file
make drivers/net/ethernet/intel/e1000e/
make fs/ext4/ext4.o
```

### 3.2 Out-of-Tree External Module Compilation
To compile an external kernel module against the currently running kernel:

```makefile
# Makefile for external module
obj-m += my_driver.o
my_driver-objs := main.o helper.o

KDIR ?= /usr/lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

default:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
```

- Requires `linux-headers` installed matching the target kernel release (`uname -r`).

---

## 4. Compiler Toolchains & Modern Hardening

### 4.1 GCC vs Clang/LLVM
Linux supports building with LLVM toolchains:
```bash
# Build kernel entirely with Clang/LLVM
make CC=clang LLVM=1 -j$(nproc)
```
- `LLVM=1`: Uses `clang`, `ld.lld`, `llvm-ar`, `llvm-objcopy`, and `llvm-nm`.

### 4.2 Modern Build Hardening & Features
- **LTO (Link-Time Optimization)**:
  - `CONFIG_LTO_CLANG_THIN=y`: Enables ThinLTO with Clang, enabling cross-translation-unit optimizations.
  - `CONFIG_LTO_CLANG_FULL=y`: Full LTO (higher link memory overhead).
- **BTF (BPF Type Format)**:
  - `CONFIG_DEBUG_INFO_BTF=y`: Embeds compact deduplicated DWARF type information into `.BTF` ELF sections using `pahole`. Essential for modern eBPF and CO-RE (Compile Once - Run Everywhere).

---

## 5. Authoritative References

- [Kbuild: the Linux Kernel Build System](https://docs.kernel.org/kbuild/kbuild.html)
- [Kconfig Language](https://docs.kernel.org/kbuild/kconfig-language.html)
- [Building the Kernel with Clang/LLVM](https://docs.kernel.org/kbuild/llvm.html)
