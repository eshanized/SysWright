# Regression Prevention: Golden Test Fixtures and CI Test Suites

Technical reference for building permanent regression prevention test suites, golden fixtures, and CI automation.

---

## 1. The Regression Corpus Pattern

Whenever a bug, crash, or regression is fixed, add the triggering artifact directly into a dedicated regression test suite:

```
tests/
├── regressions/
│   ├── issue_102_null_deref.c
│   ├── issue_145_deadlock.py
│   ├── issue_204_abi_check.sh
│   └── fixtures/
│       ├── malformed_utf8.bin
│       └── truncated_header.json
```

---

## 2. Golden Master / Approval Testing

For complex outputs (compilers, code generators, report generators, serializers), use "Golden Master" testing:
1. Run the software on a fixed reference input and commit the output as `expected_output.golden`.
2. In the regression test, compare the current output against the golden file using `diff -u`:
   ```bash
   ./my_generator input.txt > /tmp/actual.txt
   diff -u tests/fixtures/expected_output.golden /tmp/actual.txt
   ```
3. Any unexpected change in output format, whitespace, or values fails the test immediately.

---

## 3. Hermetic and Containerized CI Matrices

To prevent regressions caused by subtle glibc, compiler, or distribution differences:
- Run CI builds across multiple target distribution fixtures (Arch Linux, Debian Stable, Fedora, Ubuntu LTS).
- Use containerized testing (`podman` or `systemd-nspawn`) to ensure builds are isolated from host state.
- Test both Debug builds (with sanitizers `-fsanitize=address,undefined`) and Release builds (`-O3 -DNDEBUG`) to catch compiler-specific optimizations and assert failures.
