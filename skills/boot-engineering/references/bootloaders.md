# Linux Bootloaders Reference

## 1. Scope

This document details the architecture, configuration models, and trade-offs of systemd-boot, GRUB 2, and the Linux EFI Stub.

---

## 2. Bootloader Comparison Matrix

| Bootloader | Firmware Support | Config File Location | Complexity | Auto-Detection |
|:---|:---:|:---|:---:|:---:|
| **systemd-boot** | UEFI only | `/loader/loader.conf` & `/loader/entries/*.conf` | Low (Declarative, minimal) | Automatic Windows & EFI stub discovery |
| **GRUB 2** | BIOS & UEFI | `/boot/grub/grub.cfg` (generated from `/etc/default/grub`) | High (Turing-complete scripting engine) | Requires `os-prober` |
| **EFI Stub** | UEFI only | NVRAM variable command line | None (Kernel is the EFI application) | None (Single kernel directly booted) |
| **rEFInd** | UEFI only | `/boot/refind_linux.conf` | Medium (Graphical, plugin-driven) | Dynamic filesystem scanning |

---

## 3. systemd-boot Configuration Model

systemd-boot is a clean, minimal UEFI boot manager:

### 3.1 Main Configuration (`/efi/loader/loader.conf`)
```ini
default arch.conf
timeout 3
console-mode max
editor no
```

### 3.2 Entry Configuration (`/efi/loader/entries/arch.conf`)
```ini
title   Arch Linux
linux   /vmlinuz-linux
initrd  /intel-ucode.img
initrd  /initramfs-linux.img
options root=UUID=5f8e6d2a-4b3c-4d5e-8f9a-1b2c3d4e5f6a rw quiet
```

- **Microcode Rule**: The CPU microcode image (`intel-ucode.img` or `amd-ucode.img`) must be declared as the **first** `initrd` entry before the main `initramfs-linux.img`.

---

## 4. GRUB 2 Configuration Model

GRUB 2 generates `/boot/grub/grub.cfg` using modular scripts in `/etc/grub.d/` and options in `/etc/default/grub`:

```bash
# In /etc/default/grub:
GRUB_CMDLINE_LINUX_DEFAULT="loglevel=3 quiet"
GRUB_TIMEOUT=5

# Generate configuration:
grub-mkconfig -o /boot/grub/grub.cfg
```

---

## 5. Authoritative References

- [systemd-boot(7) Manual](https://man.archlinux.org/man/systemd-boot.7)
- [bootctl(1) Manual](https://man.archlinux.org/man/bootctl.1)
- [ArchWiki: systemd-boot](https://wiki.archlinux.org/title/systemd-boot)
- [ArchWiki: GRUB](https://wiki.archlinux.org/title/GRUB)
