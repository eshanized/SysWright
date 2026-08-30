# Maintainer: Your Name <youremail@example.com>
#
# TEMPLATE: Rust Project with Cargo
#
# RESEARCH CHECKLIST BEFORE USING THIS TEMPLATE:
# 1. Does Cargo.lock exist in upstream source? (Required for reproducible --frozen builds).
# 2. System libraries linked dynamically by *-sys crates (openssl, sqlite, zlib).
# 3. Binaries produced in target/release/.

pkgname=<PACKAGE_NAME>
pkgver=<UPSTREAM_VERSION>
pkgrel=1
pkgdesc="Concise summary under 80 characters without trailing period"
arch=('x86_64')
url="https://<UPSTREAM_URL>"
license=('<SPDX_LICENSE_IDENTIFIER>')
depends=('glibc')
makedepends=('cargo')
checkdepends=()
source=("$pkgname-$pkgver.tar.gz::$url/archive/v$pkgver.tar.gz")
sha256sums=('<COMPUTE_VIA_sha256sum_OR_updpkgsums>')

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

  # Install license notice for MIT/BSD or custom licenses:
  # install -Dm644 LICENSE-MIT "$pkgdir/usr/share/licenses/$pkgname/LICENSE-MIT"
}
