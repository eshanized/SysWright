# Device Mapper & LVM Reference

## 1. Scope

This document details the Device Mapper (DM) kernel framework and Logical Volume Manager (LVM) architectures, volume groups, logical volumes, and online resizing.

---

## 2. Device Mapper Architecture

Device Mapper is a kernel framework that maps physical block devices into virtual block devices (`/dev/mapper/*`). Targets include:
- `linear`: Concatenates physical partitions.
- `striped`: Software striping (RAID 0).
- `crypt`: Cryptographic transparent encryption (LUKS / dm-crypt).
- `snapshot`: Copy-on-Write block level snapshots.
- `thin`: Thin-provisioned storage pools.

---

## 3. LVM (Logical Volume Manager) Hierarchy

```mermaid
flowchart TD
    PHYS["Physical Disks / Partitions\n(/dev/nvme0n1p3, /dev/sda1)"]
    PHYS --> PV["1. Physical Volumes (PV)\n(pvcreate /dev/nvme0n1p3)"]
    PV --> VG["2. Volume Group (VG)\n(vgcreate vg0 /dev/nvme0n1p3)"]

    VG --> LV_ROOT["Logical Volume: root\n(lvcreate -L 50G -n root vg0)"]
    VG --> LV_HOME["Logical Volume: home\n(lvcreate -l 100%FREE -n home vg0)"]

    LV_ROOT --> FS_ROOT["ext4 / XFS Filesystem"]
    LV_HOME --> FS_HOME["ext4 / XFS Filesystem"]
```

---

## 4. Volume Resizing Operations

```bash
# 1. Extend an LVM Logical Volume by 20GB and resize ext4 filesystem simultaneously
lvextend -L +20G -r /dev/vg0/root

# 2. For XFS filesystems (resize while mounted):
lvextend -L +20G /dev/vg0/root
xfs_growfs /
```

---

## 5. Authoritative References

- [Device Mapper Kernel Documentation](https://docs.kernel.org/admin-guide/device-mapper/index.html)
- [LVM Administrator Guide](https://sourceware.org/lvm2/)
- [ArchWiki: LVM](https://wiki.archlinux.org/title/LVM)
