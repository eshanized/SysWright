---
name: linux-storage
description: Linux storage engineering skill for block devices, filesystems (ext4, Btrfs, XFS, F2FS), Device Mapper, LVM volume management, LUKS disk encryption, software RAID (mdadm), and data recovery. Covers blk-mq queue schedulers, NVMe and SMART health diagnostics, online volume expansion, TPM2 auto-unlocking, and strict data protection invariants (fsck safety, refusal of autonomous formatting). Use when investigating storage performance, configuring filesystems, setting up LUKS/LVM, or diagnosing mount failures.
license: Apache-2.0
compatibility: Requires Linux environment with storage userspace tooling (lsblk, blkid, cryptsetup, lvm2).
metadata:
  author: Eshan Roy
  version: "0.1.0"
  claude_context: "fork"
  claude_agent: "general"
---

# Linux Storage Engineering

The `linux-storage` skill provides specialist capabilities for analyzing and managing Linux block devices, filesystems (ext4, Btrfs, XFS), LVM logical volumes, LUKS encryption containers, software RAID, and storage diagnostics.

---

## 1. Operating Principles & Strict Data Protection Invariants

1. **Protect User Data Above All Else**: Storage operations carry irreversible destruction risks. Never execute destructive formatting commands (`mkfs`, `wipefs`, `dd` to raw disks) autonomously.
2. **Never Run `fsck` on a Mounted Filesystem**: Running filesystem checkers on mounted read-write filesystems corrupts metadata. Always unmount or remount read-only first.
3. **Verify Device Identity Before Action**: Never rely on transient device nodes (e.g. `/dev/sdb`) which can shift across reboots. Always reference storage by persistent identifiers: UUID (`/dev/disk/by-uuid/`) or PARTUUID.
4. **Safety Tier Gating**: All partition modifications, formatting, volume deletion, RAID rebuilding, and encryption re-keying are Tier 3 operations requiring explicit human authorization.

---

## 2. Intent Classification & Workflow Routing

```mermaid
flowchart TD
    REQ["Storage Engineering Request"] --> CLASS{"Classify Storage Task"}

    CLASS -->|Mount Failure / Corrupt Filesystem| DIAG["1. Storage Diagnostics\n(lsblk, findmnt, smartctl, mount logs, read-only checks)"]
    CLASS -->|Filesystem Selection / Tuning| FS["2. Filesystem Engineering\n(ext4, Btrfs COW snapshots, XFS reflink, F2FS, trim)"]
    CLASS -->|Volume Management (LVM)| LVM["3. Logical Volume Management\n(PV, VG, LV creation, thin pools, online lvextend)"]
    CLASS -->|Disk Encryption (LUKS)| CRYPT["4. Encryption Engineering\n(cryptsetup, LUKS2, Argon2id, TPM2 auto-unlock)"]
    CLASS -->|Redundant Arrays (RAID)| RAID["5. Software RAID\n(mdadm, RAID 1/5/6/10, sync status, Btrfs RAID)"]

    DIAG --> EXEC["Execute Storage Workflow"]
    FS --> EXEC
    LVM --> EXEC
    CRYPT --> EXEC
    RAID --> EXEC
```

---

## 3. The 5-Step Storage Diagnostic Workflow

1. **Hierarchy Inspection**: Run `lsblk -f` to map the complete hierarchy from physical device to partitions, LUKS containers, LVM volumes, and mount points.
2. **Health Verification**: Check controller health and error counters via `nvme smart-log` or `smartctl -a`.
3. **Mount State Audit**: Query `findmnt` and `journalctl -xb` to isolate filesystem mount errors without modifying on-disk state.
4. **Read-Only Verification**: Perform non-destructive read-only checks (`btrfs check --readonly`, `dumpe2fs`).
5. **Human-Gated Remediation**: Provide explicit, verified recovery commands requiring user confirmation before executing any state-mutating repairs.

---

## 4. Cross-Specialist Coordination

| Task | Coordinating Specialists | Interaction |
|:---|:---|:---|
| Encrypted root volume boot | `linux-storage` + `boot-engineering` | `linux-storage` sets up LUKS/Btrfs; `boot-engineering` configures `sd-encrypt` and cmdline. |
| NVMe PCIe hardware failure | `linux-storage` + `driver-engineering` | `linux-storage` checks blk-mq/smart-log; `driver-engineering` checks PCIe link/BARs. |
| Daemon storage directories | `linux-storage` + `systemd-engineering` | `linux-storage` provisions volumes; `systemd-engineering` wires `StateDirectory=`. |

---

## 5. Authoritative References Directory

- [Storage Architecture & Block Layer](references/storage-architecture.md)
- [Filesystems Comparison & Selection](references/filesystems.md)
- [Device Mapper & LVM Reference](references/device-mapper-lvm.md)
- [Storage Encryption & LUKS](references/encryption.md)
- [Software RAID & Multi-Device Storage](references/raid.md)
- [Diagnostics & Troubleshooting](references/troubleshooting-and-recovery.md)
- [Safety Policy](../../references/safety-policy.md)
