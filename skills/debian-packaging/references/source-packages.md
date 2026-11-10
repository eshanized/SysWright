# Debian Source Package Formats: 3.0 (quilt) vs 3.0 (native)

Technical reference for Debian source package architectures, archive naming, and source generation via dpkg-source.

---

## 1. Debian Source Package Formats

Debian source packages are specified in `debian/source/format`:

### Format `3.0 (quilt)` (Non-Native Upstream Software):
Used for any software authored outside Debian (the vast majority of packages):
- Upstream pristine source tarball: `<pkg>_<version>.orig.tar.xz` (compressed with `xz` or `gz`).
- Debian modification tarball: `<pkg>_<version>-<debian_revision>.debian.tar.xz` (contains the entire `debian/` directory).
- Downstream patches are stored in `debian/patches/` and managed via `quilt`.
- Unpacking a `3.0 (quilt)` package applies the patches automatically; building extracts pristine source and records delta.

### Format `3.0 (native)` (Debian-Specific Software):
Used strictly for software written specifically for Debian (e.g., `dpkg`, `debhelper`, `apt`):
- Single source archive: `<pkg>_<version>.tar.xz`.
- No `.orig.tar.xz` or `-<debian_revision>` suffix; the version has no hyphen.

---

## 2. Upstream Tarball Naming and Repacking

1. **Standard Upstream Tarball**:
   ```text
   pkgname_1.2.3.orig.tar.xz
   ```
2. **DFSG Repacked Tarball (`+dfsg`)**:
   If upstream tarballs bundle non-free files (e.g., precompiled binary blobs, RFCs under non-free licenses, sourceless minified JS), the maintainer must strip the non-free files:
   ```text
   pkgname_1.2.3+dfsg.orig.tar.xz
   ```
   Configured in `debian/watch` with `dversionmangle=s/\+dfsg\d*$//`.

---

## 3. Generating Debian Source Packages with `dpkg-source`

```bash
# Build source package from workspace directory containing debian/
dpkg-source -b .

# Output artifacts generated in parent directory (..):
# - pkgname_1.2.3-1.dsc (Debian Source Control file, cryptographic checksums)
# - pkgname_1.2.3.orig.tar.xz (Pristine upstream source)
# - pkgname_1.2.3-1.debian.tar.xz (Debian packaging directory and patches)

# Unpack a Debian source package for inspection:
dpkg-source -x pkgname_1.2.3-1.dsc
```
