# Repository Design & Metadata Structure

Understanding the on-disk directory layout and metadata format for each major Linux package manager is required for repository generation and maintenance.

---

## 1. Debian / Ubuntu APT Repository Structure

APT uses a two-tier directory structure separating metadata (`dists/`) from package storage (`pool/`).

```text
repo/
├── dists/
│   └── noble/                    <-- Suite / Series Codename
│       ├── InRelease             <-- Cryptographically signed inline index
│       ├── Release               <-- Unsigned index containing checksums
│       ├── Release.gpg           <-- Detached GPG signature for Release
│       └── main/                 <-- Component
│           ├── binary-amd64/
│           │   ├── Packages      <-- Concatenated debian/control stanzas
│           │   ├── Packages.gz
│           │   └── Packages.xz
│           └── binary-arm64/
│               └── Packages.xz
└── pool/
    └── main/
        └── m/
            └── myapp/
                ├── myapp_1.2.3-1_amd64.deb
                └── myapp_1.2.3-1_arm64.deb
```

### Generation Commands:
- Local lightweight index generation:
  ```bash
  dpkg-scanpackages pool/ /dev/null | gzip -9c > dists/stable/main/binary-amd64/Packages.gz
  ```
- Enterprise repository manager (`aptly`):
  ```bash
  aptly repo create -distribution=noble -component=main internal-stable
  aptly repo add internal-stable incoming/*.deb
  aptly publish repo internal-stable
  ```

---

## 2. Fedora / RHEL / openSUSE RPM Repository Structure (repomd)

RPM repositories store package files anywhere in the tree and place XML metadata under a single `repodata/` directory.

```text
repo/
├── repodata/
│   ├── repomd.xml                <-- Master index referencing XML checksums
│   ├── repomd.xml.asc            <-- Detached GPG signature
│   ├── <hash>-primary.xml.gz     <-- Package names, versions, dependencies, files
│   ├── <hash>-filelists.xml.gz   <-- Complete list of every file in every package
│   └── <hash>-other.xml.gz       <-- Changelogs
└── x86_64/
    └── myapp-1.2.3-1.fc40.x86_64.rpm
```

### Generation Commands:
- Building repomd indices with `createrepo_c`:
  ```bash
  createrepo_c --database --compatibility --workers 4 /srv/repo/x86_64/
  ```
- Adding update information (errata / security advisories):
  ```bash
  modifyrepo_c updateinfo.xml /srv/repo/x86_64/repodata/
  ```

---

## 3. Arch Linux Pacman Repository Structure

Pacman repositories are flat directories containing packages and a compressed archive database.

```text
repo/
├── os/x86_64/
│   ├── custom.db.tar.zst         <-- Symlink to database file
│   ├── custom.files.tar.zst      <-- File list database
│   ├── custom.db.sig             <-- Database GPG signature
│   ├── myapp-1.2.3-1-x86_64.pkg.tar.zst
│   └── myapp-1.2.3-1-x86_64.pkg.tar.zst.sig
```

### Generation Commands:
- Adding packages with `repo-add`:
  ```bash
  repo-add -s -v -n /srv/repo/os/x86_64/custom.db.tar.zst /srv/repo/os/x86_64/myapp-1.2.3-1-x86_64.pkg.tar.zst
  ```
  *(Note: `-s` signs the database using your default GPG key).*