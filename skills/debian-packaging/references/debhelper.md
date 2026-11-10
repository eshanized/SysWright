# Modern Debhelper Architecture: dh, dh-compat 13, and Overrides

Technical reference for debhelper sequencing in `debian/rules`, buildsystem overrides, and compatibility levels.

---

## 1. The Modern Minimal `debian/rules`

In modern Debian packaging, `debian/rules` is an executable Makefile using the `dh` sequencer:

```makefile
#!/usr/bin/make -f
export DH_VERBOSE = 1

# Enable full compiler hardening flags (PIE, RELRO, bindnow, fortify)
export DEB_BUILD_MAINT_OPTIONS = hardening=+all

%:
	dh $@
```

### The `dh $@` Pipeline:
When `dpkg-buildpackage` invokes `debian/rules binary`, `dh` executes an automated pipeline of debhelper helpers:
1. `dh_auto_clean`
2. `dh_auto_configure` (autodetects CMake, Meson, Autotools, Python, Perl)
3. `dh_auto_build`
4. `dh_auto_test` (runs `ctest`, `ninja test`, `make test`)
5. `dh_auto_install` (installs to `debian/tmp/` with `DESTDIR`)
6. `dh_install` (places files according to `debian/*.install`)
7. `dh_installdocs`, `dh_installman`, `dh_installsystemd`
8. `dh_strip` (strips debug symbols into separate automatic dbgsym packages)
9. `dh_makeshlibs`, `dh_shlibdeps`
10. `dh_gencontrol`, `dh_md5sums`, `dh_builddeb`

---

## 2. Custom Overrides in `debian/rules`

Override specific steps by defining target `override_dh_<step>`:

### Overriding CMake Configuration:
```makefile
override_dh_auto_configure:
	dh_auto_configure -- \
		-DENABLE_SYSTEM_LIBS=ON \
		-DBUILD_TESTING=ON \
		-DCMAKE_BUILD_TYPE=Release
```

### Skipping Test Suite when Cross-Compiling:
```makefile
override_dh_auto_test:
ifeq (,$(filter nocheck,$(DEB_BUILD_OPTIONS)))
	dh_auto_test
endif
```

---

## 3. Debhelper Compatibility Levels: `debhelper-compat`

Compatibility levels define default behavior across debhelper helpers:
- Declare in `debian/control`:
  ```ini
  Build-Depends: debhelper-compat (= 13), ...
  ```
- **Compat Level 13 features**:
  - `dh_missing --fail-missing` is enabled by default (fails build if upstream installed files in `debian/tmp` that are not packaged in any binary).
  - Modern systemd unit handling (`dh_installsystemd` replaces obsolete `dh_systemd_enable`).
  - Strict security buildflags and reproducible build settings enabled by default.
