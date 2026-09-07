# I2C, SPI and Platform Subsystem Driver Reference

## 1. Scope

This document details device driver development for low-speed serial buses (I2C, SMBus, SPI), Device Tree matching, ACPI matching, and the regmap abstraction.

---

## 2. I2C & SMBus Subsystem

### 2.1 I2C Driver Architecture
```c
#include <linux/i2c.h>

static int my_i2c_probe(struct i2c_client *client)
{
    struct device *dev = &client->dev;
    int data;

    // Read byte from register 0x10 over SMBus protocol
    data = i2c_smbus_read_byte_data(client, 0x10);
    if (data < 0)
        return data;

    dev_info(dev, "Read 0x%02x from I2C sensor\n", data);
    return 0;
}

static const struct of_device_id my_i2c_of_match[] = {
    { .compatible = "vendor,sensor-v1" },
    { }
};
MODULE_DEVICE_TABLE(of, my_i2c_of_match);

static struct i2c_driver my_i2c_driver = {
    .driver = {
        .name = "my_sensor",
        .of_match_table = my_i2c_of_match,
    },
    .probe = my_i2c_probe,
    .remove = my_i2c_remove,
};
module_i2c_driver(my_i2c_driver);
```

---

## 3. SPI Subsystem

### 3.1 SPI Driver Architecture
```c
#include <linux/spi/spi.h>

static int my_spi_probe(struct spi_device *spi)
{
    u8 tx_buf[2] = { 0x80, 0x00 };
    u8 rx_buf[2] = { 0 };

    // Synchronous write-then-read SPI transfer
    return spi_write_then_read(spi, tx_buf, sizeof(tx_buf), rx_buf, sizeof(rx_buf));
}

static struct spi_driver my_spi_driver = {
    .driver = {
        .name = "my_spi_dev",
    },
    .probe  = my_spi_probe,
    .remove = my_spi_remove,
};
module_spi_driver(my_spi_driver);
```

---

## 4. Hardware Matching: Device Tree (OF) vs ACPI

| Paradigm | Architecture | Matching Mechanism | Driver Table |
|:---|:---|:---|:---|
| **Device Tree (OF)** | ARM, ARM64, RISC-V, Embedded x86 | Matches `.compatible` strings in DTB with driver `.of_match_table`. | `MODULE_DEVICE_TABLE(of, ...)` |
| **ACPI** | Standard x86_64, Server ARM64 | Matches 8-character Hardware IDs (`_HID`) or Compatible IDs (`_CID`) with `.acpi_match_table`. | `MODULE_DEVICE_TABLE(acpi, ...)` |

---

## 5. Regmap Abstraction Layer

The `regmap` subsystem (`include/linux/regmap.h`) provides a unified API for register-based hardware across I2C, SPI, and Memory-Mapped I/O (MMIO), including automatic endianness conversion, caching, and locking.

---

## 6. Authoritative References

- [I2C and SMBus Subsystem](https://docs.kernel.org/i2c/index.html)
- [SPI Subsystem](https://docs.kernel.org/spi/index.html)
- [Regmap API](https://docs.kernel.org/driver-api/regmap.html)
