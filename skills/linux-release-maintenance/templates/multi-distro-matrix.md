# Multi-Distribution Packaging Compatibility Matrix

| Distribution Family | Target Release | Package Format | Build Tooling | Linter / Validator | Status |
|---|---|---|---|---|---|
| **Arch Linux** | Rolling | `pkg.tar.zst` | `extra-x86_64-build` | `namcap` | [ ] Verified |
| **Debian** | 12 (Bookworm) | `.deb` | `sbuild` | `lintian` | [ ] Verified |
| **Debian** | unstable (Sid) | `.deb` | `sbuild` | `lintian` | [ ] Verified |
| **Ubuntu** | 24.04 LTS (Noble) | `.deb` | `sbuild` / PPA | `lintian` | [ ] Verified |
| **Fedora** | 40 | `.rpm` | `mock` / Koji | `rpmlint` | [ ] Verified |
| **Fedora** | Rawhide | `.rpm` | `mock` / Koji | `rpmlint` | [ ] Verified |
| **openSUSE** | Tumbleweed | `.rpm` | `osc build` | `rpmlint` | [ ] Verified |
| **openSUSE** | Leap 15.6 | `.rpm` | `osc build` | `rpmlint` | [ ] Verified |
| **RHEL / EPEL** | EPEL 9 | `.rpm` | `mock` | `rpmlint` | [ ] Verified |
