# Research Reference: Confidence Levels & Contradiction Resolution

## 1. Confidence Level Classifications

When recording findings during Linux systems research, every claim must be categorized into one of four confidence levels:

### Level 1: Verified
- **Criteria**:
  1. Corroborated directly by official upstream source code (`git.kernel.org`, `systemd` git, `glibc` git), or
  2. Defined in an unambiguous international or upstream standard (POSIX.1-2024, ISO C23, Freedesktop specification), or
  3. Observed directly through reproducible execution on the active target environment.
- **Action**: Safe for direct production implementation without prior hesitation.

### Level 2: Strongly Supported
- **Criteria**:
  1. Stated in official upstream documentation (`docs.kernel.org`, `freedesktop.org/software/systemd/man/`), or
  2. Detailed in kernel maintainer commit messages, release notes, or `lore.kernel.org` discussions, or
  3. Documented in authoritative distribution policies (`wiki.archlinux.org`, Debian Policy).
- **Action**: Permitted for implementation, accompanied by a targeted verification test (Level 1).

### Level 3: Tentative
- **Criteria**:
  1. Deduced from secondary documentation, technical conference presentations, or architectural analogies.
  2. Inferred from community practices where upstream documentation is silent.
- **Action**: Requires explicit experimental verification or isolation prior to applying to host or production code.

### Level 4: Unknown / Unresolved
- **Criteria**:
  1. Upstream evidence is missing, conflicting, or applies to an incompatible kernel/userspace version.
  2. Behavior cannot be verified without privileged or destructive operations.
- **Action**: **Prohibited from implementation.** Must be reported to the user as an explicit uncertainty.

---

## 2. Contradiction Resolution Hierarchy

When technical sources provide conflicting information, resolve using this strict order:

1. **Source Code vs. Documentation**:
   *Source code is ground truth*. If `docs.kernel.org` specifies return code `0`, but `kernel/fork.c` returns `1` or `size`, the code reflects reality. Document the documentation erratum.
2. **Upstream Specification vs. Distribution Wiki**:
   - For Linux kernel internals, systemd unit directives, or C runtime behavior: **Upstream documentation wins**.
   - For package metadata (`PKGBUILD`, `control`), filesystem directory placement, and distribution defaults: **Distribution policy manual wins**.
3. **Current Version vs. Historical Documentation**:
   The documentation matching the **exact active version** (reported by `linux-environment`) overrules newer or older documentation.
