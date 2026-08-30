# Maintainer: Your Name <youremail@example.com>
#
# TEMPLATE: Prebuilt Binary Distribution Package (-bin)
#
# RESEARCH CHECKLIST BEFORE USING THIS TEMPLATE:
# 1. Is source code available? If open-source, prefer building from source; only use -bin
#    if build times or proprietary restrictions prevent compilation.
# 2. Inspect ELF dynamic linkages with readelf -d to declare all runtime dependencies.
# 3. Verify license terms permit binary redistribution.

pkgname=<PACKAGE_NAME>-bin
pkgver=<UPSTREAM_VERSION>
pkgrel=1
pkgdesc="Concise summary under 80 characters without trailing period (prebuilt binary)"
arch=('x86_64')
url="https://<UPSTREAM_URL>"
license=('<SPDX_LICENSE_OR_LicenseRef-Custom>')
depends=('glibc')
provides=('<PACKAGE_NAME>=$pkgver')
conflicts=('<PACKAGE_NAME>')
source=(
  "$pkgname-$pkgver.tar.gz::https://<UPSTREAM_BINARY_DOWNLOAD_URL>"
  "LICENSE::$url/LICENSE"
)
sha256sums=(
  '<COMPUTE_VIA_sha256sum_OR_updpkgsums>'
  '<COMPUTE_VIA_sha256sum_OR_updpkgsums>'
)

package() {
  install -Dm755 "$srcdir/<BINARY_NAME>" "$pkgdir/usr/bin/<PACKAGE_NAME>"
  install -Dm644 "$srcdir/LICENSE" "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
