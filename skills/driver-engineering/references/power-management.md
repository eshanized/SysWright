# Linux Driver Power Management Reference

## 1. Scope

This document details driver power management interfaces: Runtime PM, system sleep/resume transitions, and device power states.

---

## 2. Runtime Power Management (Runtime PM)

Runtime PM allows idle devices to enter low-power states individually without suspending the overall operating system:

```c
#include <linux/pm_runtime.h>

static int my_probe(struct platform_device *pdev)
{
    struct device *dev = &pdev->dev;

    pm_runtime_set_autosuspend_delay(dev, 2000); /* 2 seconds */
    pm_runtime_use_autosuspend(dev);
    pm_runtime_enable(dev);

    return 0;
}

// When executing an operation requiring the hardware:
pm_runtime_get_sync(dev);
hardware_transfer();
pm_runtime_mark_last_busy(dev);
pm_runtime_put_autosuspend(dev);
```

---

## 3. System Sleep: Suspend and Resume (`dev_pm_ops`)

When the system enters sleep (Suspend-to-RAM, S3, or s2idle):
```c
static int my_suspend(struct device *dev)
{
    // Save device register state, disable IRQs, power down clocks
    return 0;
}

static int my_resume(struct device *dev)
{
    // Power up clocks, restore register state, re-enable IRQs
    return 0;
}

static const struct dev_pm_ops my_pm_ops = {
    SYSTEM_SLEEP_PM_OPS(my_suspend, my_resume)
    RUNTIME_PM_OPS(my_runtime_suspend, my_runtime_resume, NULL)
};
```

---

## 4. Authoritative References

- [Device Power Management Basics](https://docs.kernel.org/driver-api/pm/devices.html)
- [Runtime Power Management Framework for Device Drivers](https://docs.kernel.org/power/runtime_pm.html)
