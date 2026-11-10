# RPM Macros: Built-in, Path, and Conditional Evaluation

Technical reference for standard RPM macros, custom macro definition, and conditional build flags.

---

## 1. Built-in Directory Macros

Always use built-in macros instead of hardcoding absolute paths:

| Macro | Path | Typical Value |
|---|---|---|
| `%{_prefix}` | `/usr` | Standard filesystem prefix |
| `%{_bindir}` | `%{_prefix}/bin` | `/usr/bin` |
| `%{_sbindir}` | `%{_prefix}/sbin` | `/usr/sbin` |
| `%{_libdir}` | `%{_exec_prefix}/lib64` | `/usr/lib64` on 64-bit systems |
| `%{_includedir}` | `%{_prefix}/include` | `/usr/include` |
| `%{_sysconfdir}` | `/etc` | Host configuration |
| `%{_sharedstatedir}` | `/var/lib` | Stateful daemon data |
| `%{_localstatedir}` | `/var` | Variable files |
| `%{_datadir}` | `%{_prefix}/share` | Architecture-independent assets |
| `%{_mandir}` | `%{_datadir}/man` | Man pages |
| `%{_unitdir}` | `/usr/lib/systemd/system` | Systemd service units |

---

## 2. Standard Build System Macros

Modern distributions provide build system macros that pass optimal architecture flags:

```spec
# CMake:
%cmake -DENABLE_FEATURE=ON
%cmake_build
%cmake_install
%ctest

# Meson:
%meson -Ddocs=disabled
%meson_build
%meson_install
%meson_test

# Cargo (Rust):
%cargo_prep
%cargo_build
%cargo_install
%cargo_test
```

---

## 3. Conditional Macros and Build Flags (`%bcond`)

Control optional features, tests, or subpackages using `%bcond_with` and `%bcond_without`:

```spec
# Default: enable tests (%bcond_without tests -> with_tests is 1 by default)
%bcond_without tests

# Default: disable experimental feature (%bcond_with -> with_experimental is 0 by default)
%bcond_with experimental

%build
%cmake \
%if %{with experimental}
    -DENABLE_EXPERIMENTAL=ON \
%endif
    -DCMAKE_BUILD_TYPE=Release
%cmake_build

%check
%if %{with tests}
%ctest
%endif
```
- Toggle at build time via `rpmbuild`:
  `rpmbuild -ba --without tests --with experimental myapp.spec`
