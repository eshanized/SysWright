# Linux Network Performance: Throughput, Latency, and Socket Tuning

Technical reference for diagnosing network performance bottlenecks, socket buffers, TCP parameters, and kernel offloads.

---

## 1. Network Performance Metrics

| Metric | Measurement Unit | Primary Contributing Factors |
|---|---|---|
| **Bandwidth / Throughput** | Gbps / Mbps | MTU size, TCP window size, NIC link speed, CPU core saturation |
| **Round-Trip Time (RTT)** | Milliseconds ($\mu$s LAN) | Physical distance, serialization delay, queueing delay (Bufferbloat) |
| **Packet Loss Rate** | Percentage (%) | Congested routers, physical cable noise, ring buffer drops, TCP backlog overflow |
| **Connection Establishment Rate** | Connections/sec (CPS) | `SYN` queue depth, `accept()` event loop latency, socket port exhaustion |

---

## 2. Kernel Socket Buffer Sizing and Auto-Tuning

The Linux kernel auto-tunes TCP socket buffer sizes (`tcp_rmem` and `tcp_wmem`) based on the Bandwidth-Delay Product (BDP):

$$\text{BDP (Bytes)} = \text{Bandwidth (Bytes/sec)} \times \text{RTT (Seconds)}$$

### Example BDP Calculation:
- 10 Gbps link with 20 ms RTT:
  $$\text{BDP} = \left(\frac{10 \times 10^9}{8}\right) \times 0.020 = 1.25 \times 10^9 \times 0.020 = 25,000,000\text{ Bytes} \approx 25\text{ MB}$$
- If the socket buffer is capped at the default 4 MB, maximum possible TCP throughput is throttled to:
  $$\text{Max Throughput} = \frac{4\text{ MB}}{0.020\text{ s}} = 200\text{ MB/s} = 1.6\text{ Gbps (16% of capacity)}$$

### Verifying TCP Memory Settings:
```bash
# Read min, default, max buffer sizes (in bytes)
cat /proc/sys/net/ipv4/tcp_rmem
# 4096    131072  6291456
cat /proc/sys/net/ipv4/tcp_wmem
# 4096    16384   4194304
```

---

## 3. Investigating Packet Drops & Buffer Overflow with ss

The `ss` command reveals socket-level queue drops, unacknowledged packets, and TCP congestion window (`cwnd`):

```bash
# Inspect internal TCP socket state (-t), internal stats (-i), memory (-m)
ss -tiem 'sport = :8080'
```

```text
ESTAB  0  128  192.168.1.10:8080  192.168.1.50:49210
     skmem:(r0,rb131072,t0,tb16384,f0,w0,o0,bl0,d0)
     cubic rtt:18.412/0.245 rto:220 ato:40 mss:1448 rcvspace:14600 ssthresh:20 cwnd:10
     data_segs_out:1420 retrans:2/12 (16.6%) lost:2
```

### Key Diagnostic Indicators:
- **`retrans:2/12`**: Indicates 16.6% packet retransmission on this active socket.
- **`bl0` (Backlog drop)**: Drops occurring in socket backlog queue because application's user-space `accept()` or `read()` loop is too slow to service incoming packets.
- **`rcvspace`**: Receiver advertised window capacity.

---

## 4. Controlled Throughput Testing with iperf3

Never claim network optimization by curling a random public internet domain. Use controlled local or peer endpoints with `iperf3`:

```bash
# On server:
iperf3 -s -p 5201

# On client: Test single-stream TCP throughput with 10-second duration (-t 10)
iperf3 -c 192.168.1.10 -p 5201 -t 10

# Test multi-stream throughput (4 parallel streams -P 4)
iperf3 -c 192.168.1.10 -p 5201 -P 4 -t 10
```
