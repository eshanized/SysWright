# PCI/PCIe and USB Subsystem Driver Reference

## 1. Scope

This document details hardware driver architectures for PCI/PCIe and USB devices, memory-mapped I/O, device ID tables, and URB communication.

---

## 2. PCI and PCIe Driver Architecture

### 2.1 PCI Device ID Table
Every PCI driver declares supported Vendor and Device IDs:
```c
#include <linux/pci.h>

static const struct pci_device_id my_pci_ids[] = {
    { PCI_DEVICE(0x8086, 0x100e) }, /* Intel 82540EM Gigabit Ethernet */
    { 0, } /* Terminating entry */
};
MODULE_DEVICE_TABLE(pci, my_pci_ids);
```

### 2.2 PCI Driver Registration and Probe
```c
static int my_pci_probe(struct pci_dev *pdev, const struct pci_device_id *id)
{
    int ret;
    void __iomem *ioaddr;

    /* 1. Enable PCI device and bus master */
    ret = pcim_enable_device(pdev);
    if (ret)
        return ret;

    pci_set_master(pdev);

    /* 2. Request and map Base Address Register (BAR 0) */
    ret = pcim_iomap_regions(pdev, BIT(0), "my_pci_driver");
    if (ret)
        return ret;

    ioaddr = pcim_iomap_table(pdev)[0];

    /* 3. Configure 64-bit DMA mask */
    ret = dma_set_mask_and_coherent(&pdev->dev, DMA_BIT_MASK(64));
    if (ret)
        return ret;

    return 0;
}

static struct pci_driver my_pci_driver = {
    .name     = "my_pci_driver",
    .id_table = my_pci_ids,
    .probe    = my_pci_probe,
    .remove   = my_pci_remove,
};
module_pci_driver(my_pci_driver);
```

---

## 3. USB Subsystem Architecture

### 3.1 USB Communication Model
- **Endpoints**: Unidirectional communication pipes on a device. Types:
  - *Control*: Device enumeration and setup commands (Endpoint 0).
  - *Bulk*: Large, bursty data transfers without guaranteed latency (mass storage, network).
  - *Interrupt*: Small, periodic, guaranteed-latency polling (keyboards, mice).
  - *Isochronous*: Real-time streaming with potential packet loss (audio, video).
- **URB (USB Request Block)**: Asynchronous transfer request structure passed to the USB core.

### 3.2 USB Driver Skeleton
```c
#include <linux/usb.h>

static const struct usb_device_id my_usb_table[] = {
    { USB_DEVICE(0x046d, 0xc077) }, /* Logitech USB Mouse */
    { }
};
MODULE_DEVICE_TABLE(usb, my_usb_table);

static int my_usb_probe(struct usb_interface *interface, const struct usb_device_id *id)
{
    struct usb_device *udev = interface_to_usbdev(interface);
    dev_info(&interface->dev, "USB device connected: %04x:%04x\n",
             le16_to_cpu(udev->descriptor.idVendor),
             le16_to_cpu(udev->descriptor.idProduct));
    return 0;
}

static struct usb_driver my_usb_driver = {
    .name       = "my_usb_driver",
    .id_table   = my_usb_table,
    .probe      = my_usb_probe,
    .disconnect = my_usb_disconnect,
};
module_usb_driver(my_usb_driver);
```

---

## 4. Authoritative References

- [PCI Bus Subsystem Documentation](https://docs.kernel.org/PCI/index.html)
- [Writing USB Device Drivers](https://docs.kernel.org/driver-api/usb/writing_usb_driver.html)
- [USB Core API](https://docs.kernel.org/driver-api/usb/usb.html)
