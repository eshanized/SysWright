Name:           libexample
Version:        1.0.0
Release:        1%{?dist}
Summary:        Shared library and development toolkit
License:        Apache-2.0
URL:            https://example.org/project
Source0:        %{url}/releases/download/v%{version}/%{name}-%{version}.tar.xz

BuildRequires:  gcc-c++
BuildRequires:  meson >= 0.58
BuildRequires:  ninja-build

%description
Core shared library package providing runtime utilities.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Header files and development libraries for building applications against %{name}.

%prep
%autosetup -p1

%build
%meson
%meson_build

%install
%meson_install

%check
%meson_test

%files
%license LICENSE
%doc README.md
%{_libdir}/libexample.so.1*

%files devel
%{_includedir}/example/
%{_libdir}/libexample.so
%{_libdir}/pkgconfig/example.pc

%changelog
* Mon Jan 15 2024 Packager Name <packager@example.org> - 1.0.0-1
- Initial split library and devel RPM package
