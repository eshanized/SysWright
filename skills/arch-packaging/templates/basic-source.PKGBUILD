# Maintainer: Your Name <youremail@example.com>
#
# TEMPLATE: Basic GNU Make / Autotools Source Package
#
# RESEARCH CHECKLIST BEFORE USING THIS TEMPLATE:
# 1. Official upstream project URL and release tarball location.
# 2. SPDX License identifier (verify against upstream LICENSE / COPYING).
# 3. Direct runtime dependencies via readelf -d (glibc, shared libraries).
# 4. SHA-256 cryptographic checksum of official source archive.
# 5. Build configuration flags (e.g., ./configure parameters).

pkgname=<PACKAGE_NAME>
pkgver=<UPSTREAM_VERSION>
pkgrel=1
pkgdesc="Concise summary under 80 characters without trailing period"
arch=('x86_64')
url="https://<UPSTREAM_URL>"
license=('<SPDX_LICENSE_IDENTIFIER>')
depends=('glibc')
makedepends=()
source=("$pkgname-$pkgver.tar.gz::$url/releases/download/v$pkgver/$pkgname-$pkgver.tar.gz")
sha256sums=('<COMPUTE_VIA_sha256sum_OR_updpkgsums>')

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

  # If license is MIT, BSD, or custom, install it:
  # install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
