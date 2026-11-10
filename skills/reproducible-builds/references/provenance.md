# Supply-Chain Levels for Software Artifacts (SLSA) & Provenance

Build provenance provides verifiable, authenticated claims about how a software artifact was created, what source commit it derived from, and what build infrastructure produced it.

---

## 1. SLSA Framework Overview (SLSA v1.0)

Supply-chain Levels for Software Artifacts (SLSA) defines progressive security levels:

| SLSA Level | Core Requirement | Attack Vector Mitigated |
|---|---|---|
| **Build L1** | Scripted build process; automated provenance generated. | Unrecorded manual builds, unknown source code. |
| **Build L2** | Hosted build service (CI/CD); provenance authenticated by builder service. | Tampering on developer workstations, forged build metadata. |
| **Build L3** | Hardened build platform (ephemeral workers, isolated environments); unforgeable provenance. | Compromised build nodes injecting malicious steps, cross-build contamination. |

---

## 2. In-Toto Attestation Format

Provenance statements are formatted as in-toto attestations (`statement.jsonl`). An attestation binds a subject (the compiled binary) to a predicate (the build parameters and environment).

### Anatomy of an In-Toto SLSA Provenance Predicate:
```json
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [
    {
      "name": "myapp-1.2.3-x86_64.rpm",
      "digest": {
        "sha256": "3a7bd3e2360a3d29eea436fcfb7e44c735d117c42d1c1835420b6b9942dd4f1b"
      }
    }
  ],
  "predicateType": "https://slsa.dev/provenance/v1",
  "predicate": {
    "buildDefinition": {
      "buildType": "https://actions.github.com/workflow/v1",
      "externalParameters": {
        "repository": "https://github.com/example/myapp",
        "ref": "refs/tags/v1.2.3"
      },
      "internalParameters": {},
      "resolvedDependencies": [
        {
          "uri": "git+https://github.com/example/myapp@commit-sha-abc1234",
          "digest": {
            "gitCommit": "abc1234567890abcdef1234567890abcdef12"
          }
        }
      ]
    },
    "runDetails": {
      "builder": {
        "id": "https://github.com/actions/runner"
      },
      "metadata": {
        "invocationId": "https://github.com/example/myapp/actions/runs/12345678",
        "startedOn": "2026-04-01T12:00:00Z",
        "finishedOn": "2026-04-01T12:05:00Z"
      }
    }
  }
}
```

---

## 3. Cryptographic Verification of Provenance

Clients or package maintainers verify that the artifact matches the cryptographic statement:
```bash
# Verify using slsa-verifier tool
slsa-verifier verify-artifact \
  --provenance-path build/myapp.intoto.jsonl \
  --source-uri github.com/example/myapp \
  --source-tag v1.2.3 \
  bin/myapp
```