# Linux Filesystems Comparison & Selection Reference

## 1. Scope

This document details major Linux filesystems (ext4, Btrfs, XFS, F2FS, OverlayFS), their data integrity mechanisms, snapshotting capabilities, and operational trade-offs.

---

## 2. Filesystem Comparison Matrix

| Feature | ext4 | Btrfs | XFS | F2FS |
|:---|:---|:---|:---|:---|
| **Architecture** | Journaling (In-place updates) | Copy-on-Write (COW) | Journaling (Allocation Groups) | Log-Structured (LFS) |
| **Data Integrity** | Metadata checksums only (data unchecksummed) | Full CRC32c/xxhash64 checksums for both data & metadata | Full metadata checksums (v5 superblock) | Metadata checksums |
| **Snapshots** | None (Requires LVM) | Subvolume snapshots ($O(1)$) | Reflink copies (`cp --reflink`) | None |
| **Multi-Device / RAID** | External (`mdadm`) | Native integrated RAID (RAID 0/1/1c3/10) | External (`mdadm` / LVM) | External |
| **Compression** | None | Transparent zstd / lzo compression | None | Transparent compression |
| **Online Shrink** | No (Offline only) | Yes (`btrfs filesystem resize`) | **No (Cannot shrink)** | No |
| **Best Use Case** | Baseline stability, legacy compatibility | Desktops, rollbacks, data integrity | Enterprise databases, high-throughput servers | Flash memory, MicroSD, phones |

---

## 3. Detailed Filesystem Architectures

### 3.1 ext4 (Fourth Extended Filesystem)
- Standard Linux filesystem using in-place block allocation with journaling (`data=ordered` default).
- Journaling ensures filesystem structure integrity after power loss, but does not detect silent bit-rot in user data blocks.

### 3.2 Btrfs (B-tree Filesystem)
- Advanced Copy-on-Write filesystem. When data is modified, new blocks are written elsewhere before metadata pointers update.
- **Data Checksums**: Every block has an accompanying checksum; automatically detects silent data corruption during reads.
- **Subvolumes**: Lightweight filesystem trees sharing the same storage pool. Snapshots are instant COW clones of subvolumes.

### 3.3 XFS
- High-scalability filesystem engineered for high concurrency across multi-core systems using independent Allocation Groups (AGs).
- **Reflink**: Modern XFS supports reflink (`cp --reflink`), creating instant copy-on-write clones of individual files.
- **Caution**: XFS partitions **cannot be shrunk**. Expanding is supported (`xfs_growfs`).

### 3.4 OverlayFS
- Union mount filesystem combining multiple directory trees:
  - `lowerdir`: Read-only base layer.
  - `upperdir`: Writable top layer where file modifications are stored.
  - `workdir`: Scratch directory for atomic transactions.
  - Standard in container runtimes (Docker, Podman) and live USB environments.

---

## 4. Authoritative References

- [ext4 Documentation](https://docs.kernel.org/filesystems/ext4/index.html)
- [Btrfs Documentation](https://btrfs.readthedocs.io/)
- [XFS Documentation](https://docs.kernel.org/filesystems/xfs/index.html)
- [Overlay Filesystem](https://docs.kernel.org/filesystems/overlayfs.html)
