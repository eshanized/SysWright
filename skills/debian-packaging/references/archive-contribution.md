# Debian Archive Contribution: Salsa, Mentors, and Sponsorship (RFS)

Methodological reference for contributing packages to Debian, working with Salsa Git, using mentors.debian.net, and source-only uploads.

---

## 1. Debian Contribution Channels

Debian is a volunteer-driven distribution with strict cryptographic trust rings. Non-maintainers (contributors without Debian Developer or Debian Maintainer status) cannot upload directly to the Debian archive.

### The Sponsorship Workflow:
```
[Maintainer Prepares Package on Salsa] ──► [Builds Cleanly via sbuild]
                   │
                   ▼
[Uploads to mentors.debian.net via dput] ──► [Files RFS Bug on Debian BTS]
                   │
                   ▼
[Debian Developer Reviews Package] ──► [DD Signs & Uploads to Archive (FTP Master)]
```

---

## 2. Debian Salsa (GitLab Instance)

Debian packaging teams maintain repositories on Salsa (`salsa.debian.org`):
- Uses `git-buildpackage` (`gbp`) branch layout:
  - `upstream/latest`: Upstream source releases.
  - `debian/latest` (or `debian/sid`): Debian packaging files (`debian/`).
  - `pristine-tar`: Delta data allowing bit-for-bit recreation of upstream `.orig.tar.xz`.

### Salsa CI:
Every Salsa repository includes `.gitlab-ci.yml` running Salsa CI:
- Builds package in sbuild.
- Runs `lintian`.
- Runs `autopkgtest`.
- Runs `piuparts`.
- Tests reproducible builds with `reprotest`.

---

## 3. Source-Only Uploads

Since Debian 10 (buster), Debian enforces **Source-Only Uploads** for archive inclusion:
```bash
dpkg-buildpackage -S -sa
```
- `-S`: Build source package only (no binary `.deb` files in upload).
- `-sa`: Include the `.orig.tar.xz` in the upload (mandatory for new packages entering the `NEW` queue).
- *Rationale*: Pre-built binary packages uploaded by individual maintainers could contain trojans, compiler compromises, or host-specific artifacts. The official Debian buildd network compiles all production binary packages in isolated, hermetic build environments.
