# Advanced Arch Linux Packaging Procedures

## 1. Scope

This document details advanced packaging architectures in Arch Linux, including split packages, VCS packages, DKMS kernel modules, desktop and systemd integration, font packaging, and proprietary software distribution.

---

## 2. Split Packages

Split packages allow a single source codebase to produce multiple binary packages (e.g., separating runtime libraries from CLI tools, development headers, or documentation).

### 2.1 Split Package Architecture
```bash
pkgbase=libgit2
pkgname=('libgit2' 'libgit2-docs')
pkgver=1.8.0
pkgrel=1
arch=('x86_64')
url="https://libgit2.org"
license=('GPL-2.0-or-later WITH GCC-exception-2.0')
makedepends=('cmake' 'ninja' 'python')

build() {
  cmake -B build -S "$pkgbase-$pkgver" -G Ninja \
    -DCMAKE_BUILD_TYPE=None \
    -DCMAKE_INSTALL_PREFIX=/usr
  cmake --build build
}

check() {
  ctest --test-dir build --output-on-failure
}

package_libgit2() {
  pkgdesc="C implementation of the Git core methods"
  depends=('glibc' 'openssl' 'zlib' 'libssh2')
  provides=('libgit2.so')

  DESTDIR="$pkgdir" cmake --install build
  # Remove documentation to be packaged separately
  rm -rf "$pkgdir/usr/share/doc"
}

package_libgit2-docs() {
  pkgdesc="Documentation for libgit2"
  arch=('any')

  install -d "$pkgdir/usr/share/doc/$pkgbase"
  cp -r "$srcdir/$pkgbase-$pkgver/docs/"* "$pkgdir/usr/share/doc/$pkgbase/"
}
```

### 2.2 Split Packaging Rules
- `pkgbase` is mandatory if `pkgname` contains multiple entries.
- `prepare()`, `build()`, and `check()` run once globally.
- Each `package_<subpkgname>()` function operates in an isolated `$pkgdir` dedicated to that subpackage.
- Variables declared inside `package_*()` override global variables for that specific subpackage.

---

## 3. VCS Packages (`-git`)

VCS packages build directly from upstream version control systems.

### 3.1 Syntax and Conventions
```bash
pkgname=ripgrep-git
pkgver=14.1.0.r12.g9a3bc2e
pkgrel=1
arch=('x86_64')
url="https://github.com/BurntSushi/ripgrep"
license=('MIT' 'Unlicense')
depends=('glibc')
makedepends=('git' 'cargo')
provides=('ripgrep')
conflicts=('ripgrep')
source=("$pkgname::git+https://github.com/BurntSushi/ripgrep.git#branch=master")
sha256sums=('SKIP')

pkgver() {
  cd "$pkgname"
  # Standard Git version format: <tag>.r<commits_since_tag>.g<commit_hash>
  git describe --long --tags --abbrev=7 | sed 's/\([^-]*-g\)/r\1/;s/-/./g'
}
```

### 3.2 VCS Invariants
1. `provides` and `conflicts` must declare the base non-VCS package name.
2. `source` URL should use `git+https://` or `git+ssh://`.
3. `sha256sums` uses `'SKIP'` for dynamic VCS branches.
4. `pkgver()` must produce strictly monotonic version strings that pacman `vercmp` sorts correctly.

---

## 4. DKMS (Dynamic Kernel Module Support) Packages

When packaging out-of-tree Linux kernel modules, DKMS allows users to automatically rebuild the module when upgrading kernels:

### 4.1 Packaging Structure
- Install module source files to: `/usr/src/$pkgname-$pkgver/`
- Install a `dkms.conf` file inside that directory:
  ```ini
  PACKAGE_NAME="vboxguest"
  PACKAGE_VERSION="7.0.18"
  AUTOINSTALL="yes"

  BUILT_MODULE_NAME[0]="vboxguest"
  DEST_MODULE_LOCATION[0]="/kernel/misc"
  ```
- Declare `depends=('dkms')` in `PKGBUILD`.
- Pacman hooks provided by the `dkms` package automatically trigger compilation upon kernel installation.

---

## 5. Desktop & Graphical Application Integration

Packages providing desktop applications must integrate with FreeDesktop specifications:

### 5.1 Desktop Entry Files (`.desktop`)
- Install to `/usr/share/applications/$pkgname.desktop`.
- Validate syntax using `desktop-file-validate`:
  ```bash
  desktop-file-validate "$pkgdir/usr/share/applications/$pkgname.desktop"
  ```

### 5.2 Application Icons
- Install scalable vector icons (SVG) to:
  `/usr/share/icons/hicolor/scalable/apps/$pkgname.svg`
- Install fixed raster icons (PNG) to:
  `/usr/share/icons/hicolor/<size>x<size>/apps/$pkgname.png`
- Arch uses libalpm post-transaction hooks to update the icon cache automatically.

---

## 6. Fonts Packaging Guidelines

- TrueType fonts: install to `/usr/share/fonts/TTF/`.
- OpenType fonts: install to `/usr/share/fonts/OTF/`.
- `arch` must be set to `('any')`.
- File permissions must be `0644`.

---

## 7. Proprietary & Non-Free Software Distribution

1. **License Tagging**:
   - Use `license=('LicenseRef-Proprietary')` or `license=('custom:Commercial')`.
2. **License Text**:
   - Always install the proprietary EULA / terms of service to:
     `/usr/share/licenses/$pkgname/LICENSE`
3. **No Direct Upload of Restricted Binaries**:
   - If upstream forbids redistribution of binaries, write a PKGBUILD that downloads the installer directly from upstream servers at build time. Never upload copyrighted proprietary archives to the AUR or public git repositories.

---

## 8. Authoritative References

- [Arch package guidelines: VCS packages](https://wiki.archlinux.org/title/VCS_package_guidelines)
- [Arch package guidelines: Fonts](https://wiki.archlinux.org/title/Font_package_guidelines)
- [DKMS Package Guidelines](https://wiki.archlinux.org/title/DKMS_package_guidelines)
- [FreeDesktop Desktop Entry Specification](https://specifications.freedesktop.org/desktop-entry-spec/latest/)
