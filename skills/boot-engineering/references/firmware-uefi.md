# UEFI Firmware & Boot Environment Reference

## 1. Scope

This document details UEFI firmware architecture, the EFI System Partition (ESP), NVRAM boot variable management with `efibootmgr`, and TPM2 boot measurement.

---

## 2. UEFI vs. Legacy BIOS Architecture

| Feature | Legacy BIOS | UEFI (Unified Extensible Firmware Interface) |
|:---|:---|:---|
| **Partition Table** | MBR (Master Boot Record, max 2TB, 4 primary partitions) | GPT (GUID Partition Table, max 9.4 ZB, 128+ partitions) |
| **Boot Mechanism** | Executes 446 bytes of machine code in MBR Sector 0 | Executes PE/COFF `.efi` executable binaries from standard FAT32 filesystem |
| **Boot Entries** | Fixed disk order in CMOS ROM | Dynamic NVRAM variables storing path to `.efi` binary and partition UUID |
| **Security** | None | Secure Boot (X.509 cryptographic validation) & TPM2 measured boot |

---

## 3. The EFI System Partition (ESP)

The ESP is a dedicated partition formatted as FAT32 (or FAT16):
- **Partition Type GUID**: `C12A7328-F81F-11D2-BA4B-00A0C93EC93B` (in `fdisk`/`gdisk`: type `EF00`).
- **Mount Location**:
  - Preferred standard: `/efi` (clean separation) or `/boot` (unified).
  - Alternative legacy: `/boot/efi`.
- **Default Fallback Path**: `\EFI\BOOT\BOOTX64.EFI` (used when NVRAM entries are wiped or booting removable media).

---

## 4. NVRAM Boot Variable Management: `efibootmgr`

`efibootmgr` allows inspecting and modifying UEFI NVRAM boot entries:

```bash
# 1. List current boot entries and boot order
efibootmgr -v

# Sample Output:
# BootCurrent: 0001
# BootOrder: 0001,0002,0000
# Boot0001* Arch Linux  HD(1,GPT,a1b2c3d4-...)/File(\vmlinuz-linux)root=UUID=...

# 2. Create a new UEFI boot entry
efibootmgr \
  --create \
  --disk /dev/nvme0n1 \
  --part 1 \
  --label "Arch Linux" \
  --loader /vmlinuz-linux \
  --unicode 'root=UUID=4a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d rw initrd=\initramfs-linux.img'

# 3. Change boot order
efibootmgr --bootorder 0001,0002

# 4. Remove a stale boot entry
efibootmgr --bootnum 0003 --delete-bootnum
```

---

## 5. TPM2 Boot Measurements & PCR Banks

UEFI firmware and bootloaders measure boot components into Trusted Platform Module (TPM2) Platform Configuration Registers (PCRs):
- **PCR 0**: Core UEFI firmware code and version.
- **PCR 4**: Bootloader binary execution.
- **PCR 7**: Secure Boot state (PK, KEK, db, dbx).
- **PCR 8 / 9**: Kernel command line and initramfs image measurements (systemd-stub).
- Automatic LUKS decryption via `systemd-cryptenroll --tpm2-device=auto --tpm2-pcrs=0+7` ensures disks decrypt only when firmware and Secure Boot states are uncompromised.

---

## 6. Authoritative References

- [UEFI Specification](https://uefi.org/specifications)
- [ArchWiki: Unified Extensible Firmware Interface](https://wiki.archlinux.org/title/Unified_Extensible_Firmware_Interface)
- [efibootmgr(8) Manual](https://man.archlinux.org/man/efibootmgr.8)
