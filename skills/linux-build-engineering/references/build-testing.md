# Build Testing, CTest & Continuous Integration

## 1. Scope & Automated Build Testing

Every native build system must integrate automated test discovery and execution:
- **CTest**: The standard test driver included with CMake.
- **`meson test`**: The built-in parallel test runner for Meson.
- **`cargo test`**: The built-in test runner for Rust.

---

## 2. CMake & CTest Integration

In `CMakeLists.txt`:
```cmake
include(CTest)
if(BUILD_TESTING)
    add_executable(test_math tests/test_math.cpp)
    target_link_libraries(test_math PRIVATE core_engine)

    add_test(NAME MathTest COMMAND test_math)
    set_tests_properties(MathTest PROPERTIES TIMEOUT 10)
endif()
```
Execution:
```bash
ctest --test-dir build --output-on-failure --parallel $(nproc)
```

---

## 3. Code Coverage & Static Analysis in CI

- **GCC / Clang Coverage**: Compile with `--coverage` (`-fprofile-arcs -ftest-coverage`). Execute the test suite, then generate HTML reports via `lcov` or `gcovr`.
- **Clang-Tidy**: Integrate static analysis directly into CMake:
  ```cmake
  set(CMAKE_CXX_CLANG_TIDY "clang-tidy;-checks=*,-fuchsia-*")
  ```
