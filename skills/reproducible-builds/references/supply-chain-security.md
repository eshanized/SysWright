# Software Supply-Chain Security & Transparency Logs

Modern Linux supply-chain security bridges source repository controls, independent build attestations, and public append-only transparency ledgers.

---

## 1. Attack Vectors in the Packaging Lifecycle

```text
[ Developer Account Compromised ]
         │ (1. Malicious Source Commit / Backdoor)
         ▼
[ Source Repository (Git) ]
         │ (2. Dependency Confusion / Typo-squatting)
         ▼
[ Build Infrastructure (CI/CD) ]
         │ (3. Compromised Runner / Malicious Compiler)
         ▼
[ Package Repository / Mirror ]
         │ (4. Rogue Binary Swap / Metadata Downgrade)
         ▼
[ Target Host (apt / dnf / pacman) ]
```

---

## 2. Binary Transparency with Sigstore and Rekor

To prevent covert package alterations, binary signatures and SLSA attestations are submitted to public append-only Merkle tree logs (such as Sigstore's Rekor).

### Key Features:
- **Append-Only Merkle Tree**: Anyone can cryptographically verify that an entry was added and cannot be removed or altered retroactively.
- **Keyless Signing**: Identity is tied to OpenID Connect (OIDC) tokens (e.g., GitHub Actions identity) with short-lived certificates issued by Fulcio.

### Querying Rekor for Artifact Attestation:
```bash
# Search Rekor log for an artifact SHA256
rekor-cli search --sha 3a7bd3e2360a3d29eea436fcfb7e44c735d117c42d1c1835420b6b9942dd4f1b

# Verify signature using Cosign
cosign verify-blob \
  --certificate-identity https://github.com/example/myapp/.github/workflows/release.yml@refs/tags/v1.2.3 \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  --signature myapp.sig \
  myapp-1.2.3.tar.gz
```

---

## 3. Detecting Upstream Tarball Discrepancies

Maintainers must never assume an upstream release tarball (`myapp-1.2.3.tar.gz`) corresponds exactly to the upstream Git tag `v1.2.3`. Discrepancies indicate either intentional build artifacts (e.g., pre-generated autotools scripts) or covert malicious injection.

### Audit Workflow:
1. Clone upstream repository at tag:
   ```bash
   git clone --depth 1 --branch v1.2.3 https://example.org/myapp.git git-checkout
   ```
2. Unpack upstream distributed tarball:
   ```bash
   tar -xzf myapp-1.2.3.tar.gz -C tarball-checkout/
   ```
3. Run recursive diff excluding expected autotools/build system files:
   ```bash
   diff -urN \
     -x "configure" -x "Makefile.in" -x "aclocal.m4" -x ".git" \
     git-checkout/ tarball-checkout/
   ```
4. Scrutinize every unexpected delta (especially binary blobs, obfuscated M4 test scripts, or modified build targets).