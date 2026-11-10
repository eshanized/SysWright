# Repository Rollback, Remediation & Disaster Recovery

When a critical defect, packaging regression, or security compromise slips into a published repository, immediate rollback and client remediation are required.

---

## 1. Why Removing Packages Can Break Clients

In package management, simply deleting a bad package file from a repository directory (`rm bad-pkg.rpm`) without proper planning creates severe side effects:
1. **Broken Dependency Trees**: Other packages depending on the bad package now fail solver resolution.
2. **Client Cache Inconsistency**: Clients with the old index will attempt to download the deleted package and receive `404 Not Found`.
3. **Clients Already Updated**: Removing the package does NOT downgrade clients that have already installed it. APT and DNF will not automatically revert to an older version without epoch bumps or explicit commands.

---

## 2. Emergency Rollback Strategies

### Strategy A: The "Epoch Bump" / Fast-Forward Fix (Recommended)
Package managers strictly prioritize higher versions. If `myapp-1.2.3` introduces a regression:
- Package upstream `myapp-1.2.2` with an increased package release or epoch:
  - Example: `myapp-1.2.2+revert1` or `1:1.2.2-1`.
  - In Debian/Ubuntu/Fedora, `1:1.2.2` is considered newer than `0:1.2.3` and all clients will automatically downgrade during the next routine update.

### Strategy B: Repository Snapshot Reversion
If an entire repository update is contaminated:
1. Re-point the web server / CDN symlink to the previous valid snapshot timestamp:
   ```bash
   ln -sfn /srv/snapshots/2026-04-01 /srv/repo/production
   ```
2. Invalidate CDN cache for `InRelease` or `repomd.xml`.
3. Issue an administrative notice for affected clients to run:
   ```bash
   # Debian/Ubuntu
   apt-get update && apt-get --allow-downgrades install ...
   # Fedora
   dnf distro-sync
   ```

---

## 3. Quarantining Compromised or Malicious Packages

If a package is suspected of supply-chain tampering:
1. **Revoke Repository Signature**: If signing keys were compromised, immediately revoke the subkey and publish an emergency keyring update.
2. **Yanking from Pool**: Remove package from pool and regenerate signed indices immediately.
3. **Blacklisting / Conflicts**: Push an emergency dummy package with a higher version that conflicts with the compromised artifact, or use package manager pinning to prohibit installation.