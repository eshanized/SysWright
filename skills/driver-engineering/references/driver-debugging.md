# Device Driver Debugging & Diagnostics Reference

## 1. Scope

This document details diagnostic workflows, hardware identification commands, probe failure isolation, and firmware debugging.

---

## 2. Hardware Identification Tools

Before debugging a driver, collect verified hardware identifiers:

```bash
# 1. Inspect PCI devices with numeric vendor/device IDs
lspci -nn -s 00:03.0
# Sample: 00:03.0 Ethernet controller [0200]: Intel Corporation 82540EM Gigabit Ethernet Controller [8086:100e] (rev 02)

# 2. Inspect active driver and kernel modules bound to PCI device
lspci -k -s 00:03.0

# 3. Inspect USB devices with numeric vendor:product IDs
lsusb -v

# 4. Query udev device properties
udevadm info --query=all --path=/sys/class/net/eth0
```

---

## 3. Diagnosing Driver Probe Failures

### 3.1 Common Probe Failure Classes
1. **Missing Firmware**:
   - Symptom: `dmesg` contains `Direct firmware load for ... failed with error -2`.
   - Root Cause: Microcode file is missing from `/usr/lib/firmware/`.
   - Fix: Install the relevant firmware package (`linux-firmware` or vendor package).
2. **Resource Conflicts**:
   - Symptom: `probe()` returns `-EBUSY` during `request_mem_region` or `request_irq`.
   - Root Cause: Another driver or conflicting module already claimed the BAR address or interrupt line.
3. **Deferred Probing**:
   - Symptom: Driver probe returns `-EPROBE_DEFER`.
   - Diagnosis: Inspect `/sys/kernel/debug/devices_deferred` to see which prerequisite dependency (clock, regulator, GPIO) is pending.

---

## 4. Authoritative References

- [Linux Driver Debugging](https://docs.kernel.org/driver-api/driver-model/driver.html)
- [udevadm(8) Manual](https://man.archlinux.org/man/udevadm.8)
