# nftables & Firewall Engineering Reference

## 1. Scope

This document details modern packet filtering, network address translation (NAT), stateful connection tracking, and rule syntax in `nftables`.

---

## 2. nftables vs. Legacy iptables

| Feature | Legacy iptables | Modern nftables |
|:---|:---|:---|
| **Tables/Families** | Fixed tables (`filter`, `nat`, `mangle`, `raw`) with hardcoded chains | Arbitrary user-defined tables and chains; unified `inet` family for dual-stack IPv4/IPv6 |
| **Command Execution** | Invokes separate commands (`iptables`, `ip6tables`, `arptables`, `ebtables`) | Unified command-line interface (`nft`) and atomic configuration reloads |
| **Performance** | Linear rule scanning ($O(N)$) | JIT-compiled bytecode and native hash sets / maps ($O(1)$) |
| **Configuration File** | Fragmented script dumps | Clean declarative grammar in `/etc/nftables.conf` |

---

## 3. Production nftables Architecture (`/etc/nftables.conf`)

```nft
#!/usr/sbin/nft -f

flush ruleset

table inet filter {
    chain input {
        type filter hook input priority filter; policy drop;

        # 1. Allow traffic on local loopback interface
        iifname "lo" accept

        # 2. Allow established and related traffic (stateful connection tracking)
        ct state established,related accept

        # 3. Drop invalid packets
        ct state invalid drop

        # 4. Allow essential ICMP / ICMPv6 (ping, PMTU discovery, neighbor discovery)
        ip protocol icmp accept
        ip6 nexthdr icmpv6 accept

        # 5. Open specific incoming services (e.g., SSH)
        tcp dport 22 accept

        # Log and drop remaining (implicit policy drop)
        log prefix "nft-input-drop: " counter drop
    }

    chain forward {
        type filter hook forward priority filter; policy drop;
    }

    chain output {
        type filter hook output priority filter; policy accept;
    }
}
```

---

## 4. Network Address Translation (NAT)

```nft
table ip nat {
    chain prerouting {
        type nat hook prerouting priority dstnat; policy accept;
        # Port forwarding (DNAT)
        tcp dport 80 dnat to 192.168.1.50:8080
    }

    chain postrouting {
        type nat hook postrouting priority srcnat; policy accept;
        # Outbound masquerading (SNAT)
        oifname "enp3s0" masquerade
    }
}
```

---

## 5. Authoritative References

- [nft(8) Manual](https://man.archlinux.org/man/nft.8)
- [nftables Wiki](https://wiki.nftables.org/)
- [ArchWiki: nftables](https://wiki.archlinux.org/title/Nftables)
