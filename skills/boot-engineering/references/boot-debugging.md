# Boot Diagnostics, Recovery & Troubleshooting Reference

## 1. Scope

This document details diagnostic procedures for bootloader failures, missing root filesystem devices, corrupted initramfs images, and recovery workflows.

---

## 2. Diagnosing "can't find UUID" / Missing Root Device

### 2.1 Symptom
During boot, the kernel loads the initramfs, but early userspace halts with:
```text
mount: /new_root: can't find UUID=4a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d
You are now being dropped into an emergency shell.
sh: can't access tty; job control turned off
[rootfs ]#
```

### 2.2 Root Cause Analysis
1. **Root device UUID mismatch**: The drive was reformatted or restored, giving it a new UUID, but the bootloader entry still references the old UUID.
2. **Missing storage driver module in initramfs**: The system boots from NVMe, but `nvme` is missing from `MODULES=()` in `/etc/mkinitcpio.conf` and was not autodetected.
3. **Missing LUKS / encryption hook**: The root partition is an encrypted LUKS container, but `HOOKS=()` in `/etc/mkinitcpio.conf` omits `sd-encrypt` or `encrypt`.
4. **Device mapper / LVM not scanned**: Root resides on an LVM logical volume, but `sd-lvm2` or `lvm2` hook was omitted.

### 2.3 Emergency Shell Diagnostic Commands
Inside the initramfs shell:
```bash
# 1. Print block devices and their actual UUIDs
blkid

# 2. Check disk-by-uuid symlinks
ls -l /dev/disk/by-uuid/

# 3. Manually test mounting root filesystem
mount -o ro /dev/disk/by-uuid/<ACTUAL_UUID> /new_root
ls -l /new_root/etc/os-release
```

---

## 3. Recovery Principles & Safeguards

1. **Always Retain Working Fallback Entries**: When configuring bootloaders, always maintain a verified fallback entry (`initramfs-linux-fallback.img`) generated with `autodetect` disabled (contains full set of storage drivers).
2. **Never Delete the Last Bootable Configuration**: Never overwrite a functional bootloader configuration or delete NVRAM entries before a replacement entry is verified.
3. **Arch-Chroot Recovery Workflow**:
   If an unbootable state occurs:
   ```bash
   # From Arch live installation media:
   mount /dev/nvme0n1p2 /mnt
   mount --mkdir /dev/nvme0n1p1 /mnt/efi
   arch-chroot /mnt
   # Edit /etc/mkinitcpio.conf and regenerate:
   mkinitcpio -P
   ```

---

## 4. Authoritative References

- [ArchWiki: General troubleshooting - Boot problems](https://wiki.archlinux.org/title/General_troubleshooting#Boot_problems)
- [ArchWiki: Chroot](https://wiki.archlinux.org/title/Chroot)
