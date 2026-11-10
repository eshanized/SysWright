# Managing Ubuntu Delta Against Debian: Merges, Syncs, and Upstream Forwarding

Technical reference for tracking differences between Debian and Ubuntu packaging, syncing packages, and forwarding patches upstream.

---

## 1. Debian Sync vs Merge Workflows

Most packages in Ubuntu originate from Debian:

### Direct Sync:
- Used when Ubuntu has **no local modifications** against Debian.
- Debian unstable version `1.2.3-1` imports directly into Ubuntu as `1.2.3-1`.
- Fast, automated, zero maintenance debt.

### Merge:
- Used when Ubuntu carries a local delta (e.g., AppArmor profiles, Wayland/Mir integration, architecture porting).
- When Debian uploads `1.2.3-2`, the Ubuntu maintainer must **merge** the new Debian changes with the existing Ubuntu delta, resulting in `1.2.3-2ubuntu1`.

---

## 2. Inspecting the Ubuntu Delta with `ubuntu-diff`

To view the exact differences between an Ubuntu package and its Debian parent:
```bash
# View the delta between Debian and Ubuntu for a package
ubuntu-diff myapp

# Or compare source packages directly:
debdiff myapp_1.2.3-1.dsc myapp_1.2.3-1ubuntu1.dsc
```

---

## 3. The Obligation to Minimize Delta

Every line of Ubuntu delta is permanent maintenance overhead:
- **Upstream First**: If a patch fixes a bug, submit it to upstream first.
- **Debian Second**: If the patch is accepted upstream or is generic to all Linux distributions, submit it to the Debian package via Salsa merge request or Debian BTS bug report (`reportbug`).
- **Ubuntu Last**: Only retain an Ubuntu delta if the change is strictly specific to Ubuntu's architecture or defaults.
- Once Debian adopts the fix, **drop the Ubuntu delta** and return the package to a clean, direct sync.
