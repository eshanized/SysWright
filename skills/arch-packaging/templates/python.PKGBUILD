# Maintainer: Your Name <youremail@example.com>
#
# TEMPLATE: Python Package (PEP 517 Standards)
#
# RESEARCH CHECKLIST BEFORE USING THIS TEMPLATE:
# 1. Inspect pyproject.toml [build-system] requires = [...] to identify backend:
#    - setuptools -> python-setuptools
#    - flit_core -> python-flit-core
#    - hatchling -> python-hatchling
#    - poetry-core -> python-poetry-core
# 2. Inspect runtime dependencies in pyproject.toml / setup.cfg.
# 3. Determine if arch is 'any' (pure Python) or 'x86_64' (contains C/Rust extensions).

pkgname=python-<MODULE_NAME>
pkgver=<UPSTREAM_VERSION>
pkgrel=1
pkgdesc="Concise summary under 80 characters without trailing period"
arch=('any')
url="https://<UPSTREAM_URL>"
license=('<SPDX_LICENSE_IDENTIFIER>')
depends=('python')
makedepends=('python-build' 'python-installer' 'python-wheel' 'python-setuptools')
checkdepends=('python-pytest')
source=("$pkgname-$pkgver.tar.gz::$url/archive/v$pkgver.tar.gz")
sha256sums=('<COMPUTE_VIA_sha256sum_OR_updpkgsums>')

build() {
  cd "<SOURCE_DIR_NAME>"
  python -m build --wheel --no-isolation
}

check() {
  cd "<SOURCE_DIR_NAME>"
  pytest
}

package() {
  cd "<SOURCE_DIR_NAME>"
  python -m installer --destdir="$pkgdir" dist/*.whl

  # Install license notice for MIT/BSD or custom licenses:
  # install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
