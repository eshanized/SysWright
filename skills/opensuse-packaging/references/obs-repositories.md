# Multi-Distribution Target Engineering in OBS

Technical reference for configuring Open Build Service repositories targeting non-openSUSE distributions.

---

## 1. Multi-Distribution Support in OBS

A unique capability of the Open Build Service is its ability to build packages for multiple distinct distributions from a single project:
- **RPM Targets**: openSUSE Tumbleweed, openSUSE Leap, SUSE Linux Enterprise, Fedora, CentOS, RHEL.
- **DEB Targets**: Debian Stable/Testing/Unstable, Ubuntu LTS/Interim.
- **Arch Targets**: Arch Linux (using PKGBUILD recipes).

---

## 2. Conditional Spec Logic for Multi-Distro Targets

When maintaining an RPM spec file built for both openSUSE and Fedora in OBS, use distribution identification macros:

```spec
%if 0%{?suse_version}
BuildRequires:  systemd-rpm-macros
%{?systemd_ordering}
%else
BuildRequires:  systemd
%endif

%if 0%{?fedora}
BuildRequires:  ninja-build
%else
BuildRequires:  ninja
%endif

%build
%if 0%{?suse_version}
%cmake_build
%else
%cmake_build
%endif
```
- `0%{?suse_version}`: Defined on openSUSE / SLE (e.g., `1600` on Tumbleweed, `1560` on Leap 15.6).
- `0%{?fedora}`: Defined on Fedora (e.g., `40`).
- `0%{?rhel}`: Defined on RHEL / CentOS Stream (e.g., `9`).
