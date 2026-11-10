# RPM Spec File Anatomy & Section Reference

Comprehensive technical reference for authoring and structuring `.spec` build descriptions.

---

## 1. Structure of an RPM Spec File

An RPM spec file consists of a Preamble followed by sequentially executed build sections:

```spec
Name:           example-app
Version:        1.2.3
Release:        1%{?dist}
Summary:        High-performance network processing utility
License:        Apache-2.0
URL:            https://example.org/project
Source0:        %{url}/releases/download/v%{version}/%{name}-%{version}.tar.xz
Patch0:         0001-fix-buffer-overflow.patch

BuildRequires:  cmake >= 3.20
BuildRequires:  gcc-c++
BuildRequires:  openssl-devel
BuildRequires:  pkgconfig

Requires:       ca-certificates

%description
A comprehensive multi-line description explaining the utility,
its architecture, and capabilities.

%prep
%autosetup -p1

%build
%cmake -DENABLE_TESTING=ON
%cmake_build

%install
%cmake_install

%check
%ctest

%files
%license LICENSE
%doc README.md
%{_bindir}/example-app
%{_mandir}/man1/example-app.1*

%changelog
* Mon Jan 15 2024 Packager Name <packager@example.org> - 1.2.3-1
- Initial RPM release
```

---

## 2. Core Build Sections Explained

### `%prep`:
Prepares the source tree before building:
- `%autosetup -p1`: Modern macro that extracts `Source0`, changes into the directory, and applies all declared `Patch` files using `-p1`.

### `%build`:
Compiles the application inside the build tree:
- Invokes build systems using standardized macros (`%cmake_build`, `%meson_build`, `%make_build`).

### `%install`:
Staged installation phase:
- Cleans and populates `%{buildroot}` (e.g., `~/rpmbuild/BUILDROOT/pkgname-1.0-1.x86_64`).
- Must strictly use `DESTDIR=%{buildroot}`.

### `%check`:
Automated test suite execution:
- Executes unit and integration tests (`%ctest`, `%meson_test`, `make test`).
- A test failure immediately halts the RPM build.

### `%files`:
Defines file manifest packaged into the binary RPM:
- `%license <file>`: Installs license into `/usr/share/licenses/<pkg>/`.
- `%doc <file>`: Installs documentation into `/usr/share/doc/<pkg>/`.
- `%config(noreplace) <file>`: Marks file in `/etc/` as a configuration file; prevents overwriting modified configurations on package upgrade.

---

## 3. Subpackages (`%package`)

Split packages (e.g., separating shared libraries or developer headers):
```spec
%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Header files and static libraries for building against %{name}.

%files devel
%{_includedir}/%{name}/
%{_libdir}/lib%{name}.so
```
*Note: `%{?_isa}` ensures that `devel` requires the exact same architecture binary (e.g., `x86_64` requires `x86_64`).*
