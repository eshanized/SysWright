# Security Policy: Linux Engineering

## 1. Security Philosophy

**Linux Engineering** operates at the intersection of AI coding agents and Linux systems engineering (including kernel, driver, packaging, and init systems development). Because systems operations carry inherent operational risks, our architecture is built around strict isolation, privilege separation, and verifiable safety tiers.

---

## 2. Operational Safety Model

All workflows and skills must comply with the **Four-Tier Operational Safety Model** defined in [references/safety-policy.md](references/safety-policy.md):

- **Tier 0 (Diagnostics)**: Read-only inspection (`cat`, `uname`, `systemd-analyze verify`, `readelf`). Permitted autonomously.
- **Tier 1 (Workspace Development)**: Compiling and editing code strictly inside the declared workspace (`cargo build`, `meson compile`). Permitted autonomously within declared scope.
- **Tier 2 (Clean Sandboxes)**: Ephemeral clean chroot package builds (`pkgctl build --clean`) and QEMU microVM boots. Permitted with isolation checks.
- **Tier 3 (Host Mutating / Privileged)**: Operations involving `sudo`, host package modification (`pacman -S`, `apt`), kernel module loading (`modprobe`, `insmod`), bootloader edits (`efibootmgr`, `/boot`), or disk partitioning (`fdisk`, `dd`). **Autonomous execution is strictly prohibited; explicit human confirmation, dry-run display, and a rollback plan are mandatory.**

---

## 3. Handling Untrusted Build Artifacts & Repositories

1. **AUR and Third-Party Sources**: Community `PKGBUILD` files and third-party code must be inspected in read-only mode and validated against SHA-256 checksums or maintainer PGP signatures before build execution.
2. **Container Isolation Warning**: Standard containers share the host Linux kernel. Never test untrusted kernel modules or root-level hardware operations inside standard containers; use hardware-virtualized **QEMU / KVM microVMs**.
3. **No Remote Execution**: Piping remote scripts to bash (`curl ... | sh`) is strictly forbidden. All assets must be downloaded to disk, inspected, and checksummed before execution.

---

## 4. Reporting Security Vulnerabilities

If you discover a security vulnerability, isolation escape, or unsafe autonomous execution pattern within Linux Engineering:
1. **Do not open a public issue.**
2. Report the vulnerability privately to the project maintainers via email or security advisory.
3. Provide a detailed reproduction report, affected platforms (Claude Code, Codex, Antigravity), and proposed remediation.
4. Maintainers will acknowledge reports within 48 hours and coordinate a coordinated disclosure timeline.
