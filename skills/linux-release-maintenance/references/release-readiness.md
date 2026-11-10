# Release Readiness & Go/No-Go Decision Criteria

Before releasing a package or software update, the maintainer must conduct a systematic release readiness evaluation.

---

## 1. Formal Release Readiness Evaluation

A release is NOT ready when the code compiles; it is ready only when all release criteria are affirmatively satisfied:

| Category | Verification Item | Blocking Condition |
|---|---|---|
| **Build Integrity** | Clean build in isolated chroot/container across all architectures | Any build failure or compiler error |
| **Test Suite** | 100% test pass rate in unit and integration test suites | Any test failure or timeout |
| **Packaging Standards** | `lintian` / `rpmlint` audit with zero errors | Any error-level linter violation |
| **Clean Upgrade** | Clean upgrade test from prior stable package version | Upgrade failure, unhandled conffile prompt, or crash |
| **Documentation** | Accurate changelog entries with CVEs/bugs cited | Missing changelog or incorrect version tags |
| **Licensing** | All new source files have valid copyright and license headers | Unclear license or proprietary code inclusion |
| **Reproducibility** | Bit-for-bit reproducible or diffoscope variances justified | Unjustified binary divergence |

---

## 2. The Go / No-Go Decision Protocol

```text
               [ Release Candidate Tagged ]
                            │
                            ▼
              [ Run Release Readiness Gate ]
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
        [ All Pass ]               [ Any Fail ]
              │                           │
              ▼                           ▼
        [ GO: Sign & Publish ]     [ NO-GO: Abort ]
                                          │
                                          ▼
                                   [ Open Blocker Bug ]
                                   [ Fix in Next RC ]
```

### Abort Triggers (Automatic NO-GO):
- Any reproducible crash or kernel panic under standard operational workloads.
- Any unresolved regression reported against the previous stable release.
- Unhandled data corruption or migration failure during package upgrade or removal.
- Any unpatched high-severity CVE (CVSS >= 8.0) affecting the release candidate.