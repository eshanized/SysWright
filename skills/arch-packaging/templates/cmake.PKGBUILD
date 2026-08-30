# Maintainer: Your Name <youremail@example.com>
#
# TEMPLATE: CMake Project with Ninja Generator
#
# RESEARCH CHECKLIST BEFORE USING THIS TEMPLATE:
# 1. Project build dependencies (CMakeLists.txt: find_package calls).
# 2. Runtime library linkages (DT_NEEDED).
# 3. Custom CMake options (-DBUILD_SHARED_LIBS, -DUSE_SYSTEM_*, etc.).
# 4. Correct license installation path.

pkgname=<PACKAGE_NAME>
pkgver=<UPSTREAM_VERSION>
pkgrel=1
pkgdesc="Concise summary under 80 characters without trailing period"
arch=('x86_64')
url="https://<UPSTREAM_URL>"
license=('<SPDX_LICENSE_IDENTIFIER>')
depends=('glibc')
makedepends=('cmake' 'ninja')
checkdepends=()
source=("$pkgname-$pkgver.tar.gz::$url/archive/v$pkgver.tar.gz")
sha256sums=('<COMPUTE_VIA_sha256sum_OR_updpkgsums>')

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

  # Install license notice for MIT/BSD or custom licenses:
  # install -Dm644 "$pkgname-$pkgver/LICENSE" "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
