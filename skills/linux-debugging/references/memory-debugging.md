# Memory Debugging: Corruption, Leaks, and Sanitizers

Technical reference for identifying and remediating memory defects in C, C++, and unsafe Rust on Linux.

---

## 1. Taxonomy of Memory Defects

| Defect Class | Underlying Mechanism | Primary Diagnostic Tool |
|---|---|---|
| **Use-After-Free (UAF)** | Accessing heap memory after `free()` or `delete` has returned memory to allocator. | AddressSanitizer (`-fsanitize=address`) |
| **Heap Buffer Overflow** | Reading or writing past the allocated boundaries of a heap chunk. | AddressSanitizer, Valgrind Memcheck |
| **Stack Buffer Overflow** | Writing past the bounds of a local array on the call stack, clobbering saved registers. | AddressSanitizer, GCC `-fstack-protector-strong` |
| **Double Free** | Calling `free()` twice on the exact same pointer address without an intervening allocation. | AddressSanitizer, glibc `MALLOC_CHECK_=3` |
| **Uninitialized Memory Read** | Reading memory from stack or heap before writing a defined value. | MemorySanitizer (`-fsanitize=memory`), Valgrind |
| **Memory Leak** | Losing all pointers to allocated heap blocks without freeing them. | LeakSanitizer (`-fsanitize=leak`), heaptrack |
| **Invalid Free** | Calling `free()` on a pointer to static memory, stack memory, or an interior pointer. | AddressSanitizer, glibc `free(): invalid pointer` |

---

## 2. AddressSanitizer (ASan) Usage & Diagnostics

AddressSanitizer uses compiler instrumentation and shadow memory (1 byte of shadow tracks the addressability of 8 bytes of application memory).

### Compiling with ASan:
```bash
gcc -fsanitize=address -O1 -g3 -fno-omit-frame-pointer my_app.c -o my_app
```

### Analyzing ASan Reports:
```text
=================================================================
==4210==ERROR: AddressSanitizer: heap-use-after-free on address 0x602000000010 at pc 0x555555555234 bp 0x7fffffffd470 sp 0x7fffffffd468
READ of size 4 at 0x602000000010 thread T0
    #0 0x555555555233 in process_packet /home/user/app/packet.c:42
    #1 0x555555555310 in main /home/user/app/main.c:18

0x602000000010 is located 0 bytes inside of 16-byte region [0x602000000010,0x602000000020)
freed by thread T0 here:
    #0 0x7ffff772b987 in __interceptor_free /usr/lib/libasan.so.8
    #1 0x5555555551ec in cleanup_old_packet /home/user/app/packet.c:28
    #2 0x555555555305 in main /home/user/app/main.c:16

previously allocated by thread T0 here:
    #0 0x7ffff772bd2f in __interceptor_malloc /usr/lib/libasan.so.8
    #1 0x555555555198 in allocate_packet /home/user/app/packet.c:12
    #2 0x5555555552f0 in main /home/user/app/main.c:14
=================================================================
```
*Diagnosis*: ASan provides a 3-way trace:
1. Exact crash site (Read of size 4 at `packet.c:42`).
2. Exact site where memory was freed (`packet.c:28`).
3. Exact site where memory was initially allocated (`packet.c:12`).

---

## 3. Valgrind Memcheck for Uninstrumented Binaries

When recompilation is not possible, Valgrind translates machine code into an intermediate representation and simulates CPU execution:

```bash
valgrind --tool=memcheck \
         --leak-check=full \
         --show-leak-kinds=all \
         --track-origins=yes \
         --log-file=valgrind.log \
         ./my_uninstrumented_binary
```

### Valgrind Leak Classifications:
- **definitely lost**: No pointer to the block exists anywhere in memory. True memory leak.
- **indirectly lost**: The block is pointed to by a block that is itself definitely lost.
- **possibly lost**: An interior pointer exists (may point inside an array or struct), but no pointer to the start.
- **still reachable**: A pointer to the block still exists at process exit (e.g., global configuration). Usually harmless, but can obscure leaks.

---

## 4. glibc Allocator Diagnostics

glibc's `ptmalloc` provides runtime diagnostic tunables via environment variables:

```bash
# Enable crash abort on heap corruption detection
export MALLOC_CHECK_=3

# Enable memory tagging / abort on double-free
export GLIBC_TUNABLES="glibc.malloc.check=3"
```
