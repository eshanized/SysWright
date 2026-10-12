# Fuzzing Methodology: Coverage-Guided Mutation & Feedback Loops

Technical reference for coverage-guided mutation, edge transition bitmaps, and evolutionary testing algorithms.

---

## 1. What Makes Coverage-Guided Fuzzing Effective?

Blind "black-box" fuzzing (randomly sending garbage bytes to an application) has an infinitesimally small probability of bypassing complex validation checks (such as magic headers or CRC32 checksums).

### The Coverage Feedback Loop:
```
[Seed Corpus] ──► [Mutator] ──► [Instrumented Target] ──► [Branch Coverage Bitmap]
      ▲                                                           │
      │                                                           ▼
      └────────── [Save to Corpus if New Branch Hit] ◄─────────────
```

1. **Instrumentation**: The compiler (Clang/GCC) inserts a small snippet of code at every basic block and conditional branch edge:
   $$\text{cur\_location} \oplus (\text{prev\_location} \gg 1)$$
2. **Shared Memory Bitmap**: As the target executes, every edge transition increments a byte in a shared 64 KB coverage bitmap.
3. **Evolutionary Selection**: When a mutated input triggers an edge transition never seen before (new code branch reached), that input is saved into the corpus as a parent for future mutations.
4. **Deep Path Exploration**: By incrementally mutating inputs that penetrate deeper into nested parsers, the fuzzer automatically synthesizes valid protocol structures and magic headers without human intervention.

---

## 2. Fuzzing Target Prioritization

Not all code is equally vulnerable. Rank components for fuzz testing based on risk:

1. **Tier 1 (Highest Risk)**:
   - Untrusted file format parsers (JPEG, PNG, PDF, ELF, tar, zip).
   - Network protocol packet decoders (DNS, TLS, HTTP/2, QUIC, BGP).
   - Cryptographic primitives and ASN.1 deserializers.
2. **Tier 2 (High Risk)**:
   - Configuration file parsers (YAML, JSON, XML, INI).
   - IPC message deserializers (D-Bus, Protocol Buffers).
3. **Tier 3 (Moderate Risk)**:
   - Command-line argument parsers (`getopt`, custom parsers).
   - Internal string manipulation helpers.

---

## 3. Metrics of a Healthy Fuzzing Campaign

When monitoring a fuzzing campaign (via AFL++ UI or libFuzzer terminal output):

- **Execution Speed**: Aim for $> 1,000$ executions per second per core. If speed drops $< 200$ exec/sec, the target is doing slow synchronous I/O, allocating huge buffers, or spinning in loops.
- **Corpus Growth**: New paths should be discovered regularly during the initial hours.
- **Stability**: Target should report $100\%$ stability. If stability is $< 95\%$, the harness contains non-deterministic behavior (reading random bytes, uninitialized memory, system time, or multi-threaded races).
