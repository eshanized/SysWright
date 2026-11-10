# RPM Build Engineering: rpmbuild, Buildroots, and Debuginfo

Technical reference for building RPMs, managing build directories, and generating debuginfo packages.

---

## 1. The Standard RPM Build Directory Layout

RPM build tools expect a specific directory tree (`~/rpmbuild`):

```text
~/rpmbuild/
├── BUILD/         # Unpacked sources and compilation artifacts
├── BUILDROOT/     # Staged installation root (%{buildroot})
├── RPMS/          # Generated binary RPM packages (.rpm)
│   ├── x86_64/
│   └── noarch/
├── SOURCES/       # Pristine upstream archives and patches
├── SPECS/         # RPM spec files (.spec)
└── SRPMS/         # Generated Source RPM packages (.src.rpm)
```

Create layout with `rpmdevtools`:
```bash
rpmdev-setuptree
```

---

## 2. Essential `rpmbuild` Invocations

```bash
# Build both Source RPM (.src.rpm) and binary RPMs (.rpm)
rpmbuild -ba SPECS/myapp.spec

# Build Source RPM only (.src.rpm)
rpmbuild -bs SPECS/myapp.spec

# Build binary RPMs from an existing Source RPM
rpmbuild --rebuild SRPMS/myapp-1.2.3-1.src.rpm

# Run only up to the %prep stage (useful for testing patches)
rpmbuild -bp SPECS/myapp.spec

# Run only up to the %build stage (useful for debugging compiler errors)
rpmbuild -bc SPECS/myapp.spec
```

---

## 3. Automated Debuginfo and Debugsource Generation

Modern RPM automatically extracts DWARF debug symbols from compiled binaries into separate `-debuginfo` and `-debugsource` subpackages:
- The binary package contains stripped, optimized machine code.
- Debug symbols are stored in `myapp-debuginfo-1.2.3-1.x86_64.rpm` under `/usr/lib/debug/`.
- Original source files are stored in `myapp-debugsource-1.2.3-1.x86_64.rpm` under `/usr/src/debug/`.
- **Rule**: Never manually run `strip` inside `%install`! Doing so clobbers DWARF debug symbols before RPM's automated extraction helpers run, resulting in empty debuginfo packages.
