# User-Space Fuzzing: libFuzzer and AFL++ Workflows

Comprehensive technical reference for deploying libFuzzer and AFL++ on Linux software.

---

## 1. libFuzzer: In-Process Coverage-Guided Fuzzing

libFuzzer is integrated directly into LLVM/Clang. It compiles the fuzz target and the fuzzing engine into a single executable binary.

### Compiling with libFuzzer & Sanitizers:
```bash
clang -O1 -g -fsanitize=fuzzer,address,undefined \
      -fno-omit-frame-pointer \
      fuzz_target.c my_parser.c -o fuzz_parser
```

### Running libFuzzer:
```bash
# Run with seed corpus directory, 4 worker jobs, memory ceiling 2048 MB, timeout 5s
./fuzz_parser CORPUS_DIR/ \
              -jobs=4 \
              -workers=4 \
              -rss_limit_mb=2048 \
              -timeout=5 \
              -dict=parser.dict \
              -artifact_prefix=crashes/
```

### Key libFuzzer CLI Options:
- `-dict=<file>`: Syntax dictionary containing keywords, tokens, or magic bytes.
- `-max_len=<N>`: Maximum length of test input in bytes (keep small initially, e.g., 4096).
- `-runs=<N>`: Number of individual test iterations (omit for infinite fuzzing).
- `-minimize_crash=1`: Reduces the input file size of an existing crash artifact.

---

## 2. AFL++: Advanced Fork-Server & Persistent Mode

AFL++ (AFLplusplus) provides superior mutation algorithms (MOPT, custom mutators, Redqueen) and supports both CLI programs and in-process persistent loops.

### Compiling for AFL++:
```bash
# Use AFL++ wrapper compilers
export CC=afl-clang-fast
export CXX=afl-clang-fast++

# Compile with AddressSanitizer (optional, separate campaign recommended)
AFL_USE_ASAN=1 make
```

### Persistent Mode in AFL++:
Avoids the overhead of `fork()` by looping inside the target function:
```c
#include <unistd.h>

__AFL_FUZZ_INIT();

int main(void) {
    #ifdef __AFL_HAVE_MANUAL_CONTROL
    __AFL_INIT();
    #endif

    unsigned char *buf = __AFL_FUZZ_TESTCASE_BUF;

    while (__AFL_LOOP(10000)) {
        int len = __AFL_FUZZ_TESTCASE_LEN;
        parse_untrusted_input(buf, len);
    }

    return 0;
}
```

### Running AFL++ Campaign:
```bash
# Set CPU scaling governor to performance (requires authorization)
# Launch master fuzzer node (-M)
afl-fuzz -i seed_corpus/ -o findings/ -m none -M fuzzer01 -- ./my_app_binary @@
```
*(The `@@` marker indicates where the fuzzer injects the mutated input filename).*
