# Upstream Release Tracking & Automation

Package maintainers must proactively detect new upstream releases, security advisories, and source tarball publications to prevent packages from stagnating.

---

## 1. Upstream Monitoring Tools & Protocols

### Debian `uscan` and `debian/watch`
`uscan` scans remote web pages, FTP sites, or Git repositories to discover new releases based on regex patterns defined in `debian/watch`.

```text
# debian/watch format version 4
version=4
opts="filenamemangle=s%(?:.*?)?(?:v|version)?(\d[\d.]*)\.tar\.gz%myapp-$1.tar.gz%,pgpmode=auto" \
https://github.com/example/myapp/releases \
(?:.*?/)?(?:v|version)?(\d[\d.]*)\.tar\.gz debian uupdate
```

**Running uscan**:
```bash
# Dry run to check for newer releases
uscan --dry-run --verbose

# Download and verify latest release
uscan --download --verbose
```

### Fedora / Upstream Anitya (release-monitoring.org)
Anitya is an open-source project tracking upstream release versions across thousands of projects. Fedora dist-git and Arch Linux maintainers query Anitya via REST APIs to trigger automated packaging pull requests.

---

## 2. Version Schemes: SemVer vs CalVer vs Date-Based

| Scheme | Format Example | Upgrade Compatibility Assumption |
|---|---|---|
| **Semantic Versioning (SemVer)** | `MAJOR.MINOR.PATCH` (`1.4.2`) | MAJOR breaks backward compatibility; MINOR adds features backward-compatibly; PATCH fixes bugs. |
| **Calendar Versioning (CalVer)** | `YY.MM.MICRO` (`24.04.1`) | Common for distributions (Ubuntu) and utilities; indicates release cadence rather than strict API stability. |
| **Commit / Git Snapshots** | `1.2.3^20260401gitabc123` | Used for unreleased pre-release development branches. |

---

## 3. Upstream Tarball Verification

Never unpack or package an upstream archive without verifying its authenticity:
1. **GPG Signatures**:
   ```bash
   gpg --verify myapp-1.2.3.tar.gz.asc myapp-1.2.3.tar.gz
   ```
2. **SHA-256 Checksums**:
   Compare against official signed release manifests.
3. **Pristine Source Verification**:
   Ensure tarball does not contain precompiled `.so`, `.jar`, `.exe`, or minified JavaScript files.