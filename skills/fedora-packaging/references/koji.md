# Koji: The Official Fedora Build System

Technical reference for understanding Koji build architecture, build targets, side tags, and build troubleshooting.

---

## 1. Koji Architecture

Koji (`koji.fedoraproject.org`) is the distributed build daemon network that compiles all official Fedora packages:
- Pulls source files from Fedora dist-git and the Lookaside Cache.
- Spawns builders across all primary architectures (`x86_64`, `aarch64`, `ppc64le`, `s390x`).
- Signs built packages with Fedora official release keys.

---

## 2. Querying Koji via CLI

```bash
# Query status of a specific build
koji buildinfo myapp-1.2.3-1.fc40

# Download build artifacts (.rpm) from Koji
koji download-build --arch=x86_64 myapp-1.2.3-1.fc40

# Inspect builder task logs
koji watch-task <TASK_ID>
```

---

## 3. Side Tags for Coordinated Builds

When a package update breaks API/ABI (e.g., shared library soname bump), rebuilding dependent packages against Rawhide will fail until the new library is available.
- **Solution: Side Tags**: Create an ephemeral build tag where the new library is built first, followed by dependent packages:
  ```bash
  # Request side tag
  fedpkg request-side-tag
  # Build into side tag
  fedpkg build --target=f40-build-side-12345
  ```
- Once all dependent packages compile cleanly, the side tag is merged into the main release target atomically.
