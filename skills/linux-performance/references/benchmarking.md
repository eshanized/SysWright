# Benchmarking Discipline: Statistics, Variance, and Reproducibility

Technical reference for conducting statistically valid performance benchmarks on Linux.

---

## 1. The Fallacy of the Single Measurement

A single run of a benchmark is never evidence of an optimization. Execution time is a non-deterministic random variable affected by:
- CPU frequency governors and thermal states.
- Operating system background scheduling (timer interrupts, kernel workers).
- File system page cache warm/cold states.
- Memory layout randomization (ASLR) and cache line alignment.

---

## 2. Statistical Metrics Required

When comparing a baseline against an optimized candidate, report:

1. **Sample Size ($N$)**: Minimum of 10-30 repeated trials after a discarded warm-up run.
2. **Mean ($\mu$)**: Arithmetic average of the trials.
3. **Standard Deviation ($\sigma$)**: Measure of dispersion / noise. If $\sigma > 5\%$ of $\mu$, the benchmark environment is too noisy; isolate cores or eliminate background tasks before drawing conclusions.
4. **Percentiles**:
   - **Median (p50)**: Middle value, robust against outliers.
   - **95th Percentile (p95)**: SLA boundary for 95% of requests.
   - **99th Percentile (p99)**: Tail latency; exposes worst-case garbage collection or lock contention.

### Student's t-Test for Significance:
Ensure the observed difference between baseline and candidate is statistically significant ($p < 0.05$ or $p < 0.01$) rather than random measurement noise.

---

## 3. Microbenchmarking Tools

### Rust: Criterion.rs
```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn benchmark_sort(c: &mut Criterion) {
    let mut data = vec![5, 2, 8, 1, 9];
    c.bench_function("custom_sort", |b| b.iter(|| {
        custom_sort(black_box(&mut data))
    }));
}
criterion_group!(benches, benchmark_sort);
criterion_main!(benches);
```
*Note: `black_box` prevents the compiler from optimizing away the benchmarked computation when its result is unused.*

### C++: Google Benchmark
```cpp
#include <benchmark/benchmark.h>

static void BM_StringCreation(benchmark::State& state) {
    for (auto _ : state) {
        std::string empty_string;
        benchmark::DoNotOptimize(empty_string);
    }
}
BENCHMARK(BM_StringCreation);
BENCHMARK_MAIN();
```

### CLI Benchmarking: Hyperfine
```bash
hyperfine --warmup 3 \
          --runs 20 \
          --export-json results.json \
          './original_app input.txt' \
          './optimized_app input.txt'
```
*`hyperfine` automatically computes mean, stddev, min, max, statistical speedup factor, and checks for outlier runs.*
