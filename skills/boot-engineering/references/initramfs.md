# Initramfs Engineering & mkinitcpio Reference

## 1. Scope

This document details early userspace architecture, initramfs generators (`mkinitcpio`, `dracut`), hook hierarchies (systemd-based vs busybox-based), microcode inclusion, and storage assembly.

---

## 2. Initramfs Architecture

The initramfs (initial RAM filesystem) is a cpio archive unpacked into rootfs by the kernel. Its primary mission is to load storage drivers, unlock encrypted block devices, assemble software RAID or LVM, mount the real root filesystem to `/new_root`, and execute `switch_root`.

---

## 3. mkinitcpio Configuration (`/etc/mkinitcpio.conf`)

`mkinitcpio` is the standard modular initramfs generator on Arch Linux:

### 3.1 Hook Hierarchies: Systemd vs. Busybox
Arch supports two mutually exclusive hook architectures:

| Hook Paradigm | Sample HOOKS Array in `/etc/mkinitcpio.conf` | Key Characteristics |
|:---|:---|:---|
| **systemd-based** (Recommended) | `HOOKS=(base systemd autodetect modconf kms keyboard sd-vconsole block sd-encrypt sd-lvm2 filesystems fsck)` | Uses systemd inside early userspace. Supports `/etc/crypttab`, TPM2 unlocking (`systemd-cryptenroll`), parallel device discovery. |
| **busybox-based** (Legacy) | `HOOKS=(base udev autodetect modconf kms keyboard keymap consolefont block encrypt lvm2 filesystems fsck)` | Uses busybox shell scripts. Relies on kernel cmdline arguments (`cryptdevice=UUID=...:root`). |

*Strict Invariant*: Never mix `systemd` and `udev` or `sd-encrypt` and `encrypt` hooks in the same `HOOKS` array.

### 3.2 Modules Array (`MODULES=()`)
Lists kernel modules that must be loaded before hooks execute (e.g. storage drivers or GPU drivers for early KMS):
```ini
MODULES=(nvme btrfs crc32c-intel)
```

### 3.3 Regenerating Initramfs Images
```bash
# 1. Regenerate all presets (/etc/mkinitcpio.d/*.preset)
mkinitcpio -P

# 2. Regenerate specific kernel preset
mkinitcpio -p linux

# 3. Generate a Unified Kernel Image (UKI) directly
mkinitcpio -p linux -U /efi/EFI/Linux/arch-linux.efi
```

---

## 4. CPU Microcode Updates

CPU microcode updates must be applied before kernel hardware initialization to patch processor errata:
- **Intel CPUs**: Requires `intel-ucode` package (`/boot/intel-ucode.img`).
- **AMD CPUs**: Requires `amd-ucode` package (`/boot/amd-ucode.img`).
- Must be declared as the first initrd image in the bootloader.

---

## 5. Authoritative References

- [mkinitcpio(8) Manual](https://man.archlinux.org/man/mkinitcpio.8.en)
- [mkinitcpio.conf(5) Manual](https://man.archlinux.org/man/mkinitcpio.conf.5.en)
- [ArchWiki: mkinitcpio](https://wiki.archlinux.org/title/Mkinitcpio)
- [ArchWiki: Microcode](https://wiki.archlinux.org/title/Microcode)
