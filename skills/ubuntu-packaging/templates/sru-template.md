# Stable Release Update (SRU) Justification Document

**Bug Reference:** LP: #0000000  
**Package:** example-package  
**Target Series:** noble (24.04 LTS)  

---

## [Impact]

*Describe the problem encountered by users. Explain the symptom, affected hardware/configurations, and why this justifies an SRU in a production release.*

Example: Due to an unhandled socket timeout in `daemon.c`, `example-daemon` terminates with SIGSEGV when remote connections are abruptly severed, causing unexpected service outage for production servers.

---

## [Test Plan]

*Provide a step-by-step procedure that can be executed by anyone to reproduce the defect and verify the resolution.*

1. Install `example-package` on a clean Ubuntu 24.04 (noble) system.
2. Start the daemon: `systemctl start example-daemon`.
3. Simulate abrupt disconnect: `nc -w 1 localhost 8080 < /dev/null`.
4. **Verification on unpatched version:** Daemon crashes; `journalctl -u example-daemon` shows SIGSEGV.
5. Enable `noble-proposed` and install updated package `example-package 1.0.0-1ubuntu1.1`.
6. Repeat step 3.
7. **Verification on proposed version:** Daemon logs clean connection reset and continues serving traffic normally without crashing.

---

## [Where problems could occur]

*Realistic assessment of regression potential and blast radius.*

The patch introduces a boundary check on the socket read buffer in `src/network.c`. If the logic contains a regression, it could cause valid long-lived connections to drop prematurely. To mitigate this risk, existing automated network integration tests have been executed with 10,000 synthetic requests with zero errors.
