Name:           example-cmake-app
Version:        1.0.0
Release:        1%{?dist}
Summary:        Modern CMake-based C++ application
License:        Apache-2.0
URL:            https://example.org/project
Source0:        %{url}/releases/download/v%{version}/%{name}-%{version}.tar.xz

BuildRequires:  cmake >= 3.20
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  pkgconfig
BuildRequires:  openssl-devel

%description
Modern C++ application packaged using standardized RPM CMake macros.

%prep
%autosetup -p1

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
%{_datadir}/%{name}/

%changelog
* Mon Jan 15 2024 Packager Name <packager@example.org> - 1.0.0-1
- Initial CMake RPM package
