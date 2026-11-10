# Reproducibility Testing with Reprotest & Diffoscope

Automated perturbation testing and deep binary diffing are the primary diagnostic tools used to verify reproducibility and identify the exact causes of non-deterministic builds.

---

## 1. Automated Perturbation Testing with `reprotest`

`reprotest` builds software twice: first in a control environment, and second under artificially modified conditions (different time, umask, path, timezone, and hostname). It then compares the resulting binaries.

### Basic Invocations:
```bash
# Test a standard autotools/cmake build in workspace
reprotest --verbosity=2 "make -j$(nproc)" build/myapp

# Test with specific variations enabled
reprotest --variations=environment,build_path,fileordering,time,timezone,umask \
  "cmake --build . --target myapp" bin/myapp
```

### Common Perturbations Tested:
- `build_path`: Builds in `/tmp/reprotest-1/` vs `/tmp/reprotest-2/` (checks `-ffile-prefix-map`).
- `time`: Shifts clock forward by days or years (checks `SOURCE_DATE_EPOCH`).
- `timezone`: Runs with `TZ=UTC` vs `TZ=GMT+14`.
- `umask`: Compiles under `umask 0022` vs `umask 0002`.
- `fileordering`: Uses `disorderfs` to intentionally scramble filesystem directory listings.

---

## 2. Deep Binary Diffing with `diffoscope`

When two builds produce different hashes, standard `diff` or `sha256sum` only reports that they differ. `diffoscope` recursively unpacks archives (tar, zip, deb, rpm, cpio), parses ELF binaries, decodes DWARF debug symbols, and disassembles code sections to locate the exact variance.

### Running Diffoscope:
```bash
# Compare two binary packages or executables
diffoscope --html report.html build1/myapp.deb build2/myapp.deb

# Generate terminal diff with limited output
diffoscope --max-report-size 50000000 build1/myapp build2/myapp
```

---

## 3. Interpreting Diffoscope Diagnostic Output

### Case A: Timestamp in Archive Header
```text
├── ./usr/bin/myapp
│   ├── stat
│   │ │ -rwxr-xr-x   0        0     15240 2026-04-01 12:00:00.000000 myapp
│   │ │ -rwxr-xr-x   0        0     15240 2027-08-14 05:23:11.000000 myapp
```
*Diagnosis*: Archive packaging did not clamp file modification times. Export `SOURCE_DATE_EPOCH` and pass `--mtime` to tar.

### Case B: File Order Inversion
```text
├── zipinfo -v {}
│   ├── Central directory entry #1:
│   │ │ - myapp/assets/icon.png
│   │ │ + myapp/assets/config.json
```
*Diagnosis*: Build script traversed filesystem without sorting. Pipe filenames through `sort`.

### Case C: Embedded Absolute Path in Debug Symbol
```text
├── objdump -g {}
│   ├── .debug_info
│   │ │ <12> DW_AT_name: /home/runner/work/app/src/main.c
│   │ │ <12> DW_AT_name: /builds/worker-2/app/src/main.c
```
*Diagnosis*: Missing `-ffile-prefix-map=${PWD}=.` in compiler flags.