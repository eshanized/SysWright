# Network Namespaces & Virtual Networking Reference

## 1. Scope

This document details network namespaces (`ip netns`), virtual ethernet (`veth`) pairs, Linux software bridges, and isolated testbed construction.

---

## 2. Isolated Network Namespaces (`ip netns`)

Network namespaces provide isolated instances of the network stack, each with its own interfaces, routing tables, and firewall rules:

```bash
# 1. Create two isolated network namespaces
ip netns add blue
ip netns add red

# 2. Create a virtual ethernet (veth) cable pair
ip link add veth-blue type veth peer name veth-red

# 3. Move endpoints into their respective namespaces
ip link set veth-blue netns blue
ip link set veth-red netns red

# 4. Configure IP addresses inside namespaces
ip -n blue addr add 10.0.0.1/24 dev veth-blue
ip -n blue link set veth-blue up
ip -n blue link set lo up

ip -n red addr add 10.0.0.2/24 dev veth-red
ip -n red link set veth-red up
ip -n red link set lo up

# 5. Test isolated connectivity without mutating host network
ip netns exec blue ping -c 3 10.0.0.2
```

---

## 3. Linux Software Bridges

Software bridges (`br0`) operate at Layer 2, switching Ethernet frames across physical and virtual interfaces:
```bash
# Create bridge and attach interface
ip link add name br0 type bridge
ip link set dev br0 up
ip link set dev enp3s0 master br0
```

---

## 4. Authoritative References

- [ip-netns(8) Manual](https://man.archlinux.org/man/ip-netns.8)
- [ip-link(8) Manual](https://man.archlinux.org/man/ip-link.8)
- [Bridge Network Configuration](https://wiki.archlinux.org/title/Network_bridge)
