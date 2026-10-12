# Linux CPU Profiling: perf, Counters, and Flame Graphs

Comprehensive guide to profiling CPU utilization, instruction efficiency, hardware performance counters, and callgraphs on Linux.

---

## 1. The Linux `perf` Subsystem Architecture

`perf` uses the kernel's `perf_event_open(2)` system call to sample CPU state based on hardware performance counters (PMU) or software timer events.

### Security and Privileges:
The sysctl `kernel.perf_event_paranoid` controls unprivileged access:
- `3`: Disallow all unprivileged access.
- `2` (Default on many distros): Disallow kernel profiling for unprivileged users.
- `1`: Allow kernel and user profiling without tracepoints.
- `0`: Allow raw tracepoint access.
- `-1`: Full unconstrained access (not recommended).
*Note: In Linux 5.8+, `CAP_PERFMON` allows system profiling without granting full `CAP_SYS_ADMIN`.*

---

## 2. Essential perf CLI Commands

```bash
# 1. Summary statistics of CPU counters during workload execution
perf stat -d ./my_workload

# 2. Sample CPU execution at 997 Hz with callgraphs (-g)
perf record -F 997 -g -- ./my_workload

# 3. Interactive TUI report of hotspots
perf report -g 'graph,0.5,caller'

# 4. Annotate assembly of hottest function with source lines
perf annotate --stdio -M intel my_hot_function
```

### Why sample at 997 Hz instead of 1000 Hz?
Sampling at a prime frequency (e.g., 997 Hz or 99 Hz) prevents lockstep synchronization with periodic timer interrupts, thread scheduling slices (100 Hz / 250 Hz / 1000 Hz `CONFIG_HZ`), or periodic cron jobs, which would skew statistical sampling.

---

## 3. Interpreting Hardware Performance Counters

When analyzing `perf stat -d` output:

```text
       1,452.12 msec task-clock                       #    3.921 CPUs utilized          
            812      context-switches                 #  559.182 /sec                   
             45      cpu-migrations                   #   31.000 /sec                   
          4,120      page-faults                      #    2.837 K/sec                  
  5,214,812,901      cycles                           #    3.591 GHz                    
  7,822,109,410      instructions                     #    1.50  insn per cycle (IPC)   
  1,421,098,300      branches                         #  978.637 M/sec                  
     14,210,983      branch-misses                    #    1.00% of all branches        
  2,104,800,100      L1-dcache-loads                  #    1.449 G/sec                  
     63,144,003      L1-dcache-load-misses            #    3.00% of all L1-dcache hits  
      5,120,400      LLC-loads                        #    3.526 M/sec                  
      1,024,080      LLC-load-misses                  #   20.00% of all LLC-loads       
```

### Diagnostic Key Metrics:
- **IPC (Instructions Per Cycle)**:
  - $\text{IPC} > 2.0$: CPU-bound compute; pipeline is efficiently utilizing ALUs.
  - $\text{IPC} < 1.0$: Memory-stalled; CPU is waiting on L1/L2/L3 cache misses or main memory DRAM latency.
- **Branch Miss Rate**:
  - $> 5\%$: Branch predictor is failing; unpredictable conditional logic in tight loops causes pipeline flushes (15-20 cycle penalty per miss). Solution: branchless algorithms, lookup tables, or compiler `__builtin_expect`.
- **LLC (Last Level Cache) Misses**:
  - High LLC miss rate indicates poor cache locality; CPU execution is bottlenecked by DRAM bus bandwidth. Solution: Cache-conscious data layout (Struct-of-Arrays instead of Array-of-Structs, cacheline alignment).

---

## 4. Flame Graph Generation

Flame graphs visualize hierarchical call stacks, where the horizontal axis represents population (percentage of samples) and vertical axis represents stack depth.

```bash
# Capture with frame pointers or DWARF
perf record -F 997 -g --call-graph dwarf ./my_workload

# Script perf samples to folded format
perf script | ./stackcollapse-perf.pl > out.perf-folded

# Generate interactive SVG flame graph
./flamegraph.pl out.perf-folded > flamegraph.svg
```
