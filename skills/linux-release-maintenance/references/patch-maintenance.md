# Patch Lifecycle, Rebasing & Upstream Forwarding

Downstream package patches represent technical debt. Every patch maintained downstream increases maintenance overhead during upstream upgrades.

---

## 1. The Patch Lifecycle

```text
[ Bug or Feature Identified ]
              │
              ▼
    [ Author Local Patch ]
              │
              ▼
    [ Apply in Packaging ] ──(DEP-3 Header Documented)
              │
              ▼
  [ Forward to Upstream PR ] ──(Upstream Review)
              │
              ├────────────────────────┐
              ▼                        ▼
     [ Upstream Merged ]       [ Upstream Rejected ]
              │                        │
              ▼                        ▼
 [ Drop Patch on Next Release ]  [ Re-evaluate or Drop Feature ]
```

---

## 2. DEP-3 Patch Metadata Standard

All downstream patches across Debian, Ubuntu, and modern RPM packages should adopt DEP-3 headers:

```patch
Description: Fix buffer overflow in network packet parser
Author: Jane Maintainer <jane@example.org>
Origin: upstream, https://github.com/example/myapp/commit/abc1234
Bug-Debian: https://bugs.debian.org/123456
Bug: https://github.com/example/myapp/issues/789
Forwarded: not-needed
Applied-Upstream: 1.2.4
Last-Update: 2026-04-01

--- a/src/network.c
+++ b/src/network.c
@@ -45,7 +45,7 @@ int parse_packet(const char *buf, size_t
```

---

## 3. Rebasing Downstream Patches on New Releases

When upgrading from upstream `1.2.3` to `1.2.4`:

1. **Audit Upstream Commits**:
   Inspect git log or changelog to identify which downstream patches were incorporated:
   ```bash
   git log v1.2.3..v1.2.4 --oneline
   ```
2. **Drop Merged Patches**:
   Remove applied patches from `debian/patches/series` or RPM spec `PatchN:` declarations.
3. **Rebase Remaining Patches**:
   Apply patches sequentially using `quilt` or `git am`:
   ```bash
   quilt push
   # If reject occurs:
   quilt refresh
   ```
4. **Compile and Run Tests**:
   Verify that modified patches still apply cleanly and resolve the original issue without introducing side effects.