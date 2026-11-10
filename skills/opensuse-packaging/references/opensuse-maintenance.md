# openSUSE Maintenance, Factory Submission, and openQA

Technical reference for Factory submission reviews, openQA integration, and maintenance backports.

---

## 1. The Factory Submission Lifecycle

`openSUSE:Factory` is the rolling development trunk:
1. Maintainer submits an update via `osc submitrequest` (`osc sr`).
2. An automated OBS reviewer bot checks:
   - Does the package build cleanly across all architectures?
   - Does `rpmlint` report new errors?
   - Are changes documented in `<package>.changes`?
3. Humans in the openSUSE staging team review the diff and accept it into a staging project.
4. **openQA Automated Testing**:
   - The entire openSUSE distribution is built into ISO images and booted across dozens of virtualized scenarios in **openQA** (`openqa.opensuse.org`).
   - If graphical desktop, network installation, or core services break, the staging project is rejected.
   - Once openQA yields green test results, the snapshot is released as the next openSUSE Tumbleweed snapshot.

---

## 2. Documenting Changes via `<package>.changes`

openSUSE does not put changelogs inside the `.spec` file. Instead, it uses a separate `<package>.changes` file:
```text
-------------------------------------------------------------------
Mon Jan 15 12:00:00 UTC 2024 - Packager Name <packager@example.org>

- Update to version 1.2.4:
  * Fix memory leak in connection cleanup handler (bsc#1234567).
  * Improve performance of packet parsing by 15%.
- Drop obsolete patch fix-build.patch merged upstream.
```
- Generate a new entry automatically using:
  ```bash
  osc vc -m "Update to 1.2.4"
  ```
