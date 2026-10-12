# Performance Regressions: Thresholds, Noise, and Automated CI Gates

Technical reference for detecting, measuring, and isolating performance regressions.

---

## 1. Setting Meaningful Regression Thresholds

A common flaw in automated performance CI is setting a rigid 0% tolerance threshold:
```
Baseline: 100ms
Run 2: 101ms -> "BUILD FAILED: Performance Regression Detected!"
```
Due to hardware jitter, background interrupts, and cache line variations, standard deviation ($\sigma$) in benchmarks is routinely 2% to 4%.

### The Multi-Sigma Regression Rule:
A change represents a true performance regression only when:
$$\Delta\text{Latency} > \mu_{\text{baseline}} + 3\sigma_{\text{baseline}}$$
Or when the observed percentage degradation exceeds an established operational SLA threshold (typically $\ge 5\%$ to $10\%$) with statistical significance ($p < 0.01$).

---

## 2. Isolating Performance Regressions with `git bisect`

Performance regressions can be bisected using benchmark timing inside the bisect script:

```bash
#!/usr/bin/env bash
# bisect_perf.sh
set -uo pipefail

make -j"$(nproc)" >/dev/null 2>&1 || exit 125

# Execute 10 benchmark trials using hyperfine
MEAN_TIME=$(hyperfine --warmup 2 --runs 10 --export-json /tmp/perf.json './build/bin/my_app dataset.bin' >/dev/null 2>&1 \
    && jq '.results[0].mean' /tmp/perf.json)

# Threshold: Baseline was 0.120s; regression target is > 0.180s
THRESHOLD="0.180"

if (( $(echo "$MEAN_TIME > $THRESHOLD" | bc -l) )); then
    echo "[BISECT BAD] Mean time ${MEAN_TIME}s exceeds threshold ${THRESHOLD}s"
    exit 1
else
    echo "[BISECT GOOD] Mean time ${MEAN_TIME}s is acceptable"
    exit 0
fi
```
