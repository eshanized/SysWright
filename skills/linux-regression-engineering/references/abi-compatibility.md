# Shared Library ABI Compatibility & Automated Verification with libabigail

Comprehensive technical reference for ELF shared library Application Binary Interface (ABI) stability, SONAME rules, and libabigail (`abidiff`).

---

## 1. What Constitutes an ABI Break?

In C and C++ shared libraries, changes can preserve API source compatibility (recompiling the client code succeeds) while breaking runtime ABI compatibility (running an existing compiled client binary fails or corrupts memory).

### Common ABI-Breaking Changes in C/C++:
1. **Removing or renaming an exported function**.
2. **Changing function parameter types, return types, or calling convention**.
3. **Reordering, removing, or adding member fields in an exposed struct** (shifts struct member byte offsets).
4. **Adding or reordering virtual functions in a C++ class** (shifts vtable offsets, causing client code to dispatch to the wrong method).
5. **Increasing struct size when client code allocates the struct on the stack**.
6. **Changing enum underlying representation or values**.

---

## 2. When to Increment SONAME / SOVERSION

Shared libraries use `libfoo.so.X.Y.Z` where `X` is the SONAME/SOVERSION:

- **Backward Compatible Change** (e.g., adding a brand new function without touching existing structs):
  - Retain `SOVERSION` (e.g., `libfoo.so.1`).
  - Existing compiled binaries continue loading without recompilation.
- **Breaking ABI Change** (e.g., modifying struct layout or adding a virtual function):
  - **MANDATORY**: Increment `SOVERSION` to `libfoo.so.2`.
  - Failure to bump `SOVERSION` results in silent memory corruption or crashes in all pre-existing client applications on the host.

---

## 3. Automated ABI Verification with `abidiff` (libabigail)

`abidiff` compares the DWARF debug information and ELF symbols of two shared library builds to detect ABI breakages automatically:

```bash
# Compare v1 shared library against v2 candidate
abidiff --drop-private-types \
        --suppressions abi_suppressions.ini \
        libfoo-1.0.so libfoo-2.0.so
```

### Interpreting abidiff Output:
```text
Functions changes summary: 0 Removed, 1 Changed, 0 Added function
Variables changes summary: 0 Removed, 0 Changed, 0 Added variable

1 function with some indirect sub-type change:

  [C]'function void process_record(Record*)' at record.c:28:1 has some indirect sub-type changes:
    parameter 1 of type 'Record*' has sub-type changes:
      in pointed to type 'struct Record' at record.h:12:1:
        type size changed from 64 to 96 (in bits)
        1 data member insertion:
          'int flags', at offset 64 (in bits) at record.h:15:1
```
*`abidiff` precisely caught that adding `int flags` shifted struct size from 64 bits to 96 bits. If existing client code allocates `struct Record` on the stack, passing it to `process_record` causes a buffer overflow!*
