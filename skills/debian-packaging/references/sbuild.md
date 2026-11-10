# Clean Chroot Building with sbuild and schroot

Technical reference for configuring and executing isolated Debian package builds using `sbuild`.

---

## 1. Why Isolated Clean Chroot Builds Are Mandatory

Building packages directly on a development host has critical failure modes:
- **Undeclared Build Dependencies**: The developer installed `pkgconf` or `libcurl-dev` manually months ago; the package compiles locally but fails on official buildds.
- **Host Contamination**: Compilers pick up unversioned libraries in `/usr/local/lib` or environment variables set in `~/.bashrc`.
- **Target Distribution Mismatch**: Building for `unstable` (sid) or `stable-backports` while running testing on the workstation.

`sbuild` builds the package inside a minimal, disposable chroot containing only `build-essential` and explicitly declared `Build-Depends`.

---

## 2. Setting Up sbuild on Debian / Ubuntu

```bash
# Install sbuild and schroot
sudo apt-get install sbuild schroot debootstrap

# Add user to sbuild group
sudo sbuild-adduser $USER

# Create a minimal Debian unstable (sid) chroot
sudo sbuild-createchroot \
    --include=eatmydata \
    unstable /srv/chroot/unstable-amd64-sbuild \
    http://deb.debian.org/debian
```

---

## 3. Building Packages with sbuild

```bash
# Update the build chroot packages
sbuild-update -udcar unstable-amd64-sbuild

# Build package from Debian source control (.dsc) file
sbuild -d unstable myapp_1.2.3-1.dsc

# Build directly from source directory with git-buildpackage (gbp)
gbp buildpackage --git-builder="sbuild -d unstable"
```

### Key sbuild Output Verification:
1. `dpkg-checkbuilddeps`: Confirms all declared `Build-Depends` are installable.
2. Build log: Captured in `myapp_1.2.3-1_amd64.build`.
3. Auto-lintian: `sbuild` automatically runs `lintian` against generated `.deb` and `.changes` artifacts.
