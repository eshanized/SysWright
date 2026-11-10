# Debian Package Quality Assurance: lintian, autopkgtest, and piuparts

Technical reference for static quality linting, as-installed integration testing, and installation lifecycle verification.

---

## 1. Static Package Auditing with lintian

`lintian` is the official static analysis checker for Debian packages. It analyzes source packages (`.dsc`), binary packages (`.deb`), and upload metadata (`.changes`):

```bash
lintian -I --pedantic myapp_1.2.3-1_amd64.changes
```

### Lintian Severity Tags:
- **`E:` (Error)**: Direct violation of the Debian Policy Manual. **Blocks archive acceptance!** Must be fixed before upload.
- **`W:` (Warning)**: Probable violation of policy or packaging standard. Strongly recommended to fix or provide justification.
- **`I:` (Info)**: Informational recommendation.
- **`P:` (Pedantic)**: Minor stylistic or formatting observation.
- **Overrides**: If a lintian tag is a proven false positive, add an override in `debian/source/lintian-overrides` or `debian/<pkg>.lintian-overrides` with an explanatory comment.

---

## 2. As-Installed Integration Testing with autopkgtest

`autopkgtest` installs the built `.deb` into a clean testbed (virtual machine or container) and runs tests against the *installed* system binaries, verifying that shared library links, systemd units, and CLI paths work:

### Defining Tests in `debian/tests/control`:
```ini
Tests: test-cli, test-daemon
Depends: @, curl, systemd
Restrictions: needs-root
```
- `@`: Refers to the binary packages built from this source package.
- `Restrictions: needs-root`: Declares that the test requires root permissions in the testbed.

### Running autopkgtest:
```bash
autopkgtest myapp_1.2.3-1_amd64.changes -- null
# Or inside a QEMU VM:
autopkgtest myapp_1.2.3-1_amd64.changes -- qemu /var/lib/debvm/debian-sid.qcow2
```

---

## 3. Package Lifecycle Verification with piuparts

`piuparts` (package installation, upgrade and purging testing suite) tests the complete dpkg lifecycle:
1. Installs `.deb` in a minimal root filesystem.
2. Checks for unowned files left behind.
3. Tests upgrading from previous distribution versions.
4. Purges the package (`dpkg -P`) and verifies that `/etc`, `/var`, and `/usr` are completely clean of orphaned files.
