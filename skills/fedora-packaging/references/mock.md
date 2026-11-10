# Clean Chroot Building with Mock on Fedora

Technical reference for building RPM packages inside isolated chroots using `mock`.

---

## 1. Why Mock is Mandatory in Fedora

`mock` creates a clean chroot environment using `dnf` and Linux namespaces:
- Builds packages using only the explicitly declared `BuildRequires:`.
- Simulates the exact official Koji build environment locally.
- Catches missing dependencies, host directory leaks, and unowned files.

---

## 2. Using Mock

```bash
# Add user to mock group
sudo usermod -aG mock $USER

# Build SRPM first
rpmbuild -bs SPECS/myapp.spec

# Build binary RPMs inside isolated Fedora 40 x86_64 chroot
mock -r fedora-40-x86_64 SRPMS/myapp-1.2.3-1.fc40.src.rpm

# Build for Rawhide (development branch)
mock -r fedora-rawhide-x86_64 SRPMS/myapp-1.2.3-1.fc40.src.rpm

# Build for EPEL 9 (Enterprise Linux)
mock -r epel-9-x86_64 SRPMS/myapp-1.2.3-1.fc40.src.rpm
```

### Mock Output Artifacts (`/var/lib/mock/<config>/result/`):
- `build.log`: Full compiler and build log.
- `root.log`: DNF dependency installation log inside the chroot.
- `state.log`: Mock execution phase timestamps.
- Binary `.rpm` packages and debuginfo packages.
