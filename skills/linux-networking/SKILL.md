---
name: linux-networking
description: Linux networking engineering skill for kernel network stacks, iproute2, network managers (systemd-networkd, NetworkManager), routing tables, policy routing, nftables firewalling, and network namespaces. Covers interface states, non-concurrency invariants between network managers, DNS resolution via systemd-resolved, veth pair sandboxes, and structured 7-stage OSI-aligned network troubleshooting. Use when diagnosing network connectivity, configuring firewalls, setting up network namespaces, or debugging DNS vs routing failures.
license: Apache-2.0
compatibility: Requires Linux environment with iproute2, nftables, and systemd network tools.
metadata:
  author: Linux Engineering Contributors
  version: "0.1.0"
  claude_context: "fork"
  claude_agent: "general"
---

# Linux Networking Engineering

The `linux-networking` skill provides specialist capabilities for analyzing, configuring, and troubleshooting the Linux networking stack, `iproute2` interfaces, policy routing, `nftables` firewalls, network managers, and isolated network namespaces.

---

## 1. Operating Principles & Invariants

1. **Manager Non-Concurrency Invariant**: Never run `NetworkManager` and `systemd-networkd` concurrently on the same interface. Dual managers produce race conditions, route flapping, and conflicting DHCP leases.
2. **Layered Diagnostic Discipline**: Follow the 7-stage OSI diagnostic sequence (Carrier $\to$ IP $\to$ Route $\to$ DNS $\to$ Firewall $\to$ Socket $\to$ Path). Never blame DNS without verifying IP routing first.
3. **Never Expose Secrets in Reports**: Redact Wi-Fi pre-shared keys, WireGuard private keys, and authentication credentials from diagnostic command outputs.
4. **Safety Tier Gating**: Modifying host IP addresses, altering routing tables, flushing firewall rules (`nft flush ruleset`), and toggling network interfaces are Tier 3 operations requiring explicit human authorization. Use isolated network namespaces for safe testing.

---

## 2. Intent Classification & Workflow Routing

```mermaid
flowchart TD
    REQ["Networking Request"] --> CLASS{"Classify Network Task"}

    CLASS -->|Connectivity / DNS Failure| DIAG["1. Network Diagnostics\n(Carrier check, ip route, resolvectl, ss -tulpn)"]
    CLASS -->|Routing & Gateways| ROUTE["2. Routing Engineering\n(ip route, ip rule, policy routing tables, metric)"]
    CLASS -->|Firewall & Packet Filter| FW["3. Firewall Engineering\n(nftables, tables, chains, NAT, drop policies)"]
    CLASS -->|Manager Configuration| MGR["4. Manager Configuration\n(systemd-networkd, NetworkManager, resolved, iwd)"]
    CLASS -->|Virtual / Sandbox Net| NS["5. Namespaces & Virtual Net\n(ip netns, veth pairs, bridge, wireguard tunnels)"]

    DIAG --> EXEC["Execute Networking Workflow"]
    ROUTE --> EXEC
    FW --> EXEC
    MGR --> EXEC
    NS --> EXEC
```

---

## 3. The 7-Stage Diagnostic Workflow

1. **Layer 1 (Carrier)**: Verify physical/virtual link carrier status with `ip link show` and `ethtool`.
2. **Layer 2 (Neighbor)**: Check ARP/NDP resolution with `ip neigh show`.
3. **Layer 3 (Addressing)**: Check IP assignment and subnet mask with `ip -br addr show`.
4. **Layer 3 (Routing)**: Verify default gateway and route selection with `ip route get <destination>`.
5. **Layer 4 (Sockets)**: Inspect listening ports and socket state with `ss -tulpn`.
6. **Layer 4 (Firewall)**: Check `nft list ruleset` for drop policies or missing accept rules.
7. **Layer 7 (Name Resolution)**: Query DNS reachability with `resolvectl status` and `resolvectl query`.

---

## 4. Cross-Specialist Coordination

| Task | Coordinating Specialists | Interaction |
|:---|:---|:---|
| Network-activated service | `linux-networking` + `systemd-engineering` | `linux-networking` configures interface; `systemd-engineering` wires `Type=notify` / sockets. |
| NIC driver failure | `linux-networking` + `driver-engineering` | `linux-networking` checks carrier/ethtool; `driver-engineering` diagnoses PCI/DMA faults. |

---

## 5. Authoritative References Directory

- [Networking Architecture & Stack](references/networking-architecture.md)
- [Network Configuration & Managers](references/network-configuration.md)
- [Routing & Policy-Based Routing](references/routing-and-policy.md)
- [nftables & Firewall Engineering](references/nftables.md)
- [Network Namespaces & Virtual Networking](references/namespaces-and-virtualization.md)
- [Network Diagnostics & Troubleshooting](references/troubleshooting.md)
- [Safety Policy](../../references/safety-policy.md)
