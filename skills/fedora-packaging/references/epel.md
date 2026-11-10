# EPEL (Extra Packages for Enterprise Linux) Compatibility

Technical reference for packaging and maintaining software for EPEL 8, 9, and 10 on Red Hat Enterprise Linux and CentOS Stream.

---

## 1. What is EPEL?

EPEL is a Fedora Special Interest Group that creates, maintains, and manages a high-quality set of additional packages for Enterprise Linux (RHEL, AlmaLinux, Rocky Linux, CentOS Stream):
- EPEL packages **never** replace or conflict with packages in RHEL base repositories (BaseOS / AppStream).
- EPEL follows the same strict Fedora packaging standards, but operates within older enterprise toolchain constraints.

---

## 2. Common EPEL Compatibility Gotchas

| Feature / Tool | Modern Fedora (Rawhide/f40) | EPEL 8 / EPEL 9 | EPEL Workaround |
|---|---|---|---|
| **`%autorelease` / `%autochangelog`** | Supported natively | EPEL 8 requires `rpmautospec` build macro support | Fallback to `Release: 1%{?dist}` if rpmautospec unavailable |
| **CMake Version** | CMake 3.28+ | EPEL 8 provides CMake 3.20 (or `cmake3`) | Use `BuildRequires: cmake >= 3.20` or conditional macros |
| **Python Runtimes** | Python 3.12 / 3.13 default | EPEL 8 uses Python 3.6 / 3.9 modules | Use versioned Python macros (`python3.9`) |
| **Compiler Hardening** | `-fcf-protection`, `-D_FORTIFY_SOURCE=3` | `-D_FORTIFY_SOURCE=2` | Rely on default `%set_build_flags` without hardcoding |
| **Missing Dependencies** | Extensive Fedora package catalog | Many niche libraries are not in RHEL or EPEL | Must package and maintain missing dependencies in EPEL first |

### Conditional Macro for EPEL in Spec Files:
```spec
%if 0%{?rhel} && 0%{?rhel} <= 8
BuildRequires:  cmake3
%define cmake %cmake3
%define ctest %ctest3
%else
BuildRequires:  cmake >= 3.20
%endif
```
