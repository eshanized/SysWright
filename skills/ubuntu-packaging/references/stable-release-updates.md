# Ubuntu Stable Release Updates (SRU) Process

Comprehensive guide to Ubuntu's Stable Release Update (SRU) policy, documentation template, and verification workflow.

---

## 1. The Strict Philosophy of SRU

Once an Ubuntu LTS or interim release is published, users expect absolute stability. Routine feature updates, refactorings, or minor cleanups are **STRICTLY FORBIDDEN** in stable releases.

### What Qualifies for an SRU?
- Critical bug fixes preventing severe data loss or system crashes.
- High-severity regressions introduced by previous updates.
- Support for newly released hardware.
- High/Critical security vulnerabilities (handled in coordination with Ubuntu Security).

---

## 2. Mandatory SRU Bug Description Template

Every SRU upload must be attached to a public Launchpad bug report containing this exact structured format:

```markdown
[Impact]
A clear, concise statement describing the problem, how users are affected,
and why this bug is severe enough to justify an update to a stable release.

[Test Plan]
A step-by-step, reproducible test procedure that anyone can execute:
1. Fresh installation of Ubuntu <series>.
2. Run command X -> Observe failure/crash on unpatched version.
3. Enable <series>-proposed pocket.
4. Update to proposed package version Y.
5. Run command X again -> Verify clean success and expected output.

[Where problems could occur]
A realistic regression potential analysis:
- What other subsystems or packages depend on this code?
- If the patch is flawed, what could break?
- What mitigations exist in the patch to minimize side-effects?
```

---

## 3. The 7-Day Verification Aging Period

After an SRU is approved and uploaded to `<series>-proposed`:
1. The bug report is tagged `verification-needed`.
2. Testers and community members follow the `[Test Plan]` and post verification results on the bug.
3. Once verified, the tag is updated to `verification-done`.
4. The package must age in `-proposed` for a minimum of **7 days** without new regression reports before the Ubuntu SRU team promotes it to `<series>-updates`.
