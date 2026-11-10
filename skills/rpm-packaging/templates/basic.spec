Name:           example-app
Version:        1.0.0
Release:        1%{?dist}
Summary:        Basic command-line utility
License:        Apache-2.0
URL:            https://example.org/project
Source0:        %{url}/releases/download/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  make

%description
A simple command-line utility conforming to standard RPM spec file conventions.

%prep
%autosetup -p1

%build
%make_build

%install
%make_install PREFIX=%{_prefix}

%check
make check

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1*

%changelog
* Mon Jan 15 2024 Packager Name <packager@example.org> - 1.0.0-1
- Initial RPM package
