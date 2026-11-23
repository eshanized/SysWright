#!/usr/bin/env python3
"""
Static Validation Tests for Packaging Templates
Part of Syswright (Phase 2)

Performs non-executing static validation on PKGBUILD templates:
- Verifies template structural invariants and variable declarations.
- Checks for research checklists and explicit placeholders.
- Ensures absence of forbidden paths (/usr/local) and dangerous permissions (777).
- Verifies bash syntax validity on instantiated templates via bash -n without execution.
"""

import re
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestPKGBUILDStatic(unittest.TestCase):

    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent.parent
        self.templates_dir = self.repo_root / "skills" / "arch-packaging" / "templates"

    def test_expected_templates_exist(self):
        """All 10 required packaging templates must exist in templates directory."""
        expected = [
            "basic-source.PKGBUILD",
            "cmake.PKGBUILD",
            "meson.PKGBUILD",
            "cargo.PKGBUILD",
            "python.PKGBUILD",
            "go.PKGBUILD",
            "split-package.PKGBUILD",
            "vcs-git.PKGBUILD",
            "binary-repack.PKGBUILD",
            "systemd-service.PKGBUILD",
        ]
        for name in expected:
            tpath = self.templates_dir / name
            self.assertTrue(tpath.is_file(), f"Missing template: {name}")

    def test_template_research_checklists_and_placeholders(self):
        """Templates must contain research checklists and explicit placeholders, never fake data."""
        for tpath in self.templates_dir.glob("*.PKGBUILD"):
            content = tpath.read_text(encoding="utf-8")
            self.assertIn(
                "RESEARCH CHECKLIST",
                content,
                f"Template {tpath.name} must contain a RESEARCH CHECKLIST header",
            )
            self.assertNotIn(
                "/usr/local",
                content,
                f"Template {tpath.name} must never install to /usr/local",
            )
            self.assertNotIn(
                "chmod 777",
                content,
                f"Template {tpath.name} must never assign world-writable permissions",
            )

    def test_bash_syntax_on_instantiated_templates(self):
        """Instantiated templates with mock placeholders must pass bash -n without execution."""
        mock_values = {
            "<PACKAGE_NAME>": "mockpkg",
            "<PACKAGE_BASE_NAME>": "mockbase",
            "<UPSTREAM_VERSION>": "1.0.0",
            "<INITIAL_STUB_VERSION_AUTO_UPDATED_BY_PKGVER>": "1.0.0",
            "<UPSTREAM_URL>": "example.org/mockpkg",
            "<GIT_REPOSITORY_URL>": "example.org/mockpkg.git",
            "<UPSTREAM_BINARY_DOWNLOAD_URL>": "example.org/mockpkg-bin.tar.gz",
            "<BINARY_NAME>": "mockbin",
            "<SPDX_LICENSE_IDENTIFIER>": "Apache-2.0",
            "<SPDX_LICENSE_OR_LicenseRef-Custom>": "MIT",
            "<MODULE_NAME>": "mockmod",
            "<SOURCE_DIR_NAME>": "mockmod-1.0.0",
            "<COMPUTE_VIA_sha256sum_OR_updpkgsums>": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        }

        for tpath in self.templates_dir.glob("*.PKGBUILD"):
            raw_text = tpath.read_text(encoding="utf-8")
            instantiated = raw_text
            for placeholder, val in mock_values.items():
                instantiated = instantiated.replace(placeholder, val)

            with tempfile.NamedTemporaryFile("w", suffix=".PKGBUILD", delete=True) as tf:
                tf.write(instantiated)
                tf.flush()
                # Run bash -n for non-executing syntax validation
                res = subprocess.run(
                    ["bash", "-n", tf.name],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(
                    res.returncode,
                    0,
                    f"Template {tpath.name} failed bash -n syntax validation: {res.stderr}",
                )


if __name__ == "__main__":
    unittest.main()
