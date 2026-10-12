# Compiler Sanitizers: ASan, UBSan, MSan, TSan, and KASAN

Comprehensive technical reference for LLVM/GCC sanitizers, their overheads, mutual exclusion rules, and kernel sanitizers.

---

## 1. Compiler Sanitizer Comparison Matrix

| Sanitizer | Flag | Defect Classes Detected | Slowdown | Memory Overhead | Compatible Combinations |
|---|---|---|---|---|---|
| **AddressSanitizer (ASan)** | `-fsanitize=address` | Out-of-bounds (heap, stack, global), Use-After-Free, Double-Free, Invalid Free | ~2x | 2x - 3x | Can combine with UBSan, LSan |
| **UndefinedBehaviorSanitizer (UBSan)** | `-fsanitize=undefined` | Integer overflow, null pointer dereference, misaligned pointer, shift exponents | ~1.2x | Negligible | Can combine with ASan, TSan, MSan |
| **ThreadSanitizer (TSan)** | `-fsanitize=thread` | Data races, deadlocks, lock order inversions, atomics violations | 5x - 15x | 5x - 10x | Can combine with UBSan |
| **MemorySanitizer (MSan)** | `-fsanitize=memory` | Reads of uninitialized memory in heap, stack, or variables | ~3x | ~2x | Can combine with UBSan |
| **LeakSanitizer (LSan)** | `-fsanitize=leak` | Unreferenced heap memory leaks at process termination | ~1.1x | Minimal | Integrated into ASan by default |

---

## 2. Mutual Exclusion & Incompatibilities

> [!WARNING]
> Sanitizers cannot all be combined arbitrarily in a single build:
> 1. **ASan and TSan are MUTUALLY EXCLUSIVE**: They use conflicting shadow memory layouts. Attempting `-fsanitize=address,thread` triggers a compilation or link error.
> 2. **ASan and MSan are MUTUALLY EXCLUSIVE**: Shadow memory architectures clash.
> 3. **MSan requires 100% instrumented dependencies**: If an uninstrumented library (e.g., standard libc or OpenSSL) initializes a struct, MSan will raise a false-positive uninitialized read when the application accesses that struct.

---

## 3. Kernel Sanitizers: KASAN, KCSAN, KMSAN

| Kernel Sanitizer | Target Faults | Kernel Version | Notes |
|---|---|---|---|
| **KASAN** | Kernel UAF, slab out-of-bounds | 4.0+ | Standard for kernel fuzzing with syzkaller |
| **KCSAN** | Kernel data races | 5.8+ | Uses compile-time memory access instrumentation |
| **KMSAN** | Uninitialized kernel memory reads | 6.1+ | Catches kernel info-leaks to user-space |
| **Lockdep** | Kernel deadlock detection | 2.6+ | Runtime lock dependency tracking |

---

## 4. Production Packaging Warning

> [!IMPORTANT]
> Never ship development sanitizer binaries in production software packages!
> Sanitizer runtimes intentionally abort the process on detected errors, disable allocator optimizations, increase binary sizes by 3x-5x, and introduce security vulnerabilities (e.g., ASan replaces memory allocators and is not hardened against heap exploitation). Sanitizers are strictly for testing, fuzzing, and CI pipelines.
