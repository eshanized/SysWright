# Linux Boot Sequence & Early Userspace Reference

## 1. Scope

This document details the complete end-to-end boot chain from firmware initialization to systemd target activation, isolating failure boundaries at each stage.

---

## 2. The 14-Stage Boot Chain

```mermaid
flowchart TD
    S1["1. Firmware Power-On & POST\n(Motherboard hardware self-test)"]
    S2["2. EFI Boot Manager Execution\n(Reads NVRAM boot entry)"]
    S3["3. Bootloader / Stub Execution\n(systemd-boot or GRUB loads kernel)"]
    S4["4. Kernel Decompression & Init\n(CPU, MMU, ACPI setup)"]
    S5["5. Initramfs Extraction\n(Unpacked to ramfs /rootfs)"]
    S6["6. Early Userspace Daemon Startup\n(udev starts, discovers devices)"]
    S7["7. Root Storage Assembly\n(NVMe, LUKS unlock, LVM scan, RAID sync)"]
    S8["8. Root Filesystem Mounting\n(Mounts target rootfs to /new_root)"]
    S9["9. Switch-Root Execution\n(pivot_root / switch_root to /new_root)"]
    S10["10. Systemd PID 1 Initialization\n(Mounts /sys, /proc, /dev)"]
    S11["11. sysinit.target Activation\n(Applies sysctl, udev settled)"]
    S12["12. basic.target Activation\n(Sockets, paths, timers initialized)"]
    S13["13. network-online.target Activation\n(IP address acquired & verified)"]
    S14["14. multi-user / graphical.target\n(User login and daemons ready)"]

    S1 --> S2 --> S3 --> S4 --> S5 --> S6 --> S7 --> S8 --> S9 --> S10 --> S11 --> S12 --> S13 --> S14
```

---

## 3. Failure Boundary Isolation

| Boot Stage | Observable Failure Symptom | Responsible Component | Diagnostic Tool |
|:---|:---|:---|:---|
| **Firmware / NVRAM** | System reboots into BIOS settings or "No bootable device found". | UEFI NVRAM variable missing or corrupt EFI System Partition. | `efibootmgr -v`, check `/efi/EFI/` |
| **Bootloader** | Error loading kernel or initrd; system hangs before kernel prints output. | Missing `vmlinuz-linux`, corrupted initramfs, or bad ESP path. | Bootloader menu, EFI shell |
| **Early Kernel** | Immediate freeze with black screen, or early kernel panic. | ACPI incompatibility, missing microcode, bad kernel cmdline (`nomodeset`). | `earlycon=`, `earlyprintk=` |
| **Early Userspace** | Drop to emergency rootfs shell (`can't find UUID=...`). | Missing storage controller module, missing LUKS/LVM hook in initramfs. | `blkid`, `ls -l /dev/disk/by-uuid/` |
| **Switch-Root** | `Failed to switch root: Specified switch root path '/new_root' does not seem to be an OS tree`. | `/sbin/init` or `/usr/lib/systemd/systemd` missing on root filesystem. | Mount `/new_root` and inspect |
| **Systemd Startup** | Emergency mode (`systemd: Welcome to emergency mode!`). | A filesystem in `/etc/fstab` failed to mount (corrupted superblock, missing disk). | `journalctl -xb` |

---

## 4. Authoritative References

- [ArchWiki: Arch boot process](https://wiki.archlinux.org/title/Arch_boot_process)
- [Linux Kernel Boot Parameters](https://docs.kernel.org/admin-guide/kernel-parameters.html)
- [systemd Boot Process](https://man.archlinux.org/man/bootup.7)
