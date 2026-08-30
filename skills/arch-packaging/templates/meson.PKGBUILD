# Maintainer: Your Name <youremail@example.com>
#
# TEMPLATE: Meson Project with Ninja
#
# RESEARCH CHECKLIST BEFORE USING THIS TEMPLATE:
# 1. Inspect meson.build: dependency() calls mapping to Arch packages.
# 2. Options in meson_options.txt.
# 3. Test dependencies required for meson test.

pkgname=<PACKAGE_NAME>
pkgver=<UPSTREAM_VERSION>
pkgrel=1
pkgdesc="Concise summary under 80 characters without trailing period"
arch=('x86_64')
url="https://<UPSTREAM_URL>"
license=('<SPDX_LICENSE_IDENTIFIER>')
depends=('glibc')
makedepends=('meson' 'ninja')
checkdepends=()
source=("$pkgname-$pkgver.tar.gz::$url/archive/v$pkgver.tar.gz")
sha256sums=('<COMPUTE_VIA_sha256sum_OR_updpkgsums>')

build() {
  arch-meson "$pkgname-$pkgver" build
  meson compile -C build
}

check() {
  meson test -C build --print-errorlogs
}

package() {
  meson install -C build --destdir "$pkgdir"

  # Install license notice for MIT/BSD or custom licenses:
  # install -Dm644 "$pkgname-$pkgver/LICENSE" "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
