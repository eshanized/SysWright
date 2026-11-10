# RPM Package Signing: GPG, rpmsign, and Signature Verification

Technical reference for signing RPM packages, key management, and verifying package authenticity.

---

## 1. Cryptographic Signature Architecture in RPM

RPM signs both individual package headers (`.rpm`) and repository metadata (`repomd.xml`):
- Package Header Signatures: Verify that the package was produced by a trusted builder and has not been tampered with.
- SHA-256 Digest: Protects the integrity of the cpio payload.

---

## 2. Signing Packages with `rpmsign`

Configure signing identity in `~/.rpmmacros`:
```ini
%_gpg_name Release Signing Key <security@example.org>
%_gpg_path ~/.gnupg
%_gpg_digest_algo sha256
```

### Applying Signature:
```bash
# Add or replace GPG signature on binary RPM
rpmsign --addsign myapp-1.2.3-1.fc40.x86_64.rpm

# Sign multiple packages in bulk
rpmsign --addsign RPMS/x86_64/*.rpm
```

---

## 3. Verifying Package Signatures (`rpm -K`)

Before installing or deploying an RPM package, verify its cryptographic integrity:

```bash
# Import trusted public GPG key into RPM keyring
sudo rpm --import RPM-GPG-KEY-example

# Check package signature
rpm -Kv myapp-1.2.3-1.fc40.x86_64.rpm
```

### Expected Clean Verification Output:
```text
myapp-1.2.3-1.fc40.x86_64.rpm:
    Header V4 RSA/SHA256 Signature, key ID a87c9d2f: OK
    Header SHA256 digest: OK
    Header SHA1 digest: OK
    Payload SHA256 digest: OK
    MD5 digest: OK
```
- If key is missing: `(MISSING KEYS: key ID a87c9d2f)`.
- If tampered: `BAD Signature` or `BAD Digest`.
