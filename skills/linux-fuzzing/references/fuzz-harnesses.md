# Fuzz Target & Harness Engineering

Technical reference for writing deterministic, high-throughput, leak-free fuzz targets in C, C++, and Rust.

---

## 1. The Anatomy of an Ideal Fuzz Target

A fuzz harness bridges the fuzzing engine and the target library API. The standard interface is `LLVMFuzzerTestOneInput`:

```c
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include "my_parser.h"

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // 1. Guard against trivially invalid or empty inputs
    if (size < 4) {
        return 0;
    }

    // 2. Initialize target structure
    parser_context_t ctx;
    if (parser_init(&ctx) != 0) {
        return 0;
    }

    // 3. Invoke target API with input buffer
    parser_result_t res;
    parser_parse_buffer(&ctx, data, size, &res);

    // 4. Clean up allocated state cleanly (prevent false-positive leak reports)
    parser_free_result(&res);
    parser_destroy(&ctx);

    return 0; // Return value must always be 0
}
```

---

## 2. Invariants of a High-Quality Fuzz Harness

1. **Determinism**: Given the exact same byte slice `data`, the harness must execute the exact same instructions and produce the exact same outcome every time.
   - Do NOT query system time (`clock_gettime()`, `time(NULL)`).
   - Do NOT use unseeded random number generators (`rand()`).
   - Do NOT depend on external filesystem state or environment variables.
2. **Zero Global State Accumulation**:
   Because `LLVMFuzzerTestOneInput` is executed millions of times inside the same process without restarting, any static or global memory leak will quickly cause an Out-Of-Memory (OOM) crash.
3. **No Terminal or Network Output**:
   Avoid printing `printf` statements or writing log files during iterations; terminal and disk I/O degrades throughput from 20,000 exec/sec down to 50 exec/sec.
4. **Time Bounded**:
   Ensure the target function does not spin in infinite loops on malformed inputs (use libFuzzer `-timeout=5`).

---

## 3. Rust Fuzzing with `cargo-fuzz`

In Rust, `cargo-fuzz` wraps libFuzzer:

```rust
#![no_main]
use libfuzzer_sys::fuzz_target;
use my_crate::parse_header;

fuzz_target!(|data: &[u8]| {
    // We don't care if parse_header returns an Err, but it must NEVER panic
    let _ = parse_header(data);
});
```

Execute via Cargo:
```bash
cargo fuzz run fuzz_target_1 -- -rss_limit_mb=1024
```
