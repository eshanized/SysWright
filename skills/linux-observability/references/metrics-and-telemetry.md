# Metrics and Telemetry: Prometheus, OpenTelemetry, and Collectors

Technical reference for designing metrics pipelines, instrumenting software, and configuring telemetry collectors on Linux.

---

## 1. Metric Types & Semantics

In Prometheus and OpenTelemetry, metrics adhere to strict semantic types:

| Metric Type | Mathematical Behavior | When to Use | Prometheus Query Function |
|---|---|---|---|
| **Counter** | Monotonically increasing cumulative integer/float; resets to 0 only on process restart. | Request counts, error counts, bytes sent. | `rate()`, `increase()` |
| **Gauge** | Arbitrary numerical value that can increase or decrease over time. | Memory usage, CPU temperature, active thread count, queue size. | Direct value, `avg_over_time()` |
| **Histogram** | Samples observations (usually durations or payload sizes) into configurable discrete buckets. | Request latency (p50, p90, p99), payload sizes. | `histogram_quantile(0.99, ...)` |
| **Summary** | Computes quantiles directly on the client side over a sliding time window. | When client-side quantiles are strictly necessary. | Cannot be aggregated across multiple server replicas! |

> [!WARNING]
> Never call `rate()` on a Gauge! `rate()` assumes any decrease in value represents a counter reset/restart, leading to completely nonsensical negative or inflated spike calculations. Always use `rate()` on Counters, and `avg()` or `max()` on Gauges.

---

## 2. Metric Exposition Formats

Modern applications expose metrics over HTTP via Prometheus text format:

```text
# HELP http_requests_total Total number of HTTP requests processed.
# TYPE http_requests_total counter
http_requests_total{method="GET",handler="/api/v1/status",code="200"} 148201
http_requests_total{method="POST",handler="/api/v1/login",code="401"} 12

# HELP process_resident_memory_bytes Resident memory size in bytes.
# TYPE process_resident_memory_bytes gauge
process_resident_memory_bytes 48291072
```

---

## 3. OpenTelemetry (OTel) Collector Architecture

In complex distributed architectures, host telemetry is aggregated via the OpenTelemetry Collector:

```
[Applications (OTel SDK)] ────► [Local OTel Agent (systemd)] ────► [Central Backend]
[Node Exporter (/proc)]   ────►         (Receivers)                (Prometheus / Jaeger /
[eBPF Network Telemetry]  ────►     (Processors: Batch, Filter)     ClickHouse)
                                        (Exporters)
```

### Key Collector Configuration Directives:
- **Batch Processor**: Groups metrics and spans to reduce network packet overhead.
- **Filter Processor**: Drops unwanted high-cardinality labels before storage.
- **Memory Limiter Processor**: Prevents the collector agent itself from exceeding a bounded RAM ceiling (`check_interval: 1s`, `limit_percentage: 75`).
