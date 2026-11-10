# openSUSE Spec File Conventions & Macros

Technical reference for openSUSE RPM spec macros, systemd service macros, and build wrappers.

---

## 1. Systemd Macros in openSUSE

openSUSE uses `%service_*` macros for systemd service lifecycle management (replacing Fedora's `%systemd_*`):

```spec
BuildRequires:  systemd-rpm-macros
%{?systemd_ordering}

%post
%service_add_post mydaemon.service

%pre
%service_add_pre mydaemon.service

%preun
%service_del_preun mydaemon.service

%postun
%service_del_postun mydaemon.service
```

---

## 2. Compilation and Installation Macros

| Task | openSUSE Macro | Fedora Macro Equivalent |
|---|---|---|
| Configure CMake | `%cmake -DENABLE_TESTS=ON` | `%cmake -DENABLE_TESTS=ON` |
| Build CMake | `%cmake_build` | `%cmake_build` |
| Install CMake | `%cmake_install` | `%cmake_install` |
| Configure Meson | `%meson` | `%meson` |
| Build Meson | `%meson_build` | `%meson_build` |
| Install Meson | `%meson_install` | `%meson_install` |
| Standard Makefile Install | `%make_install` | `%make_install` |

---

## 3. The openSUSE `%check` Phase

Always execute tests during `%check`:
```spec
%check
%ctest
```
*Note: In openSUSE, `%ctest` runs `ctest --output-on-failure --force-new-ctest-process -j%{?_smp_mflags}` by default.*
