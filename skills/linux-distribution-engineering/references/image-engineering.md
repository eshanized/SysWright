# Distribution Image Engineering & Composable Systems

Modern Linux distribution engineering extends beyond raw repositories into generating production system images (cloud images, container base layers, live installer ISOs, and immutable root filesystems).

---

## 1. Modern Image Generation Tooling

| Tool | Primary Distribution Target | Description |
|---|---|---|
| **`mkosi`** | Systemd-centric (Arch, Fedora, Debian, Ubuntu) | Creates raw GPT disk images, cloud images, and UKIs using systemd primitives. |
| **`kiwi`** | openSUSE, SLE, Fedora, Ubuntu | Comprehensive appliance builder creating OEM disks, live ISOs, and PXE boot images. |
| **`debootstrap` / `mmdebstrap`** | Debian, Ubuntu | Installs minimal Debian base system into a directory without host contamination. |
| **`lorax` / `livemedia-creator`** | Fedora, RHEL | Builds Anaconda installer ISOs and official cloud images. |

---

## 2. Minimal Base Image Creation with `mmdebstrap`

`mmdebstrap` operates without root privileges (using user namespaces) and generates bit-for-bit deterministic root filesystems:

```bash
mmdebstrap \
  --mode=unshare \
  --variant=minbase \
  --include=systemd,udev,iproute2,ca-certificates \
  bookworm \
  /srv/images/base-bookworm.tar.zst \
  http://deb.debian.org/debian
```

---

## 3. Composable Systems: Systemd Sysext and Confext

Immutable and A/B partition systems (e.g., Fedora Silverblue, openSUSE MicroOS, Ubuntu Core) use system extensions instead of mutating `/usr`:

- **`systemd-sysext`**: Dynamically merges read-only squashfs or dm-verity overlay images into `/usr/` at boot.
- **`systemd-confext`**: Dynamically merges read-only configuration overlays into `/etc/`.

### Creating a Sysext Image:
1. Stage binaries and libraries under `rootfs/usr/bin` and `rootfs/usr/lib`.
2. Add metadata file `rootfs/usr/lib/extension-release.d/extension-release.<name>` containing:
   ```ini
   ID=fedora
   VERSION_ID=40
   ```
3. Generate squashfs:
   ```bash
   mksquashfs rootfs/ myapp-extension.raw -comp zstd
   ```
4. Place in `/var/lib/extensions/` and activate with:
   ```bash
   systemd-sysext merge
   ```