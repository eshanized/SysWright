# Crash Analysis: Registers, Stack Unwinding, and Fault Isolation

Technical reference for analyzing register values, stack unwinding, faulting instructions, and signal frames.

---

## 1. System V AMD64 Register Architecture & ABI

When a crash occurs on x86_64, the CPU registers capture the immediate execution state:

| Register | Role in System V AMD64 ABI | Diagnostic Interpretation |
|---|---|---|
| `%rip` | Instruction Pointer | The exact machine instruction that faulted. |
| `%rsp` | Stack Pointer | Current top of the call stack. Clashing or invalid `%rsp` indicates stack overflow or corruption. |
| `%rbp` | Base / Frame Pointer | Base of the current stack frame (if compiled with `-fno-omit-frame-pointer`). |
| `%rdi`, `%rsi`, `%rdx`, `%rcx`, `%r8`, `%r9` | Function Arguments 1 through 6 | Values passed into the function currently executing. |
| `%rax` | Return Value / Arithmetic | Return value of previous function call or operand for calculation. |
| `%eflags` | Condition / Status Flags | Zero flag (ZF), Sign flag (SF), Carry flag (CF), Overflow flag (OF). |

---

## 2. Stack Unwinding and Frame Pointer vs DWARF CFI

To generate a stack backtrace, a debugger must unwind stack frames:

### Method A: Frame Pointer Unwinding (`-fno-omit-frame-pointer`)
- Every function prologue pushes `%rbp` and sets `%rbp = %rsp`.
- Fast, reliable unwinder in kernel, perf, and eBPF.
- Linked list of frames: `*(void**)%rbp` points to caller's `%rbp`, and `*(void**)(%rbp + 8)` is the return address.

### Method B: DWARF Call Frame Information (CFI)
- Binaries built with `-fomit-frame-pointer` use `.eh_frame` or `.debug_frame` sections containing state machine instructions that describe how to restore registers at each instruction offset.
- More complex; if DWARF information is stripped or corrupt, the debugger cannot unwind past the stripped frame, resulting in truncated backtraces (`??`).

---

## 3. Dissecting SIGSEGV Fault Addresses (`si_addr`)

When `SIGSEGV` is trapped via `sigaction`, the `siginfo_t` struct contains `si_addr` (stored in CPU control register `%cr2` at the time of page fault):

### Case 1: NULL Pointer Dereference
```text
Fault address: 0x0000000000000000 or near zero (< 0x1000)
Instruction: mov 0x20(%rax), %rdx  (where %rax == 0)
```
*Diagnosis*: Code dereferenced a `NULL` struct pointer with a field offset of `0x20`.

### Case 2: Non-Canonical Address (Use-After-Free / Poisoned Pointer)
```text
Fault address: 0x6b6b6b6b6b6b6b6b or 0x5a5a5a5a5a5a5a5a
```
*Diagnosis*: Allocator poison pattern!
- `0x6b6b6b6b`: Linux kernel SLAB poison (`POISON_FREE`).
- `0x5a5a5a5a`: FreeBSD / jemalloc junk filling freed memory.
- Pointer points to freed memory that was filled with debug fill bytes.

### Case 3: Stack Overflow
```text
Fault address: 0x7fffff7feff8
Instruction: push %rbp
```
*Diagnosis*: Address is immediately adjacent to the process guard page at the bottom of the stack. A deeply recursive function exhausted the stack allocation (`ulimit -s`).

---

## 4. Signal Handling and Alternative Signal Stacks

When a stack overflow occurs, the kernel attempts to push the signal frame onto the stack. If the stack is exhausted, pushing the signal frame causes another page fault, resulting in immediate process termination without running the signal handler.

### Solution: `sigaltstack(2)`
```c
stack_t ss;
ss.ss_sp = malloc(SIGSTKSZ);
ss.ss_size = SIGSTKSZ;
ss.ss_flags = 0;
sigaltstack(&ss, NULL);

struct sigaction sa;
sa.sa_flags = SA_ONSTACK | SA_SIGINFO;
sa.sa_sigaction = segv_handler;
sigaction(SIGSEGV, &sa, NULL);
```
*Effect*: Catches stack overflows cleanly, allowing backtraces or minidumps to be logged before termination.
