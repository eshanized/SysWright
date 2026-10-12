# Scientific Performance Engineering Methodology

Foundational principles for measuring, analyzing, and optimizing software performance on Linux.

---

## 1. The Core Law: Measure Before Optimizing

Premature optimization is the root of extensive technical debt. Intuition regarding where software spends time is notoriously inaccurate.

### Three Iron Invariants:
1. **No Optimization Without a Baseline**: Never modify code for performance reasons without first capturing a reproducible baseline measurement.
2. **On-CPU vs Off-CPU Distinction**:
   - **On-CPU**: The thread is actively running instructions on a CPU core (computations, tight loops, hashing).
   - **Off-CPU**: The thread is blocked waiting for an external event (disk I/O, network packet, lock acquisition, sleep).
   *Optimizing CPU instructions when a thread is blocked 95% of the time on disk I/O will produce near 0% improvement.*
3. **Amdahl's Law**:
   $$\text{Speedup} = \frac{1}{(1 - P) + \frac{P}{S}}$$
   Where $P$ is the fraction of execution time affected by the optimization, and $S$ is the speedup factor of that portion.
   *Example*: If a function accounts for 5% of execution time, making it infinitely fast ($S = \infty$) yields a maximum system speedup of only 5.26%. Always target the dominant bottleneck.

---

## 2. The Universal Performance Lifecycle

```
1. Define Objective (SLA / Target)
       │
2. Profile Workload (Find Bottleneck: CPU, Lock, I/O, Memory)
       │
3. Establish Hypothesis (E.g., "Replacing linear scan with hash map reduces O(N) to O(1)")
       │
4. Apply Minimal Mutation (Isolate exactly 1 change)
       │
5. Measure Under Identical Conditions (N >= 10 trials)
       │
6. Statistical Verification (Calculate Mean, StdDev, p95, p99)
       │
7. Evaluate Secondary Trade-offs (Did memory usage or complexity spike?)
```

---

## 3. Controlling Measurement Noise on Linux

To achieve reproducible micro- and macro-benchmarks on modern multi-core Linux systems:

1. **CPU Frequency Scaling**:
   Dynamic frequency scaling (`intel_pstate`, `amd_pstate`, `cpufreq`) creates massive variance as CPUs throttle up and down.
   ```bash
   # Set performance governor across all cores (requires authorization)
   sudo cpupower frequency-set -g performance
   ```
2. **CPU Pinning and Isolation**:
   Prevent the Linux CFS (Completely Fair Scheduler) from migrating benchmark threads across CPU cores or NUMA nodes:
   ```bash
   # Pin benchmark to isolated CPU cores 2 and 3
   taskset -c 2,3 ./my_benchmark
   ```
3. **Disable ASLR (for deterministic microbenchmarks)**:
   ```bash
   # Run with ASLR disabled to remove cache layout jitter
   setarch x86_64 -R ./my_microbenchmark
   ```
4. **Thermal Throttling**:
   Ensure CPU temperatures remain below thermal thresholds (`sensors` / `turbostat`). Thermal throttling invalidates consecutive runs.

---

## 4. The Benchmark Record Schema

Every performance recommendation must accompany a formal Benchmark Record:

| Field | Description | Example |
|---|---|---|
| **Target Workload** | Exact command, input dataset size, and concurrency | `100,000 JSON records, 16 worker threads` |
| **System Environment** | CPU model, RAM, Kernel, Compiler version | `AMD Ryzen 9 7950X, 64GB DDR5, Linux 6.6.10, GCC 13.2` |
| **Baseline Metric** | Mean $\pm$ StdDev before change | `142.3 ms ± 4.1 ms (p99: 156.0 ms)` |
| **Candidate Metric** | Mean $\pm$ StdDev after change | `88.7 ms ± 2.4 ms (p99: 94.2 ms)` |
| **Delta (%)** | Percentage reduction / throughput gain | `-37.6% execution time (1.60x speedup)` |
| **Statistical Validity** | Sample count ($N$), confidence interval | $N = 20$ runs, $p < 0.001$ |
| **Resource Trade-offs** | Memory footprint, disk I/O, code complexity | Peak RSS increased from 42 MB to 58 MB |
