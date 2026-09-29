# Dependency Discovery & Pkg-Config Integration

## 1. Scope & The Dependency Ecosystem

On Linux, applications link against system libraries distributed across `/usr/lib` and `/usr/include`. Build systems must discover compiler flags (`-I/usr/include/foo`) and linker flags (`-lfoo`) deterministically.

---

## 2. `pkg-config` / `pkgconf` Standard

`pkg-config` (and modern `pkgconf`) is the universal standard on Linux:
- Libraries install `.pc` metadata files to `/usr/lib/pkgconfig/` or `/usr/share/pkgconfig/`.
- The `.pc` file declares include directories, library names, private dependencies, and version numbers.

### 2.1 Using `pkg-config` in CMake
```cmake
find_package(PkgConfig REQUIRED)

# Queries libxml-2.0.pc and imports PkgConfig::LIBXML
pkg_check_modules(LIBXML REQUIRED IMPORTED_TARGET libxml-2.0>=2.9.0)

target_link_libraries(myapp PRIVATE PkgConfig::LIBXML)
```

### 2.2 Using `pkg-config` in Meson
```meson
libxml_dep = dependency('libxml-2.0', version : '>= 2.9.0')
executable('myapp', 'main.c', dependencies : [libxml_dep])
```

---

## 3. CMake Config Packages (`find_package`)

CMake packages provide native `*Config.cmake` or `<name>-config.cmake` files installed in `/usr/lib/cmake/<name>/`:
- Preferred over `pkg-config` for C++ libraries (e.g. `Qt6`, `Boost`, `OpenCV`).
- Directly provides imported targets with transitive dependencies (e.g. `Qt6::Core`).
