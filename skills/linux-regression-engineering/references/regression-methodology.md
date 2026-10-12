# Regression Engineering Methodology: Baselines, Invariants, and Isolation

Foundational methodology for defining, isolating, and validating software and operating system regressions.

---

## 1. What Qualifies as a Regression?

A regression is an unintended degradation in behavior, performance, or compatibility between revision $R_{\text{old}}$ and revision $R_{\text{new}}$.

### Essential Distinctions:
- **True Regression**: Software was verified to work correctly at revision $A$, but fails at revision $B$ under the exact same environment and inputs.
- **Pre-existing Defect**: Software failed at both $A$ and $B$, but the failure was only recently discovered due to new user behavior or edge cases.
- **Environment Incompatibility**: Software unchanged, but external host upgraded (e.g., Python 3.11 to 3.12 syntax deprecation, GCC upgrade, kernel syscall retirement).
- **Flaky / Non-Deterministic Failure**: Failure occurs intermittently due to race conditions or timing dependencies regardless of revision.

---

## 2. Invariant Tracking & Baseline Definition

Before beginning a regression investigation:

1. **Verify the "Good" Baseline**:
   Check out the known good version (e.g., v1.4.0) and run the reproducer. If it fails on the "good" baseline, the issue is not a regression between v1.4.0 and v1.5.0!
2. **Verify the "Bad" Baseline**:
   Check out the failing version (e.g., v1.5.0 or `main`) and confirm the reproducer fails reliably.
3. **Specify the Invariant**:
   Document the exact mathematical or behavioral invariant:
   - "HTTP status code must be 200 OK, not 500."
   - "Execution time must remain $< 150\text{ms}$."
   - "Shared library symbol `calc_hash` must remain at version `LIBFOO_1.0`."

---

## 3. The Minimization Principle

Once the culprit change is isolated:
1. **Minimize the Test Case**: Reduce large input files or complex workflows down to a one-line test command.
2. **Minimize the Fix**: Do not rewrite entire modules to fix a regression. Undo the specific invalid assumption or restore the expected contract.
3. **Verify the Flank**: Ensure that fixing the regression does not break the feature that the culprit commit was originally trying to implement.
