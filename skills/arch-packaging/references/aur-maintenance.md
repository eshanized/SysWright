# Arch User Repository (AUR) Packaging & Maintenance Reference

## 1. Scope

This document specifies the rules, repository layout, metadata requirements, and maintenance workflows for the Arch User Repository (AUR). The AUR is a community-driven repository of package build scripts (`PKGBUILD`), not precompiled binary packages.

---

## 2. Core AUR Rules & Anti-Duplication Policies

Before creating or uploading any package to the AUR, verify the following strict rules:

### 2.1 No Duplication of Official Packages
- **Absolute Rule**: Never submit a package to the AUR that already exists in the official Arch Linux binary repositories (`core`, `extra`, `multilib`).
- **Resolution Matrix**:
  - If the official package is outdated $\to$ Flag it out-of-date on [archlinux.org/packages](https://archlinux.org/packages).
  - If the official package has a bug $\to$ File a bug report on [GitLab Arch Linux packaging](https://gitlab.archlinux.org/archlinux/packaging/packages).
  - If you need custom compile flags or patches $\to$ Maintain a local PKGBUILD, or append a differentiating suffix (e.g., `linux-custom`, `neovim-nightly`), and declare `conflicts=('official-name')` and `provides=('official-name')`.

### 2.2 Pre-Submission Existing Package Check
Before creating a new AUR package, search both official repos and the AUR:
```bash
# 1. Search official repositories
pacman -Ss "^$pkgname$"

# 2. Search AUR using official web RPC or aurweb search
curl -s "https://aur.archlinux.org/rpc/v5/search/$pkgname" | jq '.results[] | {name: .Name, version: .Version, maintainer: .Maintainer}'
```
- If the package already exists on the AUR:
  - If actively maintained: Submit patches or improvements via AUR comments or email to the maintainer.
  - If orphaned (`Maintainer: null`): An authenticated maintainer may adopt it via `aurweb`.

---

## 3. AUR Git Repository Layout & Permitted Files

An AUR package repository is a bare Git repository hosted at:
`ssh://aur@aur.archlinux.org/<pkgname>.git`

```text
<pkgname>/
├── PKGBUILD          # Mandatory: The package build script
├── .SRCINFO          # Mandatory: Generated machine-readable metadata
├── mydaemon.service  # Optional: Local systemd unit file
└── fix-paths.patch   # Optional: Local patch file referenced in source=()
```

### 3.1 Strictly Forbidden Files in AUR Git Trees
1. **Binary Packages**: `.pkg.tar.zst` or any built package archives.
2. **Upstream Source Archives**: `.tar.gz`, `.zip`, `.tar.xz` downloaded from upstream. Upstream sources must be downloaded via `source=()` URLs during `makepkg`.
3. **Precompiled Binaries**: Executables or shared libraries (`.so`, `.dll`).
4. **Build Output Artifacts**: Object files (`.o`), CMake caches (`CMakeCache.txt`), or Python wheels (`dist/*.whl`).

---

## 4. The `.SRCINFO` Invariant

- The `.SRCINFO` file is a machine-readable representation of `PKGBUILD` metadata used by the AUR web interface and AUR helpers to parse dependencies and versions without executing arbitrary Bash code.
- **Mandatory Synchronization**:
  ```bash
  makepkg --printsrcinfo > .SRCINFO
  ```
- **Rule**: Every Git commit touching `PKGBUILD` MUST regenerate and include the updated `.SRCINFO`. An out-of-sync `.SRCINFO` results in broken AUR metadata and rejected pushes.

---

## 5. AUR Naming Conventions

| Package Suffix | When to Use | Requirements |
|:---|:---|:---|
| *(No suffix)* | Building software from official upstream stable source releases. | Standard `pkgver` and `sha256sums`. |
| `-git` / `-svn` / `-hg` | Building from the latest upstream version control commit. | Must implement `pkgver()` function. `source=('git+https://...')`. Must specify `provides=("$pkgname=$pkgver")` and `conflicts=("$pkgname")`. |
| `-bin` | Repackaging upstream precompiled binary releases (e.g., when source is unavailable or compilation is prohibitive). | Must declare `provides=("$pkgname=$pkgver")` and `conflicts=("$pkgname")`. |

---

## 6. Maintainer Header Conventions

Place maintainer attribution in comments at the top of the `PKGBUILD`:
```bash
# Maintainer: Firstname Lastname <maintainer@example.com>
# Contributor: Previous Maintainer <previous@example.com>
```

---

## 7. Operational Safety & Push Policy

- **Tier 3 Operation**: Pushing to the AUR alters public package indexes and impacts thousands of users.
- **Mandatory Gating**: AI agents must **NEVER** run `git push origin master` or `git push aur master` autonomously.
- Always require explicit human authorization before publishing or updating remote AUR packages:
  > "PKGBUILD and .SRCINFO prepared and validated locally. Ready for maintainer review and manual push."

---

## 8. Authoritative References

- [AUR submission guidelines](https://wiki.archlinux.org/title/AUR_submission_guidelines)
- [Arch User Repository Guidelines](https://wiki.archlinux.org/title/Arch_User_Repository)
- [aurweb RPC Interface](https://wiki.archlinux.org/title/Aurweb_RPC_interface)
