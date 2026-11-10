Name:           example-fedora-pkg
Version:        1.0.0
Release:        %autorelease
Summary:        Fedora-compliant system utility
License:        Apache-2.0
URL:            https://example.org/project
Source0:        %{url}/releases/download/v%{version}/%{name}-%{version}.tar.xz

BuildRequires:  cmake >= 3.20
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  pkgconfig
BuildRequires:  openssl-devel

%description
A comprehensive system utility packaged in strict compliance with the
Fedora Packaging Guidelines, utilizing SPDX licensing, unbundled system
libraries, and rpmautospec macros.

%prep
%autosetup -p1
# Strict Unbundling Mandate: remove any third-party bundled dependencies
# rm -rf third_party/bundled_lib

%build
%cmake -G Ninja -DENABLE_TESTING=ON
%cmake_build

%install
%cmake_install

%check
%ctest

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1*

%changelog
%autochangelog
