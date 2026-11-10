#
# spec file for package myapp
#
# Copyright (c) 2026 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#

Name:           myapp
Version:        1.2.3
Release:        0
Summary:        High-performance systems utility for openSUSE
License:        Apache-2.0
Group:          System/Management
URL:            https://example.org/myapp
Source0:        https://example.org/releases/%{name}-%{version}.tar.xz
Source1:        myapp.service

BuildRequires:  cmake >= 3.20
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(openssl)
%{?systemd_ordering}

%description
myapp is a robust systems monitoring daemon designed for openSUSE
Tumbleweed and SUSE Linux Enterprise / openSUSE Leap.

%prep
%autosetup -p1

%build
%cmake
%cmake_build

%install
%cmake_install
install -D -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/myapp.service

%check
%ctest

%pre
%service_add_pre myapp.service

%post
%service_add_post myapp.service

%preun
%service_del_preun myapp.service

%postun
%service_del_postun myapp.service

%files
%license LICENSE
%doc README.md
%{_bindir}/myapp
%{_unitdir}/myapp.service
%{_mandir}/man1/myapp.1%{?ext_man}

%changelog
