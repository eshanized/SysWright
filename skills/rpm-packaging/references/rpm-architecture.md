# RPM Package Architecture: Lead, Header, Payload, and Database

Comprehensive technical reference for the internal structure of RPM binary and source packages.

---

## 1. Binary RPM Package Structure

An RPM file (`.rpm`) is an uncompressed container divided into four contiguous sections:

```
[Lead] ──► [Signature Section] ──► [Header Section] ──► [Payload (cpio archive)]
```

1. **Lead**: Legacy 96-byte header identifying the file as an RPM package (magic number `0xedabeedb`). Mostly obsolete, retained for `file(1)` compatibility.
2. **Signature Section**: Contains cryptographic signatures (RSA/GPG) and SHA-256 digests over the Header and Payload sections.
3. **Header Section**: Contains key-value metadata tags:
   - Package identity: `NAME`, `VERSION`, `RELEASE`, `EPOCH`, `ARCH`.
   - Descriptive data: `SUMMARY`, `DESCRIPTION`, `LICENSE`, `URL`.
   - Dependency tags: `PROVIDENAME`, `REQUIRENAME`, `CONFLICTNAME`, `OBSOLETENAME`.
   - File table: Paths, file sizes, file modes, MD5/SHA256 checksums, users, groups, and flags.
4. **Payload Section**: A `cpio` archive containing the actual installed files, compressed with `xz` or `zstd`.

---

## 2. Inspecting RPM Packages Directly

Use the `rpm` command to inspect uninstalled RPM packages without root privileges:

```bash
# Print package metadata and description
rpm -qip myapp-1.2.3-1.fc40.x86_64.rpm

# List all files inside the package payload
rpm -qlp myapp-1.2.3-1.fc40.x86_64.rpm

# List dependencies required by the package
rpm -qRp myapp-1.2.3-1.fc40.x86_64.rpm

# List capabilities provided by the package
rpm --provides -qp myapp-1.2.3-1.fc40.x86_64.rpm

# Inspect package installation scriptlets
rpm --scripts -qp myapp-1.2.3-1.fc40.x86_64.rpm

# Verify cryptographic signature of the package
rpm -Kv myapp-1.2.3-1.fc40.x86_64.rpm
```

---

## 3. The RPM Database (`rpmdb`)

On installed systems, package status is tracked in `/var/lib/rpm`:
- Modern Linux distributions use `sqlite` or `ndb` (new db format) as the database backend (replacing legacy Berkeley DB `BDB`).
- Querying installed packages: `rpm -qa` or `rpm -qf /usr/bin/binary`.
- Database verification: `rpm -Va` audits installed files against the checksums and permissions recorded in the RPM database.
