# Debian Policy Manual Standards & Principles

Comprehensive reference for conforming to the Debian Policy Manual, Filesystem Hierarchy Standard (FHS), and package states.

---

## 1. The Debian Social Contract & DFSG

All software packaged for Debian `main` must adhere strictly to the **Debian Free Software Guidelines (DFSG)**:
1. Free Redistribution.
2. Source Code Inclusion.
3. Allowance of Modifications and Derived Works.
4. Integrity of The Author's Source Code (permits patch requirements).
5. No Discrimination Against Persons or Groups.
6. No Discrimination Against Fields of Endeavor (commercial use permitted).
7. Distribution of License.
8. License Must Not Be Specific to Debian.
9. License Must Not Contaminate Other Software.

### Archive Sections:
- **`main`**: 100% DFSG-compliant software that requires only DFSG-compliant software to build and run.
- **`contrib`**: DFSG-compliant software that depends on non-free software.
- **`non-free`**: Software that fails one or more DFSG guidelines.
- **`non-free-firmware`** (Debian 12+): Hardware firmware blobs separated from generic non-free software.

---

## 2. Filesystem Hierarchy Standard (FHS) in Debian

Debian packages must install files in standardized paths:
- Executables: `/usr/bin/` (user binaries), `/usr/sbin/` (system administration). Never install custom binaries directly into `/bin` or `/sbin` (Debian uses merged `/usr`).
- Shared Libraries: `/usr/lib/<triplet>/` (e.g., `/usr/lib/x86_64-linux-gnu/`).
- Header files: `/usr/include/<triplet>/` or `/usr/include/`.
- Configuration: `/etc/<package>/`. Configuration files must be managed as `conffiles`.
- Architecture-independent shared data: `/usr/share/<package>/`.
- Documentation: `/usr/share/doc/<package>/` (must include `copyright` and `changelog.Debian.gz`).
- Man pages: `/usr/share/man/man[1-8]/<binary>.[1-8].gz`. Every binary in `/usr/bin` or `/usr/sbin` MUST have a manpage!

---

## 3. Configuration Management: Conffiles

Files in `/etc/` are marked as `conffiles` by dpkg:
- When a user modifies a conffile, package upgrades must NOT overwrite the user's modifications silently.
- dpkg prompts the user during `dpkg --configure` if both the upstream maintainer and local user modified the file.
- Maintainer scripts (`postinst`) must never edit conffiles directly using `sed` or string appending; use `ucf` (Update Configuration File) if dynamic configuration generation is needed.
