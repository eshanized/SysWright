# Interactive Debugging with GDB and LLDB

Guide to interactive debugging, disassembly, watchpoints, stack inspection, and automation on Linux.

---

## 1. GDB vs LLDB Command Mapping

| Action | GDB Syntax | LLDB Syntax |
|---|---|---|
| Start process | `gdb --args ./binary arg1 arg2` | `lldb -- ./binary arg1 arg2` |
| Attach to PID | `gdb -p 1234` | `lldb -p 1234` |
| Load core dump | `gdb ./binary /path/to/core` | `lldb -c /path/to/core ./binary` |
| Set breakpoint | `break filename.c:42` or `b func_name` | `breakpoint set --file filename.c --line 42` or `b func_name` |
| Conditional break | `break filename.c:42 if count > 100` | `breakpoint set --file filename.c --line 42 -c 'count > 100'` |
| Hardware watchpoint | `watch var` / `rwatch var` (read) | `watchpoint set variable var` |
| Run / Continue | `run` / `continue` (`c`) | `run` / `continue` (`c`) |
| Step over / into | `next` (`n`) / `step` (`s`) | `next` (`n`) / `step` (`s`) |
| Step instruction | `nexti` (`ni`) / `stepi` (`si`) | `thread step-inst-over` / `thread step-inst` |
| Backtrace | `backtrace` (`bt`) or `bt full` | `thread backtrace` (`bt`) or `bt all` |
| Frame inspection | `frame <n>` (`f <n>`), `info locals` | `frame select <n>`, `frame variable` |
| Inspect registers | `info registers` (`i r`) | `register read` |
| Disassemble | `disassemble /m <func>` | `disassemble -m -n <func>` |
| Memory dump | `x/16xg $rsp` (16 giant words hex) | `memory read -c 16 -f x -s 8 $rsp` |

---

## 2. Advanced GDB Techniques

### Hardware Watchpoints
Hardware watchpoints use CPU debug registers (DR0-DR3 on x86_64) to trap when memory is written or read without incurring software interpretation overhead:
```text
(gdb) watch *0x7fffffffd480
Hardware watchpoint 1: *0x7fffffffd480
(gdb) continue
Hardware watchpoint 1: *0x7fffffffd480

Old value = 0
New value = 42
0x0000555555555189 in worker_thread (arg=0x0) at worker.c:18
18          *shared_val = 42;
```

### Catching System Calls and Signals
```text
(gdb) catch syscall write
Catchpoint 1 (syscall 'write' [1])
(gdb) catch signal SIGSEGV
Catchpoint 2 (signal SIGSEGV)
```

### Multi-Threaded Debugging
```text
(gdb) info threads
  Id   Target Id                                   Frame 
* 1    Thread 0x7ffff7c8b740 (LWP 4821) "main"     0x00007ffff7e06a3e in __GI___nanosleep ...
  2    Thread 0x7ffff748a640 (LWP 4822) "worker1"  0x00007ffff7e5a1b0 in __pthread_cond_wait ...
  3    Thread 0x7ffff6c89640 (LWP 4823) "worker2"  0x0000555555555230 in compute (data=0x0) at math.c:85

(gdb) thread 3
(gdb) bt
(gdb) thread apply all bt full
```

---

## 3. Dealing with Optimized Binaries (-O2 / -O3)

Optimizations introduce transformations that confound debugger state:
- Inlining: Functions disappear from call stack; GDB marks frames as `<inlined by>`.
- Register allocation: Variables marked `<optimized out>`.
- Instruction reordering: Stepping through source lines jumps non-linearly.

### Best Practices:
1. When building for reproduction, use `-Og -g3`:
   - `-Og`: Enables safe optimizations that do not distort debugging information.
   - `-g3`: Includes macro definitions (`info macro MACRO_NAME`).
2. If forced to debug production `-O2` binaries:
   - Check register state directly (`info registers`).
   - Disassemble the current instruction (`disassemble /r $rip-16,$rip+16`).
   - Track calling conventions (System V AMD64 ABI: arguments in `%rdi`, `%rsi`, `%rdx`, `%rcx`, `%r8`, `%r9`).

---

## 4. Automation via Python Scripting in GDB

GDB provides an embedded Python interpreter to automate state verification:
```python
# Save as check_tree.py and load in gdb: source check_tree.py
import gdb

class CheckTreeCmd(gdb.Command):
    """Check binary tree for cycles."""
    def __init__(self):
        super(CheckTreeCmd, self).__init__("check-tree", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        val = gdb.parse_and_eval(arg)
        visited = set()
        stack = [val]
        while stack:
            node = stack.pop()
            if int(node) == 0:
                continue
            if int(node) in visited:
                print(f"Cycle detected at node address: {hex(int(node))}")
                return
            visited.add(int(node))
            stack.append(node['left'])
            stack.append(node['right'])
        print(f"Tree valid: {len(visited)} nodes inspected.")

CheckTreeCmd()
```
