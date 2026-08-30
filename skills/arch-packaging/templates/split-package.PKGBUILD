# Maintainer: Your Name <youremail@example.com>
#
# TEMPLATE: Split Package (Shared Library + CLI Tool + Development Headers)
#
# RESEARCH CHECKLIST BEFORE USING THIS TEMPLATE:
# 1. Determine natural package boundaries (library vs binary vs doc vs headers).
# 2. Dependency relationships between subpackages (e.g., tool depends on library).
# 3. Soname provisions for shared library subpackage (provides=('libfoo.so=1-64')).

pkgbase=<PACKAGE_BASE_NAME>
pkgname=('<PACKAGE_BASE_NAME>' 'lib<PACKAGE_BASE_NAME>')
pkgver=<UPSTREAM_VERSION>
pkgrel=1
arch=('x86_64')
url="https://<UPSTREAM_URL>"
license=('<SPDX_LICENSE_IDENTIFIER>')
makedepends=('cmake' 'ninja')
source=("$pkgbase-$pkgver.tar.gz::$url/archive/v$pkgver.tar.gz")
sha256sums=('<COMPUTE_VIA_sha256sum_OR_updpkgsums>')

build() {
  cmake -B build -S "$pkgbase-$pkgver" \
    -G Ninja \
    -DCMAKE_BUILD_TYPE=None \
    -DCMAKE_INSTALL_PREFIX=/usr
  cmake --build build
}

check() {
  ctest --test-dir build --output-on-failure
}

package_<PACKAGE_BASE_NAME>() {
  pkgdesc="CLI utility for $pkgbase"
  depends=("lib$pkgbase=$pkgver-$pkgrel" 'glibc')

  DESTDIR="$pkgdir" cmake --install build
  # Remove libraries and headers to avoid collision with lib package
  rm -rf "$pkgdir/usr/lib"
  rm -rf "$pkgdir/usr/include"
}

package_lib<PACKAGE_BASE_NAME>() {
  pkgdesc="Core shared runtime library for $pkgbase"
  depends=('glibc')
  provides=('lib<PACKAGE_BASE_NAME>.so')

  DESTDIR="$pkgdir" cmake --install build
  # Remove binaries to avoid collision with main package
  rm -rf "$pkgdir/usr/bin"
  rm -rf "$pkgdir/usr/share/man"
}
