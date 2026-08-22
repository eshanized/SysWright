# Global Engineering Reference: Engineering Principles

## 1. Minimal & Scoped Changes

1. **Locality of Mutation**: Modify only the specific lines, functions, or configuration directives necessary to satisfy the contract. Never reformat unrelated code, reorder imports gratuitously, or rewrite working modules.
2. **Blast Radius Minimization**: Prefer surgical bug fixes over wide-ranging refactors when stabilizing production code.
3. **Preserve Existing Architecture**: When working within an established repository, adhere strictly to its coding conventions, build system, error handling idioms, and naming styles.

---

## 2. Dependency Discipline

1. **Zero Unnecessary Dependencies**: Every external library, crate, or utility introduced into a project carries supply-chain, security, and maintenance overhead. Avoid adding heavy dependencies for trivial operations.
2. **Standard Library Preference**: Prefer the native Linux/POSIX standard library (`glibc`, `musl`, Rust `std`, Python 3 `stdlib`) where practical.
3. **Explicit Dependency Auditing**: In packaging (`PKGBUILD`, `debian/control`), distinguish strictly between `depends` (direct runtime linkages), `makedepends` (build-time compilers/generators), and `checkdepends` (test suites).

---

## 3. Backward Compatibility & Upstream Conventions

1. **Upstream First**: Never introduce downstream-only hacks or proprietary workarounds if a clean upstream solution exists.
2. **ABI & API Stability**: Understand shared library sonames and symbol versioning. Avoid breaking public C ABI layouts or D-Bus signatures without bumping major interface versions.
3. **Deprecation Awareness**: Never introduce newly deprecated APIs. When fixing legacy code, migrate deprecated calls to canonical modern replacements verified in Tier 1 documentation.

---

## 4. Reproducible & Deterministic Engineering

1. **Clean Environment Isolation**: Packages and binaries must build cleanly inside isolated environments (clean chroots via `devtools`/`arch-nspawn` or containers) without relying on undeclared host tools.
2. **Deterministic Outputs**: Build outputs must be bit-for-bit reproducible where possible (`SOURCE_DATE_EPOCH`, sorted directory traversal, static timestamps).
3. **Explicit Trade-Offs**: When choosing an implementation strategy, explicitly document alternative solutions considered, why they were rejected, and the trade-offs accepted.
