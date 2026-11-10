# openSUSE Packaging Guidelines: Standards, Policies, and Libraries

Technical reference for conforming to openSUSE Packaging Guidelines, license formats, and shared library policies.

---

## 1. Core openSUSE Packaging Standards

openSUSE packages adhere to distribution-specific RPM standards documented on the openSUSE wiki:
- **Licensing**: Uses SPDX license identifiers (`License: Apache-2.0`). Non-free packages belong in `openSUSE:Factory:NonFree`.
- **Package Naming**: Standard application packages match the upstream name in lowercase.
- **Shared Library Policy**:
  - openSUSE enforces strict **Shared Library Packaging Policy**.
  - A shared library package MUST be named strictly after the soname of the library: e.g., `libfoo1` for `libfoo.so.1`.
  - Development headers must be packaged separately in `libfoo-devel`.

---

## 2. Dependencies and Capability Syntax

openSUSE heavily uses declarative pkgconfig dependencies:
```spec
BuildRequires:  pkgconfig
BuildRequires:  pkgconfig(openssl) >= 3.0
BuildRequires:  pkgconfig(zlib)
```
- By using `pkgconfig(name)`, the spec file depends on the exact virtual capability provided by whichever package ships `/usr/lib64/pkgconfig/name.pc`, decoupling the spec from specific distribution package names.
