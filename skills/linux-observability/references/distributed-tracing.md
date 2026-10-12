# Distributed Tracing: W3C Context Propagation and Spans

Technical reference for implementing distributed tracing, context propagation across threads/IPC, and sampling strategies on Linux.

---

## 1. Core Anatomy of a Trace

A distributed trace is represented as a Directed Acyclic Graph (DAG) of Spans:

```
[Span A: Frontend Gateway HTTP Request] (Trace ID: 4bf92f3577b34da6a3ce929d0e0e4736)
      │
      ├──► [Span B: Auth Verification RPC]
      │
      └──► [Span C: Backend Database Query (Span ID: 00f067aa0ba902b7)]
                 └── Parent Span ID: [Span A]
```

### Essential Span Fields:
- `trace_id`: Globally unique 16-byte hex identifier shared by all spans in this single request execution.
- `span_id`: Unique 8-byte hex identifier for this specific operation.
- `parent_span_id`: Identifies the caller span (empty on root span).
- `start_time` / `end_time`: High-resolution microsecond timestamps.
- `attributes`: Key-value metadata (e.g., `db.system = "postgresql"`, `http.status_code = 200`).
- `events`: Structured timestamped log entries within the span (e.g., `exception`, `cache_miss`).

---

## 2. W3C Trace Context Propagation

When a request crosses network or IPC boundaries (HTTP, gRPC, D-Bus, UNIX socket), trace context is propagated via standard W3C HTTP headers:

### The `traceparent` Header Format:
```text
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
              │                 │                         │         │
           version          trace_id                   span_id    flags (01 = sampled)
```

1. **Version**: Currently `00`.
2. **Trace ID**: 32 hex characters.
3. **Parent ID (Span ID)**: 16 hex characters.
4. **Trace Flags**: 8-bit field where bit 0 indicates whether the trace was sampled (`01` = record and export, `00` = not sampled).

---

## 3. Sampling Strategies

Generating spans for 100% of requests in high-throughput production systems exhausts network bandwidth and backend disk storage.

| Sampling Method | How It Works | Trade-offs |
|---|---|---|
| **Head-Based Sampling** | Root service decides whether to sample at request ingress (e.g., 1% probabilistic). | Low overhead; cannot guarantee that interesting error cases or slow p99 outliers are captured. |
| **Tail-Based Sampling** | The OpenTelemetry Collector buffers all spans in memory until the trace completes, then samples 100% of traces containing HTTP 5xx errors or latency $> 500\text{ms}$. | Guarantees capturing anomalies; requires collector memory buffering. |
| **Rate-Limiting Sampling** | Caps maximum spans recorded to a fixed quota per second (e.g., 100 traces/sec). | Prevents traffic spikes from overwhelming observability collectors. |
