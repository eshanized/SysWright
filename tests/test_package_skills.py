#!/usr/bin/env python3
"""
Unit tests for package-skills.py
Part of Linux Engineering (Phase 1)
"""

import importlib.util
import tarfile
import tempfile
import unittest
from pathlib import Path

# Load package-skills.py with importlib due to hyphen in filename
script_path = Path(__file__).resolve().parent.parent / "scripts" / "package-skills.py"
spec = importlib.util.spec_from_file_location("package_skills", script_path)
package_skills = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package_skills)

package_archive = package_skills.package_archive
package_claude_code = package_skills.package_claude_code
package_codex = package_skills.package_codex
safe_copy_file = package_skills.safe_copy_file
is_excluded = package_skills.is_excluded


class TestPackageSkills(unittest.TestCase):

    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent

    def test_path_traversal_protection(self):
        """safe_copy_file must reject destinations escaping base_dst."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dst = Path(tmpdir) / "output"
            base_dst.mkdir()
            src = Path(tmpdir) / "src.txt"
            src.write_text("content", encoding="utf-8")

            escaped_dst = base_dst / ".." / "escaped.txt"
            with self.assertRaises(ValueError):
                safe_copy_file(src, escaped_dst, base_dst)

    def test_exclude_patterns(self):
        """is_excluded must correctly identify VCS, cache, and secret files."""
        self.assertTrue(is_excluded(Path("skills/linux-engineer/.git/HEAD")))
        self.assertTrue(is_excluded(Path("skills/__pycache__/module.cpython-314.pyc")))
        self.assertTrue(is_excluded(Path(".env")))
        self.assertFalse(is_excluded(Path("skills/linux-engineer/SKILL.md")))
        self.assertFalse(is_excluded(Path("references/safety-policy.md")))

    def test_package_archive_deterministic(self):
        """package_archive must produce a valid .tar.gz bundle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            tar_path = package_archive(self.repo_root, out_dir, version="0.1.0-test")
            self.assertTrue(tar_path.is_file())
            self.assertTrue(tar_path.name.endswith(".tar.gz"))

            # Inspect archive contents
            with tarfile.open(tar_path, "r:gz") as tar:
                names = tar.getnames()
                self.assertTrue(any("skills/linux-engineer/SKILL.md" in n for n in names))
                self.assertTrue(any("references/safety-policy.md" in n for n in names))
                self.assertTrue(any("AGENTS.md" in n for n in names))
                # Ensure excluded files are NOT in archive
                self.assertFalse(any("__pycache__" in n for n in names))
                self.assertFalse(any(".git" in n for n in names))

    def test_package_claude_code(self):
        """package_claude_code must generate plugin structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            plugin_dir = package_claude_code(self.repo_root, out_dir)
            self.assertTrue(plugin_dir.is_dir())
            self.assertTrue((plugin_dir / ".claude-plugin" / "plugin.json").is_file())
            self.assertTrue((plugin_dir / "skills" / "linux-engineer" / "SKILL.md").is_file())

    def test_package_codex(self):
        """package_codex must generate Codex structure with AGENTS.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            codex_dir = package_codex(self.repo_root, out_dir)
            self.assertTrue(codex_dir.is_dir())
            self.assertTrue((codex_dir / "AGENTS.md").is_file())
            self.assertTrue((codex_dir / "skills" / "linux-research" / "SKILL.md").is_file())
            self.assertTrue((codex_dir / "agents" / "openai.yaml").is_file())


if __name__ == "__main__":
    unittest.main()
