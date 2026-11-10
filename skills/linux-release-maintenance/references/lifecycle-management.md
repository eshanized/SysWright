# Software Lifecycle Management & Deprecation Policies

Long-term software maintenance requires managing version lifecycles, defining support phases, and executing orderly deprecation and end-of-life (EOL) transitions.

---

## 1. Standard Support Phases

```text
[ Active Development ] ──► [ Maintenance / LTS ] ──► [ Security Only ] ──► [ End of Life (EOL) ]
   (Features + Bugs)           (Bugs + Security)          (CVEs Only)              (Archived)
```

1. **Active Development Phase**:
   - Upstream main branch. New features, architectural refactoring, dependency updates.
2. **Maintenance / LTS Phase**:
   - Stable branch (e.g., Ubuntu LTS, Debian Stable, RHEL). Bug fixes, driver hardware enablement, minor performance improvements. No breaking ABI changes.
3. **Security-Only Phase**:
   - Only critical security vulnerabilities (CVEs) and severe data-loss bugs backported.
4. **End of Life (EOL)**:
   - Branch closed. No further patches, builds, or security advisories issued. Repositories archived or moved to obsolete mirrors.

---

## 2. Orderly Deprecation & Sunsetting

When a feature, binary interface, or software package is scheduled for retirement:

1. **Advance Warning**: Announce deprecation at least one full release cycle prior to removal.
2. **Compiler / Runtime Warnings**:
   - Use `__attribute__((deprecated("Use new_function() instead")))` in C/C++ headers.
   - Emit runtime warnings to stderr or systemd journal.
3. **Migration Guide**: Publish explicit documentation explaining how to migrate to the replacement library or tool.
4. **Transitional Packages**:
   - In Debian/Ubuntu/RPM, use empty transitional meta-packages (`Depends: new-app`) that smoothly migrate users to the new package during upgrade before retiring the old package name.