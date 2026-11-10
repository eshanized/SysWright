# Emergency Repository Rollback & Remediation Plan

## Incident Overview
- **Incident ID**: INC-YYYYMMDD-01
- **Affected Repository / Distribution**: [e.g., Ubuntu Noble / Debian Bookworm / Fedora 40]
- **Faulty Package(s)**: [e.g., `libfoo 2.1.0-1`]
- **Severity / Impact**: [e.g., Breaks network daemon on system startup]

---

## 1. Immediate Blast-Radius Containment
1. [ ] Revert active production symlink to last known good snapshot:
   ```bash
   ln -sfn /srv/snapshots/<LAST_GOOD_DATE> /srv/repo/production
   ```
2. [ ] Invalidate edge CDN cache for master metadata indices:
   - APT: `/dists/*/InRelease`, `/dists/*/Release*`
   - DNF/RPM: `/repodata/repomd.xml*`
3. [ ] Halt automated promotion pipelines and lock staging queues.

---

## 2. Remediation Strategy Selection
- [ ] **Strategy A (Fast-Forward Revert - Preferred)**:
  - Package previous stable version with incremented epoch/release (e.g., `1:2.0.9-1` or `2.0.9-2+revert`).
  - Deploy to staging, verify clean upgrade/downgrade behavior, and promote.
- [ ] **Strategy B (Client Pinning & Workaround)**:
  - Issue security bulletin with APT preferences / DNF versionlock instructions:
    ```ini
    Package: libfoo
    Pin: version 2.0.9*
    Pin-Priority: 1001
    ```

---

## 3. Post-Incident Verification
- [ ] Verify test client installs old/reverted package cleanly via `apt-get update && apt-get dist-upgrade` or `dnf distro-sync`.
- [ ] Verify solver reports zero broken dependencies across entire repository pool.
- [ ] Conduct root cause analysis (RCA) on why automated staging gates failed to catch the regression.