# Fedora Dist-Git Workflow: fedpkg Reference

Technical reference for managing package source repositories, branches, and uploads using `fedpkg`.

---

## 1. What is fedpkg?

`fedpkg` is the primary CLI client for interacting with Fedora's dist-git repository (`src.fedoraproject.org`):
- Manages upstream lookaside caches (tarballs are not committed directly into git; SHA-512 hashes are tracked in a `sources` file).
- Manages branches (`rawhide`, `f40`, `f39`, `epel9`).
- Submits official builds to Koji.

---

## 2. Standard fedpkg Lifecycle

```bash
# Clone package repository from Fedora dist-git
fedpkg clone myapp
cd myapp

# Switch to specific release branch
fedpkg switch-branch f40

# Download upstream source tarball into workspace
fedpkg sources

# Upload a new upstream tarball to lookaside cache (updates 'sources' file)
fedpkg new-sources myapp-1.2.4.tar.xz

# Run local mock build against current branch target
fedpkg mockbuild

# Commit and push spec/patch updates to dist-git
git commit -m "Update to 1.2.4"
fedpkg push

# Trigger official Koji build from current branch
fedpkg build
```
