# Repository Cryptographic Signing & Key Lifecycle

Clients trust package repositories exclusively through cryptographic signatures. A compromised or improperly configured signing key can lead to unauthorized software execution on millions of hosts.

---

## 1. Key Hierarchy & Security Principles

```text
[ Root / Master Key ]  (4096-bit RSA or Ed25519; OFFLINE on air-gapped HSM/SmartCard)
         │  Signs Certification / Subkeys
         ▼
[ Repository Signing Subkey ]  (ONLINE on automated build/signing agent)
         │  Signs Release files / repomd.xml
         ▼
[ Client Package Manager ]  (Trusts Public Master Key or Active Subkey)
```

### Security Invariants:
1. **Never Place the Master Key on a Build Server**: If the signing server is breached, only the signing subkey is exposed. The master key can issue a revocation certificate and generate a replacement subkey without requiring users to reinstall a new root certificate.
2. **Key Expiration Policy**: Signing subkeys must have explicit expiration dates (e.g., 1 to 2 years). Rotate subkeys 60 days before expiration.
3. **Never Strip Revocation Signatures**: Keep revocation certificates generated at key creation in offline physical storage.

---

## 2. Signing Commands by Repository Type

### Debian / Ubuntu (`Release` and `InRelease`)
APT supports inline signing (`InRelease`) and detached signing (`Release.gpg`). Inline is preferred by modern APT.

```bash
# Generate InRelease (cleartext signed)
gpg --default-key "$KEY_ID" --clearsign -o dists/noble/InRelease dists/noble/Release

# Generate detached Release.gpg
gpg --default-key "$KEY_ID" -abs -o dists/noble/Release.gpg dists/noble/Release
```

### Fedora / RHEL (`repomd.xml.asc`)
DNF requires detached signatures over the master `repomd.xml`:

```bash
gpg --default-key "$KEY_ID" --detach-sign --armor /srv/repo/repodata/repomd.xml
# Result: /srv/repo/repodata/repomd.xml.asc
```

### Arch Linux (`.db.sig`)
Pacman checks GPG signatures on repository databases and binary packages:

```bash
repo-add --sign --key "$KEY_ID" custom.db.tar.zst *.pkg.tar.zst
```

---

## 3. Subkey Rotation Procedure

1. **Generate New Subkey on Master Air-Gapped Host**:
   ```bash
   gpg --expert --edit-key "$MASTER_KEY_ID"
   # gpg> addkey (select RSA [sign only] or Ed25519)
   # gpg> save
   ```
2. **Publish Updated Public Keyring**:
   Export updated public keyring containing both old and new subkeys:
   ```bash
   gpg --armor --export "$MASTER_KEY_ID" > /srv/repo/KEY.gpg
   ```
3. **Grace Period**:
   Allow clients 30 days to update their trusted keyring before signing production metadata with the new subkey.
4. **Switch Signing Daemon**:
   Install the new private subkey on the signing server.