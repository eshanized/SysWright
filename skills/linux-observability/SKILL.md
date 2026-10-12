---
name: linux-observability
description: Linux observability, tracing, and telemetry specialist. Designs non-invasive visibility architectures across Linux kernels and user-space systems. Harnesses Linux native interfaces (/proc, /sys, tracefs, ftrace, kprobes, uprobes, cgroups, PSI), engineers eBPF programs (CO-RE, libbpf, bpftrace, ring buffers, verifier troubleshooting), defines metrics/logs/traces telemetry pipelines, and evaluates observer effect and privacy overhead.
license: Apache-2.0
compatibility: Requires Linux environment, modern kernel with eBPF/BTF support.
metadata:
  author: Linux Engineering Contributors
  version: "0.1.0"
---

# Linux Observability Specialist

The `linux-observability` skill guides AI agents through system-wide and application-level observability on Linux using native kernel interfaces, eBPF, structured telemetry, and tracing.

---

## 1. Observability Signal Triad & Workflow

```mermaid
flowchart TD
    REQ["Observability Requirement"] --> TYPE{"Determine Primary Signal Type"}
    TYPE -->|Aggregated Trends & SLAs| METRIC["Metrics (Prometheus / OTel)\n- High frequency, Low cardinality\n- Gauges, Counters, Histograms"]
    TYPE -->|Discrete Contextual Events| LOG["Structured Logs (journald / JSON)\n- Detailed payload, High storage\n- Timestamped discrete events"]
    TYPE -->|Request Flow Across Boundaries| TRACE["Distributed Tracing (OTel / W3C)\n- Trace ID, Span ID, Parent Context\n- End-to-end request journeys"]
    TYPE -->|Kernel & Syscall Deep Inspection| EBPF["eBPF & Dynamic Tracing (bpftrace / libbpf)\n- Low overhead, Zero application modification\n- Kprobes, Tracepoints, Ring buffers"]

    METRIC --> OVERHEAD{"Evaluate Observer Effect & Privacy"}
    LOG --> OVERHEAD
    TRACE --> OVERHEAD
    EBPF --> OVERHEAD
    OVERHEAD -->|High Cardinality / Privacy Leak| REDACT["Sanitize Fields & Bound Cardinality"]
    OVERHEAD -->|Safe & Bounded| DEPLOY["Deploy Instrumentation"]
```

### The 4 Pillars of Observability:
1. **Metrics**: Aggregatable numeric measurements over time intervals. Perfect for alerting, dashboards, and error rates. Low storage footprint when cardinality is controlled.
2. **Logs**: Append-only timestamped records of discrete events. Carries rich context (user IDs, error messages, parameters).
3. **Traces**: Directed acyclic graphs of spans tracking a single execution transaction as it traverses threads, processes, and network microservices.
4. **Dynamic Profiling / Tracing (eBPF)**: Non-invasive, in-kernel probe execution tracking kernel functions, syscall latency, lock contention, and I/O events without modifying binary sources.

---

## 2. Linux Native Tracing Interfaces

| Interface | Path / Mechanism | Capability | Overhead & Safety |
|---|---|---|---|
| **tracefs** | `/sys/kernel/tracing` | Built-in ftrace engine, function graphs, tracepoints | Negligible when disabled; modest when tracing filtered events |
| **Kernel Tracepoints** | `TRACE_EVENT` macros in kernel code | Stable ABI hooks into kernel subsystems (sched, net, block) | Zero overhead when disabled; highly stable across kernel versions |
| **Kprobes / Kretprobes** | Dynamic kernel instruction breakpointing | Instruments any non-inlined kernel function | Moderate overhead; probe points may shift across kernel updates |
| **Uprobes / Uretprobes** | User-space instruction breakpointing | Instruments user-space functions in shared libraries and executables | Higher overhead (trap to kernel); useful for tracing SSL/TLS and glibc |
| **eBPF (BPF)** | `bpf(2)` system call + JIT compiler | Executes sandboxed bytecode directly inside kernel event loops | Fast in-kernel processing; verifier prevents crashes |

---

## 3. Operational Safety Boundaries

- **Tier 0 (Diagnostics)**: Reading `/proc/stat`, `/proc/loadavg`, `/proc/pressure/*` (PSI), and journal logs is fully autonomous.
- **Tier 3 (Host Mutating / Privileged)**: Loading eBPF programs into the kernel (`bpf(2)`), attaching kprobes, modifying `/sys/kernel/tracing`, or deploying system-wide audit rules requires explicit human authorization.
- **Privacy & Secret Protection**: Never log raw cryptographic keys, authorization headers (`Bearer ...`), credit card numbers, or passwords in observability pipelines.

---

## 4. Reference Library

- [observability-methodology.md](references/observability-methodology.md) — Four signal pillars, RED vs USE metrics, and cardinality control.
- [linux-native-observability.md](references/linux-native-observability.md) — `/proc`, `/sys`, tracefs, cgroups v2, and Pressure Stall Information (PSI).
- [perf-and-tracing.md](references/perf-and-tracing.md) — ftrace, tracepoints, kprobes, uprobes, and trace-cmd.
- [ebpf-architecture.md](references/ebpf-architecture.md) — BPF verifier, program types, maps, BTF, CO-RE, and ring buffers.
- [libbpf-and-bpftrace.md](references/libbpf-and-bpftrace.md) — Authoring bpftrace scripts, libbpf skeletons, and troubleshooting verifier rejections.
- [metrics-and-telemetry.md](references/metrics-and-telemetry.md) — Prometheus counters/gauges/histograms, OpenTelemetry collectors, and cardinality traps.
- [distributed-tracing.md](references/distributed-tracing.md) — W3C Trace Context, spans, context propagation, and sampling strategies.
- [privacy-and-overhead.md](references/privacy-and-overhead.md) — The Observer Effect, CPU/memory overhead, data redaction, and compliance.
