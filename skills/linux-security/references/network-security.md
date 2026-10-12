# Linux Network Security: Firewalls, Segmentation, and TLS Hardening

Technical reference for network perimeter hardening, socket exposure, packet filtering (nftables), and network namespace isolation.

---

## 1. Network Attack Surface Reduction

Every listening socket exposes an entry point to the system.

### Auditing Listening Ports:
```bash
ss -tulpn
```

### Remediation Rules:
1. **Local-Only Services**: Bind strictly to `127.0.0.1` (IPv4 loopback) or `::1` (IPv6 loopback), or preferably a UNIX domain socket with restricted permissions (`0600`), rather than `0.0.0.0` or `[::]`.
2. **UNIX Socket Credentials**: Verify client identity using `SO_PEERCRED`:
   ```c
   struct ucred cr;
   socklen_t len = sizeof(struct ucred);
   getsockopt(client_fd, SOL_SOCKET, SO_PEERCRED, &cr, &len);
   if (cr.uid != 0 && cr.uid != authorized_uid) {
       close(client_fd); // Reject unauthorized local caller
   }
   ```

---

## 2. Stateful Firewall Policy with nftables

Modern Linux uses `nftables` (replacing legacy `iptables`). Enforce a default-drop stateful firewall policy:

```nft
table inet filter {
    chain input {
        type filter hook input priority filter; policy drop;

        # Accept loopback traffic
        iif "lo" accept

        # Accept established and related connections
        ct state established,related accept

        # Drop invalid packets immediately
        ct state invalid drop

        # Allow incoming SSH on port 22 with rate limiting (max 10 new connections/min)
        tcp dport 22 ct state new limit rate 10/minute accept

        # Log and drop all remaining traffic
        log prefix "[NFT DROP]: " level debug
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

## 3. Network Namespace Isolation for Untrusted Applications

Isolate untrusted processes in private network namespaces (`ip netns` or systemd `PrivateNetwork=yes`):

```bash
# Create isolated network namespace
ip netns add sandbox0

# Execute command inside namespace with only a disconnected loopback
ip netns exec sandbox0 ./untrusted_binary
```
Inside `sandbox0`, the application has no default gateway, no physical Ethernet/Wi-Fi interfaces, and cannot reach external network endpoints or local LAN resources.
