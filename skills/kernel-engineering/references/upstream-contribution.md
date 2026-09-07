# Upstream Kernel Contribution & Mailing List Etiquette Reference

## 1. Scope

This document details the procedures, mailing list conventions, tooling (`b4`), and review etiquette required to prepare contribution-ready Linux kernel patches.

---

## 2. Upstream Contribution Tooling: `b4`

`b4` is the official modern CLI tool for working with Linux kernel patch series hosted on `lore.kernel.org`:

### 2.1 Preparing a Patch Series with `b4 prep`
```bash
# 1. Create a local branch for your patch series
b4 prep -n fix-e1000e-probe-null-ptr

# 2. Make commits on the branch following kernel commit guidelines

# 3. Check series formatting and trailers
b4 prep --check
```

### 2.2 Managing Maintainer Reviews & Trailers
When maintainers reply with `Reviewed-by` or `Acked-by` tags on the mailing list:
```bash
# Retrieve and apply trailers from public-inbox automatically
b4 trailers -u
```

---

## 3. Mailing List Etiquette & Persona Invariants

1. **Plain Text Only**:
   - Kernel mailing lists reject HTML emails. Emails must be pure 7-bit ASCII or UTF-8 plaintext with hard word-wrapping at 72 characters.
2. **Bottom-Posting / In-Line Replies**:
   - Never top-post. Quote only relevant context and write replies directly underneath the quoted snippet.
3. **No Autonomous Email Sending**:
   - An AI agent must **NEVER execute `git send-email` or `b4 send` autonomously**.
   - All contributions must be formatted as `.patch` files and presented for human inspection:
     > "Patch series formatted and validated with checkpatch.pl. Ready for human review and submission."

---

## 4. Stable Tree Backport Criteria

To qualify for the stable kernel tree (`stable@vger.kernel.org`), a patch must satisfy:
1. It must already be accepted in Linus Torvalds' upstream tree (`torvalds/linux.git`).
2. It must be small (< 100 lines) and obviously correct.
3. It must fix a real bug (regression, crash, data corruption, hardware lockup).
4. It must contain a valid `Fixes:` tag pointing to the commit that introduced the bug.
5. New features or general refactorings are strictly rejected from stable trees.

---

## 5. Authoritative References

- [Submitting Patches](https://docs.kernel.org/process/submitting-patches.html)
- [b4 Documentation](https://b4.docs.kernel.org/)
- [Stable Kernel Rules](https://docs.kernel.org/process/stable-kernel-rules.html)
