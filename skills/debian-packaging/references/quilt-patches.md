# Debian Patch Management: Quilt & DEP-3 Patch Tagging

Technical reference for managing downstream patches, the `debian/patches/series` file, and DEP-3 metadata headers.

---

## 1. How Quilt Works in Debian Source Packages

In format `3.0 (quilt)`, upstream source code is extracted pristine. All Debian-specific modifications must be recorded as patches inside `debian/patches/` and listed in `debian/patches/series`:

```text
debian/patches/
├── series
├── 0001-fix-spelling-in-manpage.patch
└── 0002-use-system-shared-libraries.patch
```

### Essential Quilt Commands in Packaging:
```bash
# Set quilt environment variables for Debian
export QUILT_PATCHES=debian/patches
export QUILT_REFRESH_ARGS="-pab --no-timestamps --no-index"

# Push all patches onto source tree
quilt push -a

# Pop all patches before generating source package
quilt pop -a

# Create a new patch
quilt new 0003-fix-cve-2024-001.patch
quilt add src/network.c
# Edit src/network.c
quilt refresh
```

---

## 2. The DEP-3 Patch Tagging Standard

Every patch in `debian/patches/` must include standardized DEP-3 (Debian Enhancement Proposal 3) headers:

```patch
Description: Fix heap buffer overflow when parsing malformed headers
 When processing untrusted HTTP packet headers, length checks were
 omitted, leading to an out-of-bounds heap write. This patch validates
 that header_len <= MAX_HEADER_SIZE before invoking memcpy.
Author: Jane Developer <jane@example.org>
Origin: upstream, https://github.com/upstream/project/commit/8a7c9d2f012b4e8590623aef5c01bc81d45903b1
Bug: https://github.com/upstream/project/issues/142
Bug-Debian: https://bugs.debian.org/1024501
Forwarded: not-needed
Applied-Upstream: 1.4.2
Last-Update: 2024-01-15
---
--- a/src/network.c
+++ b/src/network.c
@@ -42,6 +42,9 @@ int parse_header(const uint8_t *data, si
+    if (len > MAX_HEADER_SIZE) {
+        return -EINVAL;
+    }
     memcpy(dest, data, len);
```

### Key DEP-3 Fields:
- `Description:`: Detailed explanation of what the patch does and why it was created.
- `Author:`: Name and email of patch author.
- `Origin:`: Source of the patch (`upstream`, `backport`, `vendor`).
- `Bug:` / `Bug-Debian:`: Canonical URLs to upstream and Debian bug tracking entries.
- `Forwarded:`: `yes`, `no`, `not-needed` (if Debian-specific packaging change), or URL where forwarded upstream.
