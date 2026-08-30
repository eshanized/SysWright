# Upstream Build System Specialization Reference

## 1. Scope

This document details the exact configuration, packaging, and testing workflows for major upstream build systems encountered in Arch Linux packaging.

---

## 2. CMake

### 2.1 Project Indicators
- Root file: `CMakeLists.txt`
- Build generators: `Ninja` (recommended for Arch), `Unix Makefiles`.

### 2.2 Standard Workflow
```bash
makedepends=('cmake' 'ninja')

build() {
  cmake -B build -S "$pkgname-$pkgver" \
    -G Ninja \
    -DCMAKE_BUILD_TYPE=None \
    -DCMAKE_INSTALL_PREFIX=/usr \
    -DCMAKE_INSTALL_LIBDIR=lib \
    -Wno-dev
  cmake --build build
}

check() {
  ctest --test-dir build --output-on-failure
}

package() {
  DESTDIR="$pkgdir" cmake --install build
}
```

### 2.3 Key Considerations
- `-DCMAKE_BUILD_TYPE=None`: Essential so Arch compiler flags (`CFLAGS`, `CXXFLAGS`) from `/etc/makepkg.conf` are not overridden by CMake's internal `Release` or `Debug` flagsets.
- `-DCMAKE_INSTALL_PREFIX=/usr`: Ensures installation directly into the standard system tree, avoiding `/usr/local`.
- `-DCMAKE_INSTALL_LIBDIR=lib`: Arch uses unified 64-bit lib structure (`/usr/lib`, not `/usr/lib64`).

---

## 3. Meson & Ninja

### 3.1 Project Indicators
- Root file: `meson.build`

### 3.2 Standard Workflow
```bash
makedepends=('meson' 'ninja')

build() {
  arch-meson "$pkgname-$pkgver" build
  meson compile -C build
}

check() {
  meson test -C build --print-errorlogs
}

package() {
  meson install -C build --destdir "$pkgdir"
}
```

### 3.3 Key Considerations
- **`arch-meson` wrapper**: Provided by Arch's `meson` package. Sets standard `--prefix=/usr`, `--libdir=/usr/lib`, `--libexecdir=/usr/lib`, `--sbindir=/usr/bin`, `--buildtype=plain`, and `--wrap-mode=nodownload`.
- If invoking raw `meson setup`:
  ```bash
  meson setup "$pkgname-$pkgver" build \
    --prefix=/usr \
    --libdir=/usr/lib \
    --buildtype=plain \
    --wrap-mode=nodownload
  ```
- `--wrap-mode=nodownload`: Prevents Meson from silently fetching subprojects from the internet during compilation.

---

## 4. Rust & Cargo

### 4.1 Project Indicators
- Root files: `Cargo.toml`, `Cargo.lock`

### 4.2 Standard Workflow
```bash
makedepends=('cargo')

prepare() {
  cd "$pkgname-$pkgver"
  cargo fetch --locked --target "$(rustc -vV | sed -n 's/host: //p')"
}

build() {
  cd "$pkgname-$pkgver"
  export RUSTUP_TOOLCHAIN=stable
  export CARGO_TARGET_DIR=target
  cargo build --frozen --release --all-features
}

check() {
  cd "$pkgname-$pkgver"
  export RUSTUP_TOOLCHAIN=stable
  cargo test --frozen --all-features
}

package() {
  cd "$pkgname-$pkgver"
  install -Dm755 "target/release/$pkgname" "$pkgdir/usr/bin/$pkgname"
  install -Dm644 LICENSE-MIT "$pkgdir/usr/share/licenses/$pkgname/LICENSE-MIT"
}
```

### 4.3 Key Considerations
- `cargo fetch` in `prepare()`: Downloads all crates before entering the offline build sandbox.
- `--frozen`: Ensures Cargo does not modify `Cargo.lock` and forbids network downloads during `build()` and `check()`.
- Do not pass `--target` to `cargo build` in standard packaging unless cross-compiling, as it alters binary output directories.

---

## 5. Python (PEP 517 Standards)

### 5.1 Project Indicators
- Root files: `pyproject.toml`, `setup.py`, `setup.cfg`

### 5.2 Standard Workflow
```bash
depends=('python' 'python-requests')
makedepends=('python-build' 'python-installer' 'python-wheel' 'python-setuptools')
checkdepends=('python-pytest')

build() {
  cd "$pkgname-$pkgver"
  python -m build --wheel --no-isolation
}

check() {
  cd "$pkgname-$pkgver"
  pytest
}

package() {
  cd "$pkgname-$pkgver"
  python -m installer --destdir="$pkgdir" dist/*.whl
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
```

### 5.3 Key Considerations
- `--no-isolation`: Mandatory. Instructs `build` to use system Python packages instead of creating an ephemeral `pip` virtual environment that accesses the internet.
- Build backend in `makedepends`: Identify the backend from `pyproject.toml` (`[build-system] requires = [...]`):
  - `setuptools` $\to$ `python-setuptools`
  - `flit_core` $\to$ `python-flit-core`
  - `hatchling` $\to$ `python-hatchling`
  - `poetry-core` $\to$ `python-poetry-core`

---

## 6. Go (Modules & Hardening)

### 6.1 Project Indicators
- Root files: `go.mod`, `go.sum`

### 6.2 Standard Workflow
```bash
makedepends=('go')

prepare() {
  cd "$pkgname-$pkgver"
  export GOPATH="$srcdir/gopath"
  go mod download -modcacherw
}

build() {
  cd "$pkgname-$pkgver"
  export GOPATH="$srcdir/gopath"
  export CGO_CPPFLAGS="${CPPFLAGS}"
  export CGO_CFLAGS="${CFLAGS}"
  export CGO_CXXFLAGS="${CXXFLAGS}"
  export CGO_LDFLAGS="${LDFLAGS}"
  export GOFLAGS="-buildmode=pie -trimpath -ldflags=-linkmode=external -mod=readonly -modcacherw"

  go build -v -o "$pkgname" ./cmd/"$pkgname"
}

check() {
  cd "$pkgname-$pkgver"
  export GOPATH="$srcdir/gopath"
  export GOFLAGS="-mod=readonly"
  go test -v ./...
}

package() {
  cd "$pkgname-$pkgver"
  install -Dm755 "$pkgname" "$pkgdir/usr/bin/$pkgname"
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
```

### 6.3 Key Considerations
- `-buildmode=pie`: Enables Position Independent Executables for Address Space Layout Randomization (ASLR).
- `-trimpath`: Strips absolute file system paths from compiled binaries (crucial for reproducible builds).
- `-mod=readonly`: Enforces that `go.mod` is not mutated during compilation.
- `-modcacherw`: Ensures downloaded modules in cache have write permissions so `rm -rf "$srcdir"` cleans up properly.

---

## 7. GNU Autotools & Make

### 7.1 Project Indicators
- Files: `configure.ac`, `Makefile.am`, or pre-generated `./configure`

### 7.2 Standard Workflow
```bash
build() {
  cd "$pkgname-$pkgver"
  ./configure \
    --prefix=/usr \
    --sbindir=/usr/bin \
    --sysconfdir=/etc \
    --localstatedir=/var
  make
}

check() {
  cd "$pkgname-$pkgver"
  make check
}

package() {
  cd "$pkgname-$pkgver"
  make DESTDIR="$pkgdir" install
}
```

### 7.3 Key Considerations
- `--sbindir=/usr/bin`: Arch Linux unifies `/bin`, `/sbin`, and `/usr/sbin` into `/usr/bin`.
- `--sysconfdir=/etc`: Ensures configuration files install into `/etc`, not `/usr/etc`.
- Always use `DESTDIR="$pkgdir"` during `make install`.

---

## 8. Prebuilt Binary Repackaging (`-bin`)

### 8.1 Workflow
```bash
pkgname=app-bin
pkgver=1.2.0
pkgrel=1
arch=('x86_64')
provides=("app=$pkgver")
conflicts=('app')
source=("$pkgname-$pkgver.tar.gz::https://example.com/app-$pkgver-linux-x64.tar.gz")

package() {
  install -Dm755 "$srcdir/app" "$pkgdir/usr/bin/app"
  install -Dm644 "$srcdir/LICENSE" "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
```

### 8.2 Invariants for Binary Repackaging
1. Name must end in `-bin` if source code is publicly available.
2. Must set `provides=("original_name=$pkgver")` and `conflicts=('original_name')`.
3. Must verify dynamic library linkage against Arch standard libraries (`readelf -d` / `objdump -p`).

---

## 9. Authoritative References

- [Arch package guidelines: CMake](https://wiki.archlinux.org/title/CMake_package_guidelines)
- [Arch package guidelines: Meson](https://wiki.archlinux.org/title/Meson_package_guidelines)
- [Arch package guidelines: Rust](https://wiki.archlinux.org/title/Rust_package_guidelines)
- [Arch package guidelines: Python](https://wiki.archlinux.org/title/Python_package_guidelines)
- [Arch package guidelines: Go](https://wiki.archlinux.org/title/Go_package_guidelines)
