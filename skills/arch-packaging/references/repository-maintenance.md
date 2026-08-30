# Custom Distribution Repositories & Pacman Database Reference

## 1. Scope

This document specifies how to create, sign, maintain, and publish custom third-party distribution repositories for Arch-based Linux systems, internal enterprise infrastructure, or private package archives.

---

## 2. Repository Architecture & Layout

An Arch package repository is a standard HTTP, HTTPS, or local filesystem directory containing compiled packages (`.pkg.tar.zst`), cryptographic detached signatures (`.sig`), and the pacman repository database:

```text
/srv/http/custom-repo/x86_64/
├── custom-repo.db -> custom-repo.db.tar.gz      # Symlink to active database
├── custom-repo.db.tar.gz                        # Gzip-compressed package database
├── custom-repo.db.tar.gz.sig                    # GPG detached signature of database
├── custom-repo.files -> custom-repo.files.tar.gz# Symlink to files index
├── custom-repo.files.tar.gz                     # Complete filelist database (for pacman -F)
├── custom-repo.files.tar.gz.sig                 # GPG detached signature of filelist
├── myapp-1.0.0-1-x86_64.pkg.tar.zst             # Binary package archive
└── myapp-1.0.0-1-x86_64.pkg.tar.zst.sig         # GPG detached package signature
```

---

## 3. Database Management: `repo-add` & `repo-remove`

Pacman provides `repo-add` and `repo-remove` to manage repository databases:

### 3.1 Initializing and Adding Packages
```bash
# Basic package addition to a repository database
repo-add /srv/http/custom-repo/x86_64/custom-repo.db.tar.gz \
  /srv/http/custom-repo/x86_64/myapp-1.0.0-1-x86_64.pkg.tar.zst
```

### 3.2 Production Add with Signing & Cleanups
```bash
repo-add \
  --sign \
  --key "44869609740AE61A21704C408F73607422E5824A" \
  --verify \
  --remove \
  --prevent-downgrade \
  --include-sigs \
  /srv/http/custom-repo/x86_64/custom-repo.db.tar.gz \
  /srv/http/custom-repo/x86_64/*.pkg.tar.zst
```

#### Option Explanations:
- `-s, --sign`: Generates detached `.sig` signature for the database using GnuPG.
- `-k, --key <fingerprint>`: Explicitly specifies the GPG key to use for signing.
- `-v, --verify`: Validates the database's existing signature before allowing mutations.
- `-R, --remove`: Automatically deletes older `.pkg.tar.zst` files from disk when replaced by newer versions.
- `-p, --prevent-downgrade`: Prevents accidentally overwriting a newer package with an older version.
- `--include-sigs`: Embeds package signatures directly into the repository database.

### 3.3 Removing Packages (`repo-remove`)
```bash
repo-remove -s -R /srv/http/custom-repo/x86_64/custom-repo.db.tar.gz myapp
```

---

## 4. Key Management & Client Configuration

### 4.1 Client Configuration (`/etc/pacman.conf`)
To consume the custom repository on client systems, add a repository section:
```ini
[custom-repo]
SigLevel = Required DatabaseOptional
Server = https://repo.example.com/$arch
```

### 4.2 Distributing the Repository Key
Clients must trust the repository signing key:
1. **Best Practice**: Package the public key in a dedicated keyring package (`custom-keyring`) signed by an existing trusted key.
2. **Manual Key Trust**:
   ```bash
   # Import public key into pacman's keyring
   pacman-key --add /path/to/repo-signing-key.pub
   # Locally sign the key to mark it trusted
   pacman-key --lsign-key <KEY_FINGERPRINT>
   ```

---

## 5. Repository Maintenance Invariants

1. **Atomic Publishing**: Always write new packages and run `repo-add` in a staging directory, then synchronize atomically to the web server (`rsync -a --delete`). Never run `repo-add` directly on a live HTTP directory while clients may be downloading updates.
2. **Symlink Consistency**: Ensure `custom-repo.db` and `custom-repo.files` symlinks are present and point to the `.tar.gz` archives.
3. **Retention Policies**: If keeping older package versions for rollback, store them in an `archive/` subfolder rather than leaving them in the active repository root.

---

## 6. Authoritative References

- [repo-add(8) Manual](https://man.archlinux.org/man/repo-add.8)
- [pacman.conf(5) Manual](https://man.archlinux.org/man/pacman.conf.5)
- [pacman-key(8) Manual](https://man.archlinux.org/man/pacman-key.8)
- [ArchWiki: Custom local repository](https://wiki.archlinux.org/title/Pacman/Tips_and_tricks#Custom_local_repository)
