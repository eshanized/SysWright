# Fedora Spec Conventions: rpmautospec, %autorelease, and %autochangelog

Technical reference for modern Fedora spec file conventions and automated release/changelog generation.

---

## 1. rpmautospec Overview

Historically, packagers manually incremented `Release: 1%{?dist}` and manually edited `%changelog` on every commit. In modern Fedora, `rpmautospec` automates this process directly from git history:

```spec
Name:           example-tool
Version:        1.2.3
Release:        %autorelease
Summary:        System monitoring tool
License:        MIT
URL:            https://example.org/tool
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  meson

%description
Example monitoring tool using modern Fedora rpmautospec conventions.

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
%{_bindir}/%{name}

%changelog
%autochangelog
```

---

## 2. How `%autorelease` and `%autochangelog` Function

- **`Release: %autorelease`**: When processed by Koji or `rpmautospec`, expands dynamically to the commit count and distribution tag (e.g., `1.fc40`).
- **`%changelog \n %autochangelog`**: Automatically parses git commit messages in Fedora dist-git and populates the `%changelog` section upon building the SRPM.
- Commits with `[skip changelog]` or minor merge commits are omitted from the generated changelog automatically.
