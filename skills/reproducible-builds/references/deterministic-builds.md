# Deterministic Builds & Source Normalization

Writing deterministic code requires eliminating runtime timestamps, volatile compiler macros, and non-deterministic archive creation routines.

---

## 1. The `SOURCE_DATE_EPOCH` Standard

The `SOURCE_DATE_EPOCH` specification standardizes UNIX timestamps across build tools. It replaces the current system time with a fixed reference time (typically the Unix timestamp of the latest git commit or package changelog entry).

### Setting the Variable:
```bash
# In Git repositories:
export SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)

# In Debian packages:
# debhelper automatically sets SOURCE_DATE_EPOCH from debian/changelog

# In RPM packages:
# rpmbuild automatically sets SOURCE_DATE_EPOCH from the latest %changelog date
```

### Compiler Support:
- **GCC and Clang**: When `SOURCE_DATE_EPOCH` is set, calls to `__DATE__` and `__TIME__` evaluate to UTC formatted dates/times based on `SOURCE_DATE_EPOCH` instead of wall-clock time.
- **Python / Sphinx / Doxygen**: Respects `SOURCE_DATE_EPOCH` for generated HTML/manpage timestamps.

---

## 2. Eliminating `__DATE__` and `__TIME__` in C/C++

Avoid relying solely on compiler magic; remove volatile macros in application code:

```c
/* Non-deterministic: changes on every compilation run */
printf("Compiled on %s at %s\n", __DATE__, __TIME__);

/* Deterministic: use version strings or explicit release timestamps */
printf("Application version %s (commit %s)\n", APP_VERSION, APP_GIT_SHA);
```

---

## 3. Deterministic Archive Creation (`tar`, `cpio`, `zip`)

Standard `tar` embeds the current timestamp, file owner UID/GID, and filesystem readdir order:

```bash
# DETERMINISTIC TAR COMMAND
tar --sort=name \
    --mtime="@${SOURCE_DATE_EPOCH}" \
    --owner=0 --group=0 --numeric-owner \
    --pax-option=exthdr.name=%d/PaxHeaders/%f,delete=atime,delete=ctime \
    -czf archive.tar.gz -C src .
```

### Key Flags:
- `--sort=name`: Orders directory contents alphabetically regardless of underlying filesystem traversal order.
- `--mtime="@${SOURCE_DATE_EPOCH}"`: Clamps file modification times to the fixed epoch.
- `--owner=0 --group=0 --numeric-owner`: Prevents developer usernames or UIDs (e.g., UID 1000) from leaking into distributed archives.
- `--pax-option=delete=atime,delete=ctime`: Strips volatile access/change timestamps.

---

## 4. Deterministic Compression (`gzip`, `zstd`)

Compressors frequently embed timestamps and original filenames in their headers:
- **`gzip`**: Always pass `-n` or `--no-name` to prevent saving the original timestamp and filename:
  ```bash
  gzip -9n file.tar
  ```
- **`zstd`**: By default does not embed timestamps, but ensure threads count (`-T`) does not alter framing (use `--fixed-threads` or standard compression levels).