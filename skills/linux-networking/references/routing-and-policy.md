# Linux Routing & Policy Routing Reference

## 1. Scope

This document details standard and policy-based routing in the Linux kernel using `iproute2`.

---

## 2. Standard Routing with `ip route`

```bash
# 1. Display active routing table
ip route show

# 2. Add default gateway
ip route add default via 192.168.1.1 dev enp3s0

# 3. Add default route with explicit metric (lower metric = higher priority)
ip route add default via 192.168.1.1 dev enp3s0 metric 100
ip route add default via 10.0.0.1 dev wlan0 metric 600

# 4. Query the kernel's routing decision for a destination IP
ip route get 1.1.1.1
# Sample Output: 1.1.1.1 via 192.168.1.1 dev enp3s0 src 192.168.1.50 uid 1000
```

---

## 3. Policy-Based Routing (PBR) with `ip rule`

Policy routing allows routing decisions based on attributes beyond the destination IP, such as source IP address, firewall mark (`fwmark`), or incoming interface:

```bash
# 1. Define custom routing table in /etc/iproute2/rt_tables
echo "200 vpn_table" >> /etc/iproute2/rt_tables

# 2. Populate the custom routing table
ip route add default via 10.8.0.1 dev wg0 table vpn_table

# 3. Create policy rules directing specific traffic to that table
# Rule: All traffic from 192.168.1.100 must use vpn_table
ip rule add from 192.168.1.100 lookup vpn_table

# 4. View active routing policy database (RPDB)
ip rule show
```

---

## 4. Authoritative References

- [ip-route(8) Manual](https://man.archlinux.org/man/ip-route.8)
- [ip-rule(8) Manual](https://man.archlinux.org/man/ip-rule.8)
- [Linux Advanced Routing & Traffic Control (LARTC)](https://lartc.org/)
