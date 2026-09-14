# Linux Network Configuration & Managers Reference

## 1. Scope

This document details network managers (`iproute2`, `systemd-networkd`, `NetworkManager`), the non-concurrency invariant, and DNS management via `systemd-resolved`.

---

## 2. The Non-Concurrency Invariant

- **Critical Architectural Rule**: Never configure or run multiple network managers concurrently managing the same network interface.
- Running `NetworkManager` and `systemd-networkd` simultaneously leads to:
  1. Race conditions during DHCP lease acquisition.
  2. Conflicting default gateway metric updates.
  3. Route flapping and dropped active connections.
  4. Conflicting DNS server entries in `/etc/resolv.conf`.
- **Remediation**: Standardize on one manager for the system:
  - Desktop environments / roaming laptops: Prefer `NetworkManager` + `iwd`.
  - Servers / containers / headless VMs: Prefer `systemd-networkd` + `systemd-resolved`.

---

## 3. Manager Implementations

### 3.1 `systemd-networkd` Configuration
Stored in `/etc/systemd/network/`:
```ini
# /etc/systemd/network/20-wired.network
[Match]
Name=enp*

[Network]
DHCP=yes
IPv6PrivacyExtensions=yes

[DHCPv4]
RouteMetric=100
```

### 3.2 DNS Resolution: `systemd-resolved`
- Manages local DNS stub listener on `127.0.0.53:53`.
- `/etc/resolv.conf` must be a symlink to `/run/systemd/resolve/stub-resolv.conf`:
  ```bash
  ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
  ```
- Querying and troubleshooting DNS:
  ```bash
  # Check active upstream DNS servers per link
  resolvectl status

  # Test DNS lookup
  resolvectl query archlinux.org
  ```

---

## 4. Wi-Fi Management: `iwd` vs `wpa_supplicant`

- **`iwd` (Intel Wireless Daemon)**: Modern, written exclusively using Linux Netlink and crypto APIs; significantly faster connection establishment and roaming.
- **`wpa_supplicant`**: Legacy standard cross-platform daemon.

---

## 5. Authoritative References

- [systemd-networkd(8) Manual](https://man.archlinux.org/man/systemd-networkd.8)
- [systemd.network(5) Manual](https://man.archlinux.org/man/systemd.network.5)
- [systemd-resolved(8) Manual](https://man.archlinux.org/man/systemd-resolved.8)
- [ArchWiki: Network configuration](https://wiki.archlinux.org/title/Network_configuration)
