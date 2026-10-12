# Fuzzing Crash Triage: Deduplication, Minimization, and Regression Tests

Methodological reference for analyzing fuzzer crash artifacts, deduplicating findings, minimizing test cases, and creating permanent regression tests.

---

## 1. The Crash Triage Lifecycle

When a fuzzer flags a crash:

```
[Crash Artifact Generated] ──► [Reproduce with Sanitizer] ──► [Deduplicate via Stack Trace]
                                                                        │
[Permanent Regression Test] ◄── [Patch & Verify] ◄── [Minimize Testcase via afl-tmin]
```

### Step 1: Confirm Deterministic Reproduction
Execute the standalone target with the crash artifact:
```bash
./fuzz_target crash-8a7c9d2f012b4e8590623aef5c01bc81d45903b1
```
Verify that the crash reproduces consistently.

---

## 2. Crash Deduplication

A 24-hour fuzzing run might generate 5,000 "crash" files. In reality, 4,998 of them may represent the exact same single bug triggered via slightly different input mutations.

### Deduplication Criteria:
1. **Sanitizer Error Class**: (e.g., `heap-use-after-free`, `heap-buffer-overflow`, `SEGV on unknown address`).
2. **Top 3 Stack Frames**: The function name, source file, and line numbers of the 3 innermost stack frames. If two crashes share identical top 3 stack frames, group them as the same unique bug.

---

## 3. Testcase Minimization (`afl-tmin` / `libFuzzer`)

A crash artifact might be 8 KB in size, but only 3 specific bytes actually trigger the defect.

### Using `afl-tmin`:
```bash
afl-tmin -i raw_crash.bin -o minimal_crash.bin -- ./my_app @@
```
*`afl-tmin` systematically zeroes out and truncates bytes, ensuring the binary still crashes on `minimal_crash.bin`. Often shrinks an 8 KB payload down to 5 bytes, making root cause diagnosis trivial.*

### Using `libFuzzer`:
```bash
./fuzz_target -minimize_crash=1 -exact_artifact_path=minimal_crash.bin raw_crash.bin
```

---

## 4. Converting Crashes into Regression Tests

Never close a fuzzing bug without committing the minimized crash file as an automated regression test:

```c
// test_fuzz_crashes.c - Executed by ctest / cargo test
#include <assert.h>
#include <stdio.h>
#include "my_parser.h"

void test_crash_cve_2024_01(void) {
    FILE *f = fopen("tests/fixtures/crashes/minimal_crash_01.bin", "rb");
    assert(f != NULL);
    uint8_t buffer[256];
    size_t n = fread(buffer, 1, sizeof(buffer), f);
    fclose(f);

    parser_result_t res;
    // Must return an error code safely, NOT crash or abort
    int status = parse_data(buffer, n, &res);
    assert(status != 0); 
}
```
