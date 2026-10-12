# Linux Storage & I/O Profiling: Latency, IOPS, and Throughput

Technical reference for measuring block layer latency, filesystem throughput, IOPS, and queueing behavior on Linux.

---

## 1. Storage Performance Fundamentals

Storage operations are characterized by three interdependent metrics:

$$\text{Throughput (MB/s)} = \text{IOPS} \times \text{Block Size (KB)}$$

1. **IOPS (I/O Operations Per Second)**: Frequency of read/write requests serviced. Dominates random workloads (database indexes, logging).
2. **Throughput (Bandwidth)**: Volume of data transferred per unit time. Dominates sequential workloads (streaming, bulk backup).
3. **Latency**: Time elapsed between issuing a request and receiving completion.
   - **Service Time (`r_await`, `w_await`)**: Time the physical device takes to process the request.
   - **Queue Time**: Time the request spent waiting in the kernel I/O scheduler queue before dispatch.

---

## 2. Real-Time Storage Diagnostics with iostat

`iostat` reports CPU utilization and block device metrics from `/proc/diskstats`:

```bash
# Report extended disk stats (-x) in megabytes (-m) every 1 second
iostat -x -m -z 1
```

### Analyzing iostat Metrics:
```text
Device            r/s     w/s     rMB/s     wMB/s   rrqm/s   wrqm/s  %rrqm  %wrqm  r_await  w_await  aqu-sz  rareq-sz  wareq-sz  %util
nvme0n1         12.00  450.00      0.48     18.20     0.00    24.00   0.00   5.06     0.18     1.24    0.56     41.00     41.42  12.40
```

### Interpretation Rules:
- **`%util`**: Percentage of time during which requests were issued to the device.
  - On single HDDs, `%util > 90%` means saturation.
  - On modern multi-queue NVMe devices with dozens of queues, `%util` can reach 100% while device still has headroom; inspect `r_await` and `w_await` instead.
- **`r_await` / `w_await`**: Average time (in milliseconds) for read/write requests.
  - On NVMe SSD: Expected $< 0.5$ ms. Values $> 5$ ms indicate severe block-layer or device queue contention.
  - On SATA SSD: Expected $< 2$ ms.
- **`aqu-sz` (Average Queue Size)**: Number of requests queued and inflight. Values consistently $\gg 1$ indicate backpressure.

---

## 3. Dissecting I/O Latency Distributions with bpftrace

Averages obscure tail latencies. Use eBPF tools (`biolatency`) to inspect block I/O latency histograms:

```bash
# Trace block I/O latency distribution in microseconds
sudo bpftrace -e '
kprobe:blk_account_io_start { @start[arg0] = nsecs; }
kprobe:blk_account_io_done /@start[arg0]/ {
    @usecs = hist((nsecs - @start[arg0]) / 1000);
    delete(@start[arg0]);
}'
```

Output highlights bimodal latency distributions (e.g., 99% of requests complete in 150 $\mu$s, but 1% take 50 ms due to SSD garbage collection or filesystem journaling syncs).

---

## 4. Controlled Benchmarking with fio

Never use `dd` for storage benchmarking (`dd` uses single-threaded unbuffered synchronous I/O and does not test concurrency, queue depth, or realistic block sizes). Always use `fio` (Flexible I/O Tester):

```ini
; Save as benchmark_workload.fio
[global]
ioengine=libaio
direct=1
runtime=30
time_based=1
size=1G
filename=/tmp/fio_test_file

[random-write-4k-qd32]
rw=randwrite
bs=4k
iodepth=32
numjobs=1
```

```bash
# Run benchmark safely against workspace test file
fio benchmark_workload.fio
rm -f /tmp/fio_test_file
```

> [!CAUTION]
> Never specify a raw disk partition (e.g., `filename=/dev/nvme0n1p2`) in `fio` when benchmarking on user hosts. Doing so immediately overwrites the filesystem and partition table. Always benchmark against a regular file within an allowed temporary or workspace directory.
