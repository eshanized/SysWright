# Linux Kernel Regressions: Linus's Law, QEMU Testing, and Bisecting

Technical reference for investigating and bisecting Linux kernel regressions.

---

## 1. The Cardinal Rule of Linux Kernel Development

> **"WE DO NOT BREAK USERSPACE!"** — Linus Torvalds

In the Linux kernel, any change that causes an existing user-space program to crash, behave incorrectly, or fail is considered a kernel bug and a regression, even if the user-space program was technically buggy or violating a specification.

If a kernel commit breaks user space:
- The change will be reverted or fixed immediately upstream.
- "Fixing user space instead" is not an acceptable response from kernel maintainers.

---

## 2. Kernel Bisecting Workflow with QEMU

Bisecting the Linux kernel requires compiling hundreds of commits. Never install these intermediate kernels onto the host machine bootloader. Compile minimal kernel images and boot them in QEMU:

```bash
#!/usr/bin/env bash
# kernel_bisect_test.sh
set -uo pipefail

# 1. Build minimal bzImage
if ! make -j"$(nproc)" bzImage >/dev/null 2>&1; then
    exit 125 # Compilation failure -> skip
fi

# 2. Boot kernel in QEMU with serial console
# QEMU runs minimal initramfs containing test script
timeout 60s qemu-system-x86_64 \
    -kernel arch/x86/boot/bzImage \
    -initrd /tmp/test_initrd.cpio.gz \
    -nographic \
    -append "console=ttyS0 panic=-1 quiet" > /tmp/qemu_output.log 2>&1

# 3. Check serial log for test outcome
if grep -q "REGRESSION_TEST_SUCCESS" /tmp/qemu_output.log; then
    exit 0 # Good
else
    exit 1 # Bad
fi
```

---

## 3. Reporting Kernel Regressions Upstream

When reporting a confirmed kernel regression upstream:
1. Provide the exact output of `git bisect log`.
2. State the first bad commit SHA and subject line.
3. CC the author of the commit and the relevant subsystem maintainer (obtained via `scripts/get_maintainer.pl -f <file>`).
4. Include minimal QEMU reproducer commands or C reproducer code.
