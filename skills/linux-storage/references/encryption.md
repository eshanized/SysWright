# Storage Encryption & LUKS Key Management Reference

## 1. Scope

This document details block device encryption using `dm-crypt`, the LUKS format (LUKS1 vs LUKS2), key slot management, and TPM2 auto-unlocking.

---

## 2. LUKS Architecture (LUKS1 vs LUKS2)

| Feature | LUKS1 | LUKS2 (Modern Standard) |
|:---|:---|:---|
| **Header Format** | Fixed binary header | Redundant JSON metadata header with binary key slots |
| **Key Derivation Function** | PBKDF2 (Vulnerable to GPU bruteforce) | Argon2id / Argon2i (Memory-hard against ASIC/GPU bruteforce) |
| **Data Integrity** | None | Optional authenticated encryption (dm-integrity / AEAD) |
| **Token Framework** | None | Native JSON tokens (FIDO2, TPM2, PKCS#11 integration) |

---

## 3. Cryptsetup Operations

```bash
# 1. Format a block device with LUKS2
cryptsetup luksFormat --type luks2 /dev/nvme0n1p3

# 2. Open encrypted container (maps to /dev/mapper/cryptroot)
cryptsetup open /dev/nvme0n1p3 cryptroot

# 3. Close encrypted container
cryptsetup close cryptroot

# 4. Add a backup passphrase to key slot
cryptsetup luksAddKey /dev/nvme0n1p3

# 5. Enroll TPM2 chip for automatic secure unlocking during boot
systemd-cryptenroll --tpm2-device=auto --tpm2-pcrs=0+7 /dev/nvme0n1p3
```

### Security Invariants:
- Never print or store cleartext encryption keys or passphrases in logs, diagnostics, or version control.
- Always retain at least one recovery passphrase key slot when enrolling hardware tokens (TPM2 / FIDO2).

---

## 4. Authoritative References

- [cryptsetup(8) Manual](https://man.archlinux.org/man/cryptsetup.8)
- [systemd-cryptenroll(1) Manual](https://man.archlinux.org/man/systemd-cryptenroll.1)
- [ArchWiki: dm-crypt/Device encryption](https://wiki.archlinux.org/title/Dm-crypt/Device_encryption)
