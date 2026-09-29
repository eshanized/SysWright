# Linking, SONAME & C/C++ ABI Stability

## 1. Scope & Dynamic Linking on Linux

Dynamic linking on Linux is managed by the GNU C library dynamic linker (`ld.so` / `ld-linux.so`). Shared libraries (`.so`) must be versioned to prevent application crashes when libraries are upgraded.

---

## 2. SONAME & Library Versioning

A shared library has three names:
1. **Real Name** (`libfoo.so.1.2.0`): The actual binary containing code.
2. **SONAME** (`libfoo.so.1`): The interface contract name embedded inside the binary (`DT_SONAME` ELF header). Applications linking against `libfoo` record this SONAME in their `DT_NEEDED` headers.
3. **Linker Name** (`libfoo.so`): A symlink pointing to the SONAME, used exclusively by the compiler linker during `gcc -lfoo`.

### Invariant:
When an ABI-breaking change occurs (removing a function, changing a struct layout, modifying C++ virtual table order), the **SONAME major version must increment** (`libfoo.so.1` $\to$ `libfoo.so.2`). Failure to increment SONAME causes segmentation faults in applications compiled against the older ABI.

---

## 3. RPATH, RUNPATH & `$ORIGIN`

- **RPATH / RUNPATH**: An ELF header (`DT_RUNPATH`) specifying additional directories where the dynamic linker should search for shared libraries before checking system paths (`/usr/lib`).
- **System Libraries Invariant**: Shared libraries installed to `/usr/lib` must **never** contain hardcoded build-host RPATHs (e.g. `/home/user/build/lib`).
- **Application Bundles (`$ORIGIN`)**: For self-contained application bundles or private helper libraries:
  ```cmake
  # Resolves libraries relative to the executable's directory at runtime!
  set_target_properties(myapp PROPERTIES
      INSTALL_RPATH "$ORIGIN/../lib"
  )
  ```
