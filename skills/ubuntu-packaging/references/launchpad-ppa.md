# Launchpad Personal Package Archives (PPAs) & dput Workflow

Technical reference for configuring, building, signing, and uploading source packages to Launchpad PPAs.

---

## 1. What is a Personal Package Archive (PPA)?

A PPA is an automated repository hosting service provided by Canonical's Launchpad platform.
- Maintainers upload **source packages only** (`.dsc`, `.orig.tar.xz`, `.debian.tar.xz`, and signed `.changes`).
- Launchpad's build farm automatically compiles binary packages across all enabled architectures (`amd64`, `arm64`, `armhf`, `ppc64el`, `s390x`, `riscv64`).
- Launchpad signs the resulting APT repository metadata with its own PPA GPG key.

---

## 2. Preparing and Uploading a Source Package

```bash
# 1. Build source-only package with GPG signature
debuild -S -sa -k"$GPG_KEY_ID"

# Generates:
# ../myapp_1.2.3-0ubuntu1~ppa1~noble1_source.changes

# 2. Upload to Launchpad PPA using dput
dput ppa:myuser/myrepo ../myapp_1.2.3-0ubuntu1~ppa1~noble1_source.changes
```

### Critical Rules:
- Launchpad strictly rejects binary `.deb` uploads to PPAs; builds must always use `-S` (source-only).
- The GPG key used to sign the `.changes` file must be registered and verified on your Launchpad profile.
- Uploads cannot overwrite existing versions in a PPA. To fix a broken build in a PPA, increment the package version (e.g., `~ppa2`).

---

## 3. Monitoring Launchpad Build Results

After upload, monitor the Launchpad build farm:
- Inspect build logs per architecture.
- Common failure: Architecture-specific compilation issues (e.g., assuming 64-bit pointers on `armhf`, or endianness bugs on `s390x`).
- Autopkgtest status: If `debian/tests/control` is present, Launchpad runs autopkgtest on the built `.deb` files before publication.
