# Modern Target-Based CMake Architecture

## 1. Scope & The Modern CMake Paradigm

Modern CMake (CMake 3.20+) is an object-oriented modeling system for software targets, not a scripting language for global compiler flags.
> **CORE INVARIANT**: Code should manipulate **targets** and **target properties**, never global variables or directory-level states.

---

## 2. Target Visibility & Usage Requirements

When defining a library target, usage requirements dictate what downstream consumers inherit:
- **`PRIVATE`**: Needed to build this target, but NOT needed by consumers linking against it.
- **`INTERFACE`**: NOT needed to build this target (e.g. header-only library), but REQUIRED by consumers.
- **`PUBLIC`**: Needed by this target AND required by consumers.

```cmake
cmake_minimum_required(VERSION 3.20)
project(CoreEngine VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 1. Define shared library target
add_library(core_engine SHARED
    src/Engine.cpp
    src/InternalMath.cpp
)

# 2. Scoped include directories
target_include_directories(core_engine
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        src
)

# 3. Scoped dependencies
find_package(OpenSSL REQUIRED)
target_link_libraries(core_engine
    PUBLIC
        OpenSSL::Crypto # Consumers will also need Crypto symbols
    PRIVATE
        m               # libm is an internal implementation detail
)

# 4. Target properties
set_target_properties(core_engine PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION 1
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN ON
)
```

---

## 3. Forbidden Legacy Anti-Patterns

| Legacy Anti-Pattern (DO NOT USE) | Modern Target-Based Replacement |
|---|---|
| `include_directories(/path)` | `target_include_directories(target PRIVATE /path)` |
| `link_libraries(libfoo)` | `target_link_libraries(target PRIVATE libfoo)` |
| `add_definitions(-DMY_FLAG)` | `target_compile_definitions(target PRIVATE MY_FLAG)` |
| `set(CMAKE_CXX_FLAGS "-Wall")` | `target_compile_options(target PRIVATE -Wall -Wextra)` |
| Sourcing custom `FindFoo.cmake` modules | Use upstream `Config.cmake` packages or `pkg_check_modules` |

---

## 4. Generating Exported Config Packages

To make a library discoverable via `find_package(MyLib)`:
```cmake
install(TARGETS core_engine
    EXPORT CoreEngineTargets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    INCLUDES DESTINATION include
)

install(EXPORT CoreEngineTargets
    FILE CoreEngineTargets.cmake
    NAMESPACE CoreEngine::
    DESTINATION lib/cmake/CoreEngine
)
```
