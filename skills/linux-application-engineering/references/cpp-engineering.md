# Modern C++ Engineering for Linux Systems

## 1. Scope & Standard Selection

Modern C++ (C++17, C++20, and C++23) combines zero-cost abstraction with expressiveness, making it the choice for high-performance computing, complex domain engines, Qt desktop applications, and low-latency infrastructure.

### Language Standard Selection:
- **C++17**: Universal baseline for Linux systems software; supported by GCC 7+ and Clang 5+. Features: `std::string_view`, `std::optional`, `std::variant`, `std::filesystem`, structured bindings.
- **C++20**: Recommended standard for new development; supported by GCC 11+ and Clang 13+. Features: Concepts, Ranges, Coroutines, `std::span`, `<format>`, `std::jthread`.
- **C++23**: Use only when targeting modern toolchains (GCC 14+, Clang 18+) where `std::expected` and `std::print` are available.

---

## 2. Resource Management: Zero-Tolerance for Raw Pointers

Resource Acquisition Is Initialization (RAII) is the fundamental invariant of modern C++:

### 2.1 Smart Pointers & Ownership Semantics
- **`std::unique_ptr<T>`**: Default pointer type for single, exclusive ownership. Zero runtime overhead compared to a raw pointer. Use `std::make_unique<T>()`.
- **`std::shared_ptr<T>`**: Shared ownership managed via atomic reference counting. Use ONLY when multiple independent subsystems hold non-hierarchical lifetimes.
- **`std::weak_ptr<T>`**: Non-owning observer used to break circular reference cycles between `std::shared_ptr` instances.
- **Raw Pointers (`T*`) and References (`T&`)**: Used exclusively for non-owning parameter passing where lifetime is guaranteed by the caller. Never call `delete` on a raw pointer.

```cpp
// Correct: Exclusive ownership with deterministic RAII destruction
class SocketConnection {
public:
    explicit SocketConnection(int fd) : fd_(fd) {}
    ~SocketConnection() {
        if (fd_ >= 0) ::close(fd_);
    }
    // Disable copy semantics
    SocketConnection(const SocketConnection&) = delete;
    SocketConnection& operator=(const SocketConnection&) = delete;
    // Enable move semantics
    SocketConnection(SocketConnection&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    SocketConnection& operator=(SocketConnection&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }
private:
    int fd_{-1};
};
```

---

## 3. Modern Concurrency & Thread Management

### 3.1 `std::jthread` (C++20)
Prefer `std::jthread` over legacy `std::thread`. `std::jthread` automatically requests cancellation via `std::stop_token` and joins upon destruction, eliminating accidental `std::terminate()` calls caused by unjoined threads:
```cpp
void backgroundWorker(std::stop_token stopToken) {
    while (!stopToken.stop_requested()) {
        // Perform work step
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
}

void runService() {
    std::jthread worker(backgroundWorker);
    // Worker automatically requested to stop and joined when worker goes out of scope
}
```

### 3.2 Thread-Safe Synchronization
- Use `std::mutex` with `std::scoped_lock` (C++17) or `std::unique_lock`. `std::scoped_lock` acquires multiple mutexes simultaneously without deadlock (using a deadlock-avoidance algorithm).
- Prefer `std::shared_mutex` with `std::shared_lock` for read-heavy, write-infrequent data structures.
- For simple counters and state flags, use lock-free atomics: `std::atomic<bool>`, `std::atomic<uint64_t>`.

---

## 4. Value Semantics, Views & Efficient Passing

1. **Non-Owning Views**:
   - Use `std::string_view` for read-only string parameters. Avoids temporary `std::string` heap allocations.
   - Use `std::span<const T>` (C++20) for contiguous sequences (arrays, `std::vector`) instead of pointer + length.
2. **Parameter Passing Rules**:
   - Small, cheaply copyable types ($\le 16$ bytes: `int`, `double`, `std::string_view`): Pass by value.
   - Large or non-trivial objects: Pass by `const T&` for read-only access.
   - Sinks (functions that take ownership): Pass by value and `std::move` into destination.
3. **Error Handling without Exceptions**:
   - For performance-critical code or embedded targets, prefer `std::expected<T, E>` (C++23) or `std::optional<T>` over throwing exceptions.

---

## 5. ABI Compatibility & Shared Libraries

- When authoring shared libraries (`.so`), hide internal symbols by default:
  ```cmake
  set(CMAKE_CXX_VISIBILITY_PRESET hidden)
  set(CMAKE_VISIBILITY_INLINES_HIDDEN ON)
  ```
- Explicitly export public APIs using macro annotations:
  ```cpp
  #define APP_EXPORT __attribute__((visibility("default")))
  ```
- Use the **Pimpl Idiom** (Pointer to Implementation) for stable ABI boundaries in public C++ shared libraries, ensuring private class members can change without breaking caller binary compatibility.
