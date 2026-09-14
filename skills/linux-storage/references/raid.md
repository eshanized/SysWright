# Software RAID (mdadm) & Multi-Device Storage Reference

## 1. Scope

This document details Linux software RAID via `mdadm`, RAID levels (0, 1, 5, 6, 10), write-intent bitmaps, and Btrfs native multi-device pools.

---

## 2. Linux Software RAID (`mdadm`)

### 2.1 Standard RAID Levels
- **RAID 0 (Striping)**: Combines drives for maximum speed. Zero fault tolerance (one drive fails $\to$ all data lost).
- **RAID 1 (Mirroring)**: Exact copy across drives. Tolerates $N-1$ drive failures. High read speed.
- **RAID 5 (Distributed Parity)**: Requires $\ge 3$ drives. Tolerates 1 drive failure.
- **RAID 6 (Dual Parity)**: Requires $\ge 4$ drives. Tolerates 2 simultaneous drive failures.
- **RAID 10 (Striped Mirrors)**: Requires $\ge 4$ drives. Combines performance of RAID 0 with redundancy of RAID 1.

### 2.2 Array Operations
```bash
# 1. Create a RAID 1 mirrored array
mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sda1 /dev/sdb1

# 2. Check sync status
cat /proc/mdstat

# 3. Add internal write-intent bitmap (accelerates resync after unexpected reboot)
mdadm --grow /dev/md0 --bitmap=internal

# 4. Save array configuration to /etc/mdadm.conf
mdadm --detail --scan >> /etc/mdadm.conf
```

---

## 3. Btrfs Native Multi-Device Pools

Btrfs provides filesystem-level RAID without `mdadm`:
```bash
# Convert existing single Btrfs filesystem to RAID 1 data and metadata
btrfs balance start -dconvert=raid1 -mconvert=raid1 /mnt/data
```

---

## 4. Authoritative References

- [mdadm(8) Manual](https://man.archlinux.org/man/mdadm.8)
- [mdadm.conf(5) Manual](https://man.archlinux.org/man/mdadm.conf.5)
- [ArchWiki: RAID](https://wiki.archlinux.org/title/RAID)
