# Storage Diagnostics, Recovery & Data Protection Reference

## 1. Scope

This document details storage health inspection (SMART, NVMe), filesystem verification, repair hazards, and strict data protection invariants.

---

## 2. Strict Data Protection Invariants

Storage operations are among the highest-risk actions in systems engineering. Data loss is irreversible.
1. **Zero Silent Destructive Commands**: Never execute `mkfs`, `wipefs`, `dd` to raw block devices, or partitioning tools (`fdisk`, `parted`, `gdisk`) autonomously.
2. **Never Run `fsck` on a Mounted Filesystem**: Running `fsck` or `e2fsck` on a filesystem mounted read-write corrupts directory trees and superblocks. Always unmount (`umount`) or remount read-only (`mount -o remount,ro`) first.
3. **Caution with `btrfs check --repair`**: The Btrfs wiki explicitly warns against running `--repair` unless instructed by a kernel filesystem developer, as it can cause catastrophic data truncation on complex B-tree corruptions. Use `btrfs restore` or read-only checks first.

---

## 3. Storage Diagnostics Commands

```bash
# 1. Print block device hierarchy, filesystems, and mount points
lsblk -f

# 2. Inspect filesystem mount options and active states
findmnt

# 3. Check NVMe controller health and wear
nvme smart-log /dev/nvme0n1

# 4. Check SATA/SAS SMART health status
smartctl -H /dev/sda
smartctl -a /dev/sda
```

---

## 4. Btrfs Snapshot & Recovery Procedures

```bash
# 1. Create a read-only snapshot before system changes
btrfs subvolume snapshot -r / /snapshots/root-pre-update

# 2. Recover read-only corrupted data to external disk without mounting
btrfs restore -v /dev/nvme0n1p2 /mnt/external/recovery/
```

---

## 5. Authoritative References

- [smartctl(8) Manual](https://man.archlinux.org/man/smartctl.8)
- [nvme(1) Manual](https://man.archlinux.org/man/nvme.1)
- [e2fsck(8) Manual](https://man.archlinux.org/man/e2fsck.8)
- [btrfs-check(8) Manual](https://man.archlinux.org/man/btrfs-check.8)
