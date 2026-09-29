# C Systems Programming for Linux

## 1. Scope & Standards

C remains foundational for Linux kernel modules, system daemons, core utility suites, and stable C ABI dynamic libraries. This reference defines defensive C engineering practices targeting **C11 / POSIX.1-2008** on modern Linux systems (glibc / musl).

---

## 2. Memory Safety & Resource Lifetime Management

Because C lacks automated garbage collection and language-level RAII, resource ownership must be strictly codified:

### 2.1 The Allocation-Ownership Contract
- **Explicit Ownership**: Every allocated resource (`malloc`, `open`, `socket`, `fopen`) must have a single designated owner responsible for its destruction (`free`, `close`, `fclose`).
- **Transfer of Ownership**: Document whether a function borrows a pointer or takes ownership:
  ```c
  /* BORROWS: caller retains ownership of 'config'; function must not free it */
  int daemon_apply_config(const struct daemon_config *config);

  /* TAKES OWNERSHIP: caller transfers ownership of 'msg' to queue; queue will free it */
  int queue_push_transfer(struct message_queue *q, struct message *msg);
  ```
- **Cleanup GOTO Pattern**: In functions managing multiple resource acquisitions, use single-point-of-exit error unwinding:
  ```c
  int process_file(const char *path) {
      int ret = -1;
      int fd = -1;
      char *buffer = NULL;

      fd = open(path, O_RDONLY | O_CLOEXEC);
      if (fd < 0) {
          perror("open");
          goto out;
      }

      buffer = malloc(BUFFER_SIZE);
      if (!buffer) {
          perror("malloc");
          goto out_close;
      }

      /* Core processing logic */
      ret = 0;

  out_close:
      free(buffer);
      close(fd);
  out:
      return ret;
  }
  ```

### 2.2 GCC/Clang Cleanup Attribute (`__attribute__((cleanup))`)
On GCC/Clang platforms, use RAII-like automated cleanup:
```c
static inline void autofree(void *p) {
    void **ptr = (void **)p;
    free(*ptr);
}
#define _autofree_ __attribute__((cleanup(autofree)))

static inline void autoclosing(int *p) {
    if (*p >= 0) close(*p);
}
#define _autoclose_ __attribute__((cleanup(autoclosing)))
```

---

## 3. Defensive Programming: Avoiding Undefined Behavior

1. **Strict Pointer Verification & Nulling**:
   - Check every return from `malloc`, `calloc`, and `realloc`.
   - After `free(ptr);`, immediately set `ptr = NULL;` to prevent dangling use-after-free bugs.
2. **Buffer Bounds & String Safety**:
   - Forbid dangerous, unbounded legacy functions: `strcpy`, `strcat`, `sprintf`, `gets`.
   - Prefer bounded, size-explicit alternatives: `snprintf`, `strnlen`, `memmove`.
   - When copying strings into fixed-size buffers, guarantee null termination:
     ```c
     snprintf(dest, sizeof(dest), "%s", src);
     ```
3. **Integer Overflow & Arithmetic Protection**:
   - Check for integer overflow before arithmetic in buffer sizing:
     ```c
     if (count > SIZE_MAX / sizeof(struct item)) {
         return -EINVAL; /* Overflow prevented */
     }
     struct item *items = malloc(count * sizeof(struct item));
     ```
   - On GCC/Clang, use compiler built-in overflow-checked arithmetic: `__builtin_mul_overflow(a, b, &res)`.
4. **Strict Aliasing Rule**:
   - Never cast unrelated pointers (e.g., casting `char*` to `int*` or struct pointers) without `union` or `memcpy`. Compilers with `-O2`/`-O3` will reorder or eliminate memory accesses if strict aliasing is violated.

---

## 4. Signal Handling & File Descriptor Invariants

- **Asynchronous Signal Safety**:
  - In signal handler functions registered via `sigaction`, invoke ONLY async-signal-safe functions listed in `signal-safety(7)` (e.g., `write`, `_exit`, `unlink`). Never call `printf`, `malloc`, `free`, or `syslog` inside a signal handler.
  - Set a `volatile sig_atomic_t g_stop = 0;` flag, or use `signalfd(2)` / the self-pipe trick to translate signals into event-loop-readable file descriptor events.
- **Close-on-Exec (`O_CLOEXEC` / `SOCK_CLOEXEC`)**:
  - Always open file descriptors with `O_CLOEXEC` or `SOCK_CLOEXEC` (e.g., `open(path, O_RDONLY | O_CLOEXEC)`, `socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0)`). This prevents file descriptor leakage into child processes executed via `fork`/`execve`.

---

## 5. Verification & Sanitizer Suite

Always compile and verify C code using strict warnings and sanitizers:
- **Compiler Flags**:
  ```bash
  gcc -std=c11 -Wall -Wextra -Wpedantic -Wshadow -Wformat=2 -Wconversion -Wnull-dereference -Werror
  ```
- **Runtime Sanitizers**:
  ```bash
  # Address and Undefined Behavior Sanitizers
  gcc -fsanitize=address,undefined -g -O1 app.c -o app
  ./app
  # Thread Sanitizer for multi-threaded code
  gcc -fsanitize=thread -g -O1 app.c -o app
  ```
- **Static Analysis**: Run `cppcheck --enable=all --suppress=missingInclude app.c` and `scan-build make`.
