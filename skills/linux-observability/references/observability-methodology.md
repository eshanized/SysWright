# Observability Methodology: Signals, Metrics Models, and Cardinality

Methodological reference for telemetry signal selection, RED/USE frameworks, and metric cardinality management.

---

## 1. Comparing the Core Observability Signals

Do not use observability terms interchangeably:

| Signal | Definition | Best Used For | Weakness |
|---|---|---|---|
| **Metric** | Numeric value sampled at regular time intervals ($t$). | Trend analysis, alerting, SLI/SLO tracking, capacity planning. | Lacks context; cannot explain *why* a specific individual request failed. |
| **Log** | Timestamped text or JSON document emitted on an event. | Post-mortem investigation, detailed error stacks, audit records. | High volume and storage cost; expensive to search at scale. |
| **Trace** | Causal journey of a transaction across distributed services. | Pinpointing network latency hops and service dependencies. | Requires context propagation across all network and thread hops; sampling required. |
| **Profile** | Statistical sampling of CPU instruction pointers and callstacks. | Code-level performance hotspots, memory leak identification. | Overhead when sampling continuously; requires debug symbols. |

---

## 2. Telemetry Modeling Frameworks: USE vs RED

### The USE Method (For Infrastructure & Resources)
Created by Brendan Gregg for servers, CPUs, disks, and network interfaces:
- **Utilization**: The average time that the resource was busy servicing work (e.g., Disk %util, CPU 85%).
- **Saturation**: The degree to which extra work is queued waiting for the resource (e.g., Runqueue length, I/O wait queue, TCP backlog).
- **Errors**: Count of error events (e.g., Device read retries, ECC memory corrections, NIC packet drops).

### The RED Method (For Services & Requests)
Created by Tom Wilkie for microservices and HTTP/gRPC APIs:
- **Rate**: The number of requests being serviced per second.
- **Errors**: The number of failing requests per second (e.g., HTTP 5xx responses).
- **Duration**: The amount of time requests take (latency distribution, p50, p95, p99).

---

## 3. The High Cardinality Trap

Cardinality refers to the number of unique combinations of label/tag dimensions on a metric.

### The Problem:
Every unique combination of labels creates an independent time-series in a metrics database (Prometheus / InfluxDB).
$$\text{Total Series} = \prod (\text{Count of unique values for each label})$$

### The Cardinality Explosion Anti-Pattern:
```promql
# DANGEROUS ANTI-PATTERN: High cardinality labels in metrics
http_requests_total{method="GET", user_id="1849204", request_id="f81d4fae-7dec-11d0-a765-00a0c91e6bf6"}
```
- A million users $\times$ millions of UUID request IDs generates billions of time-series, causing the Prometheus server or OpenTelemetry agent to crash with Out-Of-Memory (OOM).

### Cardinality Rules:
1. **Never** include unbounded values (`user_id`, `request_id`, `email`, `timestamp`, `ip_address`) as metric labels.
2. Store high-cardinality identifiers in **structured logs** or **distributed trace span attributes**, where storage is append-only and indexed per record.
3. Keep metric labels strictly bounded to finite enumerations (`http_status_code`, `method`, `service_name`, `datacenter`).
