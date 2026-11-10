# Shared Library ABI Transitions & Soname Bumps

Shared libraries provide binary interfaces (ABI) to consuming applications. Changing an ABI without proper packaging coordination breaks every linked application on the operating system.

---

## 1. What Constitutes an ABI Break?

An ABI break occurs when an existing application compiled against library version $N$ fails to execute properly against library version $N+1$ without recompilation:
- Removing an exported function or global variable.
- Changing function signature (adding/removing parameters, changing parameter types).
- Changing struct layout (adding fields, reordering fields, changing struct size).
- Changing enum values or calling conventions.

---

## 2. Detecting ABI Changes with `abi-compliance-checker`

Always verify shared library ABI compatibility before a release:

```bash
# Generate ABI dump of old version
abi-dumper libfoo.so.1.0 -o libfoo-1.0.dump -lver 1.0

# Generate ABI dump of new version
abi-dumper libfoo.so.2.0 -o libfoo-2.0.dump -lver 2.0

# Compare ABIs
abi-compliance-checker -l libfoo -old libfoo-1.0.dump -new libfoo-2.0.dump
```

If the report indicates `Verdict: INCOMPATIBLE`, you **MUST** bump the SONAME.

---

## 3. The Soname Bump & Transition Workflow

When changing from `libfoo.so.1` to `libfoo.so.2`:

```text
[ libfoo1 (SONAME 1) ]             [ libfoo2 (SONAME 2) ]
        ▲                                  ▲
        │                                  │
[ app-a, app-b ] (Rebuild against libfoo2) │
        │                                  │
        └───────────────►──────────────────┘
```

### Steps for Maintainers:
1. **Rename Binary Package**:
   - In Debian/Ubuntu: Package name changes from `libfoo1` to `libfoo2`.
   - In openSUSE: Package name changes from `libfoo1` to `libfoo2`.
   - In Fedora: Spec file provides `libfoo` with updated `%files` containing `libfoo.so.2*`.
2. **Co-Installability**:
   `libfoo1` and `libfoo2` must be co-installable (they must not place conflicting files in `/usr/lib/` or `/usr/share/`). Development headers (`libfoo-dev` / `libfoo-devel`) can only link to one version at a time.
3. **Coordinated Rebuilds**:
   File rebuild tickets for all reverse dependencies (`apt-cache rdepends libfoo1` or `dnf repoquery --whatrequires libfoo.so.1`) to recompile against the new soname.
4. **Deprecate Old Library**:
   Once all reverse dependencies are rebuilt against `libfoo2`, drop `libfoo1` from the distribution repository.