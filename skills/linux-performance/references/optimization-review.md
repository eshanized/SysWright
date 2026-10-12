# Performance Optimization Review & Trade-Off Evaluation

Checklist and guidelines for reviewing performance optimization patches and evaluating secondary trade-offs.

---

## 1. The Optimization Review Checklist

Before accepting any performance optimization patch, answer these four questions:

1. **Is the bottleneck substantiated by empirical profiling data?**
   - *Requirement*: A flame graph, `perf report`, or `heaptrack` dump demonstrating that the affected function consumed significant CPU cycles or memory.
2. **Was the optimization tested with a representative workload?**
   - *Requirement*: Synthetic microbenchmarks often fail to reflect cache pressure, memory layout, and concurrency in realistic workloads.
3. **What is the secondary trade-off cost?**
   - *Questions*:
     - Did RAM usage increase to save CPU (e.g., memoization, lookup tables)?
     - Did binary size balloon due to aggressive loop unrolling or template inlining?
     - Did code readability or maintainability suffer?
4. **Is the improvement statistically significant?**
   - *Requirement*: Rejection of claims asserting "3% improvement" derived from a single run when baseline variance is ±4%.

---

## 2. Common Premature Optimizations to Reject

| Proposed Optimization | Why It Should Often Be Rejected |
|---|---|
| Replacing clear standard library functions with manual bit-twiddling | Modern compilers (GCC/Clang `-O2`/`-O3`) already autovectorize and generate optimal SIMD instructions; manual bit-twiddling harms readability and often defeats compiler optimization passes. |
| Over-aggressive manual inlining (`inline` / `always_inline`) | Increases instruction cache (I-cache) footprint and LLC misses, potentially slowing down the whole application. |
| Caching data without invalidation or memory bounds | Creates unbounded memory leaks and stale state bugs. |
| Premature multi-threading for small workloads | Thread creation, context switching, and synchronization overhead often take longer than running the computation sequentially. |

---

## 3. Algorithmic vs Micro-Optimizations

Prioritize optimization efforts in descending order of impact:

```
1. Algorithmic Complexity (O(N^2) -> O(N log N) -> O(1))  [Impact: 10x - 1000x]
       │
2. I/O Reduction (Caching, Batching, Async I/O)           [Impact: 5x - 50x]
       │
3. Data Locality & Cache Layout (SoA vs AoS)             [Impact: 2x - 10x]
       │
4. Micro-Optimizations (SIMD, Loop unrolling, inlining)   [Impact: 1.1x - 1.5x]
```
