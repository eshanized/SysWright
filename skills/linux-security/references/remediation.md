# Security Remediation: Patch Engineering, Verification, and Disclosure

Technical reference for writing security patches, verifying defensive fixes, preventing regression side-effects, and responsible disclosure.

---

## 1. Principles of Security Patch Engineering

Security patches require extreme surgical discipline:

1. **Minimal Surface Area**:
   A security patch must fix only the vulnerability. Do not combine security fixes with refactoring, code formatting, or feature enhancements. Combining changes increases regression risk and complicates downstream distribution backporting.
2. **Defend at the Boundary**:
   Validate inputs immediately upon crossing the trust boundary before data reaches internal structures or parsers.
3. **Fail Closed (Safe Defaults)**:
   If an unexpected return code, invalid header, or memory allocation error occurs, immediately fail closed (terminate connection, return `EACCES` or `EINVAL`, or abort). Never fall through to default processing.

---

## 2. Regression Testing for Security Patches

Every security patch must be accompanied by an automated regression test:

```python
# test_path_traversal_regression.py
import unittest
from pathlib import Path
from my_app import safe_read_file

class TestPathTraversalRegression(unittest.TestCase):
    def test_rejection_of_dot_dot_escape(self):
        """Ensure path traversal payloads are rejected with PermissionError."""
        malicious_paths = [
            "../../etc/passwd",
            "....//....//etc/shadow",
            "normal_dir/../../../etc/hosts",
            "/etc/passwd\0.png",
        ]
        for path in malicious_paths:
            with self.subTest(path=path):
                with self.assertRaises(PermissionError):
                    safe_read_file(path)
```

---

## 3. Responsible Disclosure and Redaction Rules

When producing security reports or patch proposals:

1. **Zero Secret Leakage**:
   Never include real passwords, private keys, API tokens, session cookies, or user PII in bug reports, commit messages, or test fixtures. Use RFC-compliant dummy data (`example.com`, `0xdeadbeef`, `192.0.2.1` TEST-NET).
2. **Coordinated Vulnerability Disclosure (CVD)**:
   Disclose zero-day vulnerabilities privately to upstream maintainers (via security mailing lists, security.txt, or private GitHub security advisories) with an agreed embargo window (typically 90 days) before publishing public technical write-ups.
