# RPM Package Validation: rpmlint, File Ownership, and Common Errors

Technical reference for static quality linting with rpmlint, file ownership checks, and resolving unpackaged file errors.

---

## 1. Static Package Auditing with `rpmlint`

`rpmlint` is the official static analysis tool for RPM packages. Always run `rpmlint` against the spec file, Source RPM, and all generated binary RPMs:

```bash
rpmlint SPECS/myapp.spec \
        SRPMS/myapp-1.2.3-1.src.rpm \
        RPMS/x86_64/myapp-1.2.3-1.x86_64.rpm
```

### rpmlint Tag Severity:
- **`E:` (Error)**: Severe spec violation, security risk, or broken filesystem path. Must be fixed before submission.
- **`W:` (Warning)**: Potential packaging defect or policy divergence. Should be fixed or explained.

---

## 2. Common RPM Build & Validation Errors

### A. "Installed (but unpackaged) file(s) found"
- **Cause**: Upstream's `make install` installed files into `%{buildroot}`, but those files were omitted from the `%files` section.
- **Remediation**: Either add the paths to `%files`, or remove unwanted files explicitly at the end of `%install`:
  ```spec
  rm -f %{buildroot}%{_libdir}/*.la
  ```

### B. "Unexpanded macro in %files"
- **Cause**: A macro syntax error or undefined macro appears literally in the file list (e.g., `%{_unitdir}` when `systemd-rpm-macros` was not in `BuildRequires`).
- **Remediation**: Add `BuildRequires: systemd-rpm-macros`.

### C. "Explicit-lib-dependency"
- **Cause**: Adding manual `Requires: libfoo.so.1` or `Requires: openssl`.
- **Remediation**: Remove the manual declaration; allow RPM's automatic dependency generator to manage shared library requirements.
