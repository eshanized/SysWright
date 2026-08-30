# Maintainer: Your Name <youremail@example.com>
#
# TEMPLATE: Package with Systemd Service, Patch, & Sysusers Integration
#
# RESEARCH CHECKLIST BEFORE USING THIS TEMPLATE:
# 1. Systemd unit directives (ProtectSystem=strict, DynamicUser=yes vs sysusers.d).
# 2. Configuration file defaults and backup=() declarations.
# 3. Patch provenance (upstream PR / commit URL).

pkgname=<PACKAGE_NAME>
pkgver=<UPSTREAM_VERSION>
pkgrel=1
pkgdesc="Concise summary under 80 characters without trailing period"
arch=('x86_64')
url="https://<UPSTREAM_URL>"
license=('<SPDX_LICENSE_IDENTIFIER>')
depends=('glibc')
makedepends=()
backup=('etc/<PACKAGE_NAME>/<PACKAGE_NAME>.conf')
source=(
  "$pkgname-$pkgver.tar.gz::$url/archive/v$pkgver.tar.gz"
  "0001-fix-default-config-path.patch"
  "$pkgname.service"
  "$pkgname.sysusers"
  "$pkgname.tmpfiles"
)
sha256sums=(
  '<COMPUTE_VIA_sha256sum_OR_updpkgsums>'
  '<COMPUTE_VIA_sha256sum_OR_updpkgsums>'
  '<COMPUTE_VIA_sha256sum_OR_updpkgsums>'
  '<COMPUTE_VIA_sha256sum_OR_updpkgsums>'
  '<COMPUTE_VIA_sha256sum_OR_updpkgsums>'
)

prepare() {
  cd "$pkgname-$pkgver"
  # Apply downstream or backported patch
  patch -Np1 -i "$srcdir/0001-fix-default-config-path.patch"
}

build() {
  cd "$pkgname-$pkgver"
  make
}

check() {
  cd "$pkgname-$pkgver"
  make test
}

package() {
  cd "$pkgname-$pkgver"
  make DESTDIR="$pkgdir" install

  # Install systemd service unit to /usr/lib/systemd/system/ (NEVER /etc/systemd/system/)
  install -Dm644 "$srcdir/$pkgname.service" "$pkgdir/usr/lib/systemd/system/$pkgname.service"

  # Install declarative user creation definition
  install -Dm644 "$srcdir/$pkgname.sysusers" "$pkgdir/usr/lib/sysusers.d/$pkgname.conf"

  # Install volatile directory creation definition
  install -Dm644 "$srcdir/$pkgname.tmpfiles" "$pkgdir/usr/lib/tmpfiles.d/$pkgname.conf"

  # Install default configuration into /etc
  install -Dm644 config.conf "$pkgdir/etc/$pkgname/$pkgname.conf"

  # Install license notice for MIT/BSD or custom licenses:
  # install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
