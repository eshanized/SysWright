# Maintainer: Your Name <youremail@example.com>
#
# TEMPLATE: Go Project (Modules & Hardened Binary)
#
# RESEARCH CHECKLIST BEFORE USING THIS TEMPLATE:
# 1. Does go.mod and go.sum exist?
# 2. Main package location (e.g., ./cmd/<name> or .).
# 3. Dynamic C library dependencies (CGO).

pkgname=<PACKAGE_NAME>
pkgver=<UPSTREAM_VERSION>
pkgrel=1
pkgdesc="Concise summary under 80 characters without trailing period"
arch=('x86_64')
url="https://<UPSTREAM_URL>"
license=('<SPDX_LICENSE_IDENTIFIER>')
depends=('glibc')
makedepends=('go')
checkdepends=()
source=("$pkgname-$pkgver.tar.gz::$url/archive/v$pkgver.tar.gz")
sha256sums=('<COMPUTE_VIA_sha256sum_OR_updpkgsums>')

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

  # Install license notice for MIT/BSD or custom licenses:
  # install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
