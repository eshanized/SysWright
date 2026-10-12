# Concurrency Debugging: Deadlocks, Races, and Synchronization

Technical reference for diagnosing multi-threaded race conditions, deadlocks, lock contention, and memory ordering defects.

---

## 1. Concurrency Defect Categories

| Defect Class | Definition | Diagnostic Approach |
|---|---|---|
| **Data Race** | Two or more threads concurrently access the same memory location, at least one access is a write, and no synchronization (mutex or atomic) orders the accesses. | ThreadSanitizer (`-fsanitize=thread`), Helgrind |
| **Deadlock** | Two or more threads are permanently blocked waiting for locks held by each other (Circular wait / ABBA locking). | GDB `thread apply all bt`, Lockdep (kernel) |
| **Lock Contention** | High proportion of CPU time spent waiting for mutexes, reducing throughput. | `perf lock`, `bpftrace` |
| **Priority Inversion** | A low-priority thread holds a lock needed by a high-priority thread, but is preempted by a medium-priority thread. | Priority inheritance mutexes (`PTHREAD_PRIO_INHERIT`) |
| **Atomic Memory Ordering Violation** | Using `memory_order_relaxed` when `acquire`/`release` semantics are required to publish data across threads. | ThreadSanitizer, TSO/ARM memory models |

---

## 2. Diagnosing Deadlocks with GDB

When a process hangs completely with near 0% CPU consumption, attach GDB to inspect thread call stacks:

```bash
gdb -p $(pgrep my_hung_daemon)
```

```text
(gdb) info threads
  Id   Target Id                                   Frame 
* 1    Thread 0x7ffff7c8b740 (LWP 1001) "worker_A" 0x00007ffff7e5a1b0 in __futex_abstimed_wait64 ()
  2    Thread 0x7ffff748a640 (LWP 1002) "worker_B" 0x00007ffff7e5a1b0 in __futex_abstimed_wait64 ()

(gdb) thread apply all bt

Thread 1 (LWP 1001):
#0  0x00007ffff7e5a1b0 in __futex_abstimed_wait64 ()
#1  0x00007ffff7e5c543 in pthread_mutex_lock ()
#2  0x0000555555555234 in transfer_funds (src=0x555555558010, dst=0x555555558050) at bank.c:45
    -> Holds lock on src (0x555555558010), waiting for dst (0x555555558050)

Thread 2 (LWP 1002):
#0  0x00007ffff7e5a1b0 in __futex_abstimed_wait64 ()
#1  0x00007ffff7e5c543 in pthread_mutex_lock ()
#2  0x0000555555555234 in transfer_funds (src=0x555555558050, dst=0x555555558010) at bank.c:45
    -> Holds lock on src (0x555555558050), waiting for dst (0x555555558010)
```

### Analysis and Remediation:
- **Classic ABBA Deadlock**: Thread 1 acquired lock A and requests lock B; Thread 2 acquired lock B and requests lock A.
- **Architectural Solution**: Enforce strict global lock ordering. For arbitrary pointer locks, order by pointer address:
```c
if ((uintptr_t)src < (uintptr_t)dst) {
    pthread_mutex_lock(&src->mutex);
    pthread_mutex_lock(&dst->mutex);
} else {
    pthread_mutex_lock(&dst->mutex);
    pthread_mutex_lock(&src->mutex);
}
```

---

## 3. ThreadSanitizer (TSan)

ThreadSanitizer intercepts memory accesses and pthread synchronization events to detect data races even if a particular run didn't corrupt data:

```bash
gcc -fsanitize=thread -O1 -g3 my_threaded_app.c -o my_threaded_app
```

```text
==================
WARNING: ThreadSanitizer: data race (pid=8921)
  Write of size 4 at 0x7fffffffd480 by thread T2:
    #0 worker_increment /home/user/app/threads.c:19 (my_threaded_app+0x1254)
    #1 start_thread /usr/lib/libc.so.6 (libc.so.6+0x8b740)

  Previous Read of size 4 at 0x7fffffffd480 by thread T1:
    #0 worker_read /home/user/app/threads.c:32 (my_threaded_app+0x12a8)
    #1 start_thread /usr/lib/libc.so.6 (libc.so.6+0x8b740)

  Location is stack of main thread at 0x7fffffffd000.
==================
```

---

## 4. Signal Safety Rules

Calling non-async-signal-safe functions from signal handlers (e.g., `SIGINT`, `SIGTERM`) causes re-entrancy deadlocks and heap corruption:
- Never call `malloc()`, `free()`, `printf()`, `syslog()`, or `pthread_mutex_lock()` inside a signal handler.
- Strictly use `sig_atomic_t` or atomic flags (`atomic_bool`) and notify main loops via `write()` on a self-pipe or `signalfd(2)`.
