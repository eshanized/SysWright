# osc: The Open Build Service Command-Line Client

Technical reference for working with Open Build Service packages and repositories using `osc`.

---

## 1. What is osc?

`osc` is the official CLI client for the Open Build Service (OBS). It combines the capabilities of `git`, `subversion`, and `rpmbuild`:
- Checkouts working directories of packages from remote OBS projects.
- Performs clean, isolated local builds on your workstation.
- Submits merge requests (Submit Requests / SR) back to official distribution trees (`openSUSE:Factory`).

---

## 2. Essential osc Commands

```bash
# 1. Branch a package from openSUSE:Factory to your personal home project
osc branch openSUSE:Factory myapp

# 2. Checkout your branched package to a local working directory
osc checkout home:myuser:branches:openSUSE:Factory/myapp
cd home:myuser:branches:openSUSE:Factory/myapp

# 3. Add or update files in the package directory
osc status
osc add myapp-1.2.4.tar.xz
osc rm myapp-1.2.3.tar.xz

# 4. Run a clean local build targeting openSUSE Tumbleweed
osc build openSUSE_Tumbleweed x86_64 myapp.spec

# 5. Commit changes back to your remote OBS project
osc commit -m "Update to 1.2.4"

# 6. Check remote build status across all architectures and distributions
osc results

# 7. View build failure log for a specific repository
osc buildlog openSUSE_Tumbleweed x86_64

# 8. Submit changes back to openSUSE:Factory for inclusion in the distribution
osc submitrequest -m "Update to 1.2.4: fixes CVE-2024-001"
```
