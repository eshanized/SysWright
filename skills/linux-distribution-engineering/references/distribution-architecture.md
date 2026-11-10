# Distribution Architecture & Repository Topologies

A Linux distribution repository infrastructure distributes software packages, dependency metadata, and cryptographic proofs across heterogeneous networks and geographically distributed client fleets.

---

## 1. Repository Topology Models

### Single-Tier vs Multi-Tier Repositories
- **Single-Tier (Direct Origin)**:
  - Single origin server handles metadata generation, package storage, and client HTTP requests.
  - *Use Case*: Small internal company repository or development staging (<50 clients).
  - *Risk*: Single point of failure; bandwidth saturation; no blast radius containment.
- **Two-Tier (Origin + CDN / Mirror Fleet)**:
  - Central origin server generates and signs metadata.
  - Edge mirrors or Content Delivery Networks (CDNs) cache static package artifacts (`.deb`, `.rpm`, `.pkg.tar.zst`) and short-TTL metadata files (`InRelease`, `repomd.xml`).
  - *Standard for*: Arch Linux mirrors, Ubuntu archive mirrors, Fedora mirror manager.

---

## 2. Environment Segmentation: Staging vs Production

To prevent broken packages from bricking production servers, repositories must be segmented into progressive environments:

```text
[ Incoming Pool / CI Artifacts ]
              │
              ▼
    ┌──────────────────┐
    │  dev / unstable  │  <-- Bleeding edge, automated builds land here
    └─────────┬────────┘
              │  (Smoke & Integration Tests Pass)
              ▼
    ┌──────────────────┐
    │ staging / testing│  <-- Co-installability tests, multi-arch validation (2-7 days)
    └─────────┬────────┘
              │  (Human Sign-off / QA Gating)
              ▼
    ┌──────────────────┐
    │ production/stable│  <-- Locked, immutable release tags, guaranteed upgrade path
    └──────────────────┘
```

### Promotion Principles:
1. **Never Rebuild Between Stages**: The exact binary artifact compiled in CI must flow from `unstable` to `testing` to `stable`. Recompilation changes timestamps and binary hashes, invalidating prior testing.
2. **Atomic Ingestion**: Never overwrite packages in-place. Use versioned filenames and update index metadata atomically.

---

## 3. CDN Caching Strategies for Package Repositories

| Artifact Type | Cache-Control Header | Invalidation Strategy |
|---|---|---|
| **Packages (`.deb`, `.rpm`)** | `max-age=31536000, immutable` | Never invalidate; packages are content-addressed and immutable by version. |
| **Indices (`Packages.gz`, `primary.xml.gz`)** | `max-age=300, must-revalidate` | Invalidate on release or allow short 5-minute TTL. |
| **Top-Level Signed Metadata (`InRelease`, `repomd.xml`)** | `max-age=60, no-cache` | Must be re-checked frequently by clients to discover new package releases. |

---

## 4. Mirror Consistency: The "Sync Mid-Update" Problem

When mirrors synchronize via `rsync` or background HTTP jobs, a client fetching `repomd.xml` or `InRelease` might receive the *new* index while the referenced binary packages have not yet finished downloading to the mirror. This causes `404 Not Found` or checksum mismatch errors.

### Mitigation:
1. **Upload Packages First**: Mirrors must sync package pools before syncing metadata indices (`rsync --exclude 'repodata/' ...` followed by `rsync 'repodata/'`).
2. **Content-Hashed Metadata**: Modern APT and DNF repos use `by-hash` directories (`dists/stable/main/by-hash/SHA256/...`) ensuring metadata requests link to exact immutable hashes.