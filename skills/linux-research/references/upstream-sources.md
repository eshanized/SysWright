# Research Reference: Authoritative Upstream Sources Index

## 1. Primary Upstream Repositories & Documentation

| Domain | Primary Source | Authority Tier | URL / Access Method | Notes |
|:---|:---|:---:|:---|:---|
| **Linux Kernel Documentation** | The Linux Kernel documentation | Tier 1 | `https://docs.kernel.org/` | Official upstream documentation for Kbuild, Kconfig, drivers, and subsystems. |
| **Linux Kernel Source** | Linus Torvalds mainline tree | Tier 2 | `git://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git` | Canonical kernel source repository. |
| **Kernel Mailing Lists** | lore.kernel.org public-inbox | Tier 3 | `https://lore.kernel.org/` | Public archive of LKML, netdev, linux-btrfs, etc. |
| **systemd Manuals** | Freedesktop systemd project | Tier 1 | `https://www.freedesktop.org/software/systemd/man/latest/` | Official systemd unit, service, socket, and exec configuration documentation. |
| **systemd Source** | systemd git repository | Tier 2 | `https://github.com/systemd/systemd` | Ground truth for systemd behavior, D-Bus interfaces, and sandbox enforcement. |
| **Linux Man-Pages** | Michael Kerrisk / Linux man-pages project | Tier 1 | `https://man7.org/linux/man-pages/` | Official manual pages for Linux system calls and GNU C library functions. |
| **Arch Linux Wiki** | Arch Linux Documentation | Tier 4 | `https://wiki.archlinux.org/` | World-class documentation for Linux administration, packaging, and configuration. |
| **Arch Packaging Standards** | Arch Package Guidelines | Tier 4 | `https://wiki.archlinux.org/title/Arch_package_guidelines` | Authoritative rules for `PKGBUILD` and package creation. |
| **FreeDesktop Standards** | FreeDesktop.org specifications | Tier 1 | `https://specifications.freedesktop.org/` | Desktop Entry, Icon Theme, XDG Base Directory, and AppStream specifications. |
| **POSIX Standards** | IEEE Std 1003.1-2024 (Issue 8) | Tier 1 | `https://pubs.opengroup.org/onlinepubs/9799919799/` | Core POSIX system calls, shell grammar, and utility specifications. |

---

## 2. Disqualified Sources (Never Use as Authoritative Evidence)
- Unverified StackOverflow answers without reproducible code or official citations.
- Personal blog posts claiming deprecated methods are still valid.
- AI search snippets or forum summaries without link to upstream documentation.
- Distribution forums discussing obsolete releases (>5 years old).
