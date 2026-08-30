# Maintainer: Your Name <youremail@example.com>
#
# TEMPLATE: VCS Git Development Package (-git)
#
# RESEARCH CHECKLIST BEFORE USING THIS TEMPLATE:
# 1. Authoritative git repository URL.
# 2. Upstream tagging convention (to format pkgver() properly).
# 3. Base package name that this package provides and conflicts with.

pkgname=<PACKAGE_NAME>-git
pkgver=<INITIAL_STUB_VERSION_AUTO_UPDATED_BY_PKGVER>
pkgrel=1
pkgdesc="Concise summary under 80 characters without trailing period (git development branch)"
arch=('x86_64')
url="https://<UPSTREAM_URL>"
license=('<SPDX_LICENSE_IDENTIFIER>')
depends=('glibc')
makedepends=('git')
provides=('<PACKAGE_NAME>=$pkgver')
conflicts=('<PACKAGE_NAME>')
source=("$pkgname::git+https://<GIT_REPOSITORY_URL>#branch=main")
sha256sums=('SKIP')

pkgver() {
  cd "$pkgname"
  # Generates monotonic version string: <tag>.r<commits_since_tag>.g<abbreviated_hash>
  git describe --long --tags --abbrev=7 2>/dev/null | sed 's/\([^-]*-g\)/r\1/;s/-/./g' ||
    printf "r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short=7 HEAD)"
}

build() {
  cd "$pkgname"
  # Execute upstream compilation command (e.g. make / cmake / meson / cargo)
  make
}

check() {
  cd "$pkgname"
  make test
}

package() {
  cd "$pkgname"
  make DESTDIR="$pkgdir" install

  # Install license notice for MIT/BSD or custom licenses:
  # install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
