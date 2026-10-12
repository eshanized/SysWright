# Observability Overhead, The Observer Effect, and Privacy Compliance

Technical reference for evaluating profiling overhead, telemetry resource footprints, and preventing secret exposure.

---

## 1. The Observer Effect in Systems Engineering

The Observer Effect states that the act of observing or measuring a system inevitably alters its state, timing, and behavior.

### Measurement Overhead by Tooling:
- **`strace -f`**: Stalls threads on every syscall entry/exit (2 context switches). Overhead: **10x to 50x slowdown**. Can mask concurrency race conditions or cause timeout failures in heartbeat protocols.
- **`perf record` at 997 Hz**: Low-overhead timer/hardware counter sampling. Overhead: **< 1-2% CPU**. Safe for production.
- **eBPF (Tracepoints)**: In-kernel probe with direct memory extraction. Overhead: **< 1-3% CPU**.
- **eBPF (Kprobes on hot functions)**: If attached to a function called millions of times per second (e.g., `tcp_v4_rcv`), can add **15-30% CPU overhead**.
- **Valgrind Memcheck**: Full CPU binary translation. Overhead: **10x to 30x slowdown**. Never use in production.

---

## 2. Rules for Minimizing Tracing Overhead

1. **Avoid Probing Hot In-Kernel Paths**:
   Never attach kprobes to scheduler tick functions (`scheduler_tick`) or network packet per-byte processing loops.
2. **Filter in the Kernel (eBPF)**:
   Never stream all kernel events to user-space and filter them in Python/C. Filter inside the eBPF program (`if (pid != target_pid) return 0;`) so only relevant events are copied to the ring buffer.
3. **Use Ring Buffers with Dropped Counters**:
   Always check for dropped events (`bpf_ringbuf_reserve` failure) to detect when event generation exceeds user-space consumption rate.

---

## 3. Privacy, PII, and Secret Redaction

Observability pipelines frequently leak sensitive customer data or credentials into searchable logs and dashboards:

### Mandatory Redaction Rules:
1. **HTTP Headers**:
   Strictly redact or drop:
   - `Authorization: Bearer <token>`
   - `Cookie: session_id=...`
   - `X-Api-Key: ...`
2. **SQL Query Payloads**:
   Replace literals with parameter placeholders in database spans (`SELECT * FROM users WHERE ssn = ?` instead of `WHERE ssn = '123-45-6789'`).
3. **Process Arguments (`/proc/PID/cmdline`)**:
   Applications that pass passwords via CLI flags (`mysqldump -pSecret123`) leak credentials to all users via `ps` and audit logs. Applications must read credentials from environment variables or secure files (`0600`), and observability agents must sanitize command arguments.
