# Global Engineering Reference: Research Methodology

## 1. The Research-First Imperative

In Linux systems engineering, code and configuration mutations without prior authoritative research are the primary cause of system instability, build regressions, and security exposure.

Every significant engineering workflow must strictly execute the **10-Step Engineering Protocol**:
1. **Deconstruct the Objective**: Separate symptoms from fundamental technical requirements.
2. **Identify Target & Versions**: Inspect the host release, kernel version, compiler, and init system.
3. **Query Authoritative Upstream Documentation**: Consult primary specifications (kernel.org, freedesktop.org, POSIX).
4. **Inspect Existing Implementations**: Read codebase patterns, build definitions, and existing unit configs.
5. **Analyze Git History & Rationale**: Trace why code was structured in its current form (`git log -S`, `git blame -w`).
6. **Evaluate Architectural Alternatives**: Compare trade-offs between competing approaches before touching files.
7. **Formulate a Scoped Strategy**: Define an exact list of files to modify and a concrete rollback plan.
8. **Execute Focused Mutations**: Apply minimal, non-invasive changes strictly within declared workspace boundaries.
9. **Verify with Deterministic Validators**: Execute compilers, linters, and unit test suites post-mutation.
10. **Report Empirical Evidence & Risks**: Document observed outputs, pass counts, and any remaining uncertainties.

---

## 2. Evidence Tracking & Confidence Tiers

Every technical claim supporting an engineering change must be classified into one of four confidence tiers:

| Confidence Tier | Criteria | Permitted Usage |
|:---|:---|:---|
| **Verified** | Directly confirmed via upstream source code, official specification, or observed test execution on target version. | Direct implementation and architecture decisions. |
| **Strongly Supported** | Stated in current maintainer documentation, release notes, or established reference implementations. | Implementation with targeted verification. |
| **Tentative** | Deduced from community practices, historical documentation, or architectural analogies. | Requires explicit pre-implementation verification. |
| **Unknown / Unresolved**| Insufficient or contradictory evidence; behavior unverified on active version. | Prohibited from implementation; must be flagged to user. |

---

## 3. Root-Cause Analysis Framework

When troubleshooting failures (build errors, crashes, kernel panics, service startup failures):
1. **Isolate the Fault Boundary**: Determine whether the defect is in application code, library linkage, packaging metadata, runtime permissions, or kernel configuration.
2. **Reproduce Deterministically**: Create a minimal reproducer script or targeted test invocation.
3. **Trace Syscalls & Call Stacks**: Use `strace -f -e trace=...`, `gdb`, or sanitizer logs (`-fsanitize=address`) to identify the exact faulting line.
4. **Never Mask Symptoms**: Reject workarounds (e.g., adding `chmod 777`, running services as root, disabling compiler hardening) that disguise underlying permission or memory errors.

---

## 4. Structured Evidence Schema

All formal research outputs must structure findings into the standard evidence block:

```markdown
### Evidence Record: [Technical Topic]
- **Claim**: [Concise technical statement]
- **Source**: [Authoritative URL or source tree file]
- **Authority**: [Tier 1 Upstream Spec / Tier 2 Source / Tier 3 Maintainer / Tier 4 Distro]
- **Target Version**: [Software version verified against]
- **Date Accessed**: [ISO 8601 Date]
- **Confidence**: [Verified / Strongly Supported / Tentative / Unknown]
- **Engineering Implication**: [Consequence for the implementation plan]
```
