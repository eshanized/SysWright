# Software Bill of Materials (SBOM) Engineering

A Software Bill of Materials (SBOM) is an authoritative, machine-readable inventory of software components, dependencies, and metadata included within a software build.

---

## 1. SBOM Standards: SPDX vs CycloneDX

| Specification | Primary Standards Body | Primary Focus | Standard Formats |
|---|---|---|---|
| **SPDX (ISO/IEC 5962:2021)** | Linux Foundation | Licensing compliance, IP provenance, package relationships | JSON, YAML, tag-value |
| **CycloneDX** | OWASP | Cybersecurity, vulnerability management, component exploitability (VEX) | JSON, XML |

Both formats are widely supported by enterprise security scanners and distribution tooling. Modern Linux engineering targets **SPDX 2.3 / 3.0 (JSON)** and **CycloneDX 1.5 (JSON)**.

---

## 2. Core Elements of a Production SBOM

An SBOM is legally and technically ineffective unless it includes:
1. **Document Identity**: Unique namespace URI, creation timestamp, and creator entity.
2. **Component Identifiers**:
   - Component Name and Version.
   - Package URL (`purl` format: `pkg:deb/debian/curl@7.88.1-10+deb12u5?arch=amd64`).
   - Common Platform Enumeration (CPE).
3. **Cryptographic Hashes**: SHA-256 and SHA-512 hashes of source and binary artifacts.
4. **Declared & Concluded Licenses**: Valid SPDX license expressions (e.g., `GPL-2.0-or-later WITH Linux-syscall-note`).
5. **Relationship Graph**: Explicit dependency tree (`DEPENDS_ON`, `CONTAINS`, `DYNAMIC_LINK`).

---

## 3. SBOM Generation Tooling

### Generating SBOMs for Container Images and Filesystems:
Using `syft`:
```bash
# Generate SPDX JSON for a directory or binary
syft dir:./build/out -o spdx-json=build/sbom-spdx.json

# Generate CycloneDX JSON for an installed rootfs
syft rootfs:/srv/rootfs -o cyclonedx-json=build/sbom-cyclonedx.json
```

### Validating SBOM Integrity:
Ensure generated SBOMs adhere strictly to official schemas:
```bash
# Validate SPDX document structure
spdx-tools-cli validate -i build/sbom-spdx.json
```