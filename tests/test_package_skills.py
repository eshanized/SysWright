#!/usr/bin/env python3
"""Security and reproducibility tests for package-skills.py."""

import hashlib
import importlib.util
import os
import tarfile
import tempfile
import unittest
from pathlib import Path

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

    def test_destination_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            base = root / "output"
            base.mkdir()
            source = root / "source.txt"
            source.write_text("content", encoding="utf-8")
            with self.assertRaises(ValueError):
                safe_copy_file(source, base / ".." / "escaped.txt", base, root)

    def test_external_source_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            repository = root / "repo"
            repository.mkdir()
            outside = root / "outside.txt"
            outside.write_text("secret", encoding="utf-8")
            link = repository / "linked.txt"
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("Symlink creation is unavailable")
            output = root / "output"
            output.mkdir()
            with self.assertRaises(ValueError):
                safe_copy_file(link, output / "linked.txt", output, repository)

    def test_symlinked_directory_is_rejected_during_packaging(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            repo = root / "repo"
            (repo / "skills").mkdir(parents=True)
            outside = root / "outside"
            outside.mkdir()
            (outside / "SKILL.md").write_text("not trusted", encoding="utf-8")
            try:
                (repo / "skills" / "external").symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Symlink creation is unavailable")
            with self.assertRaises(ValueError):
                package_archive(repo, root / "dist")

    def test_exclude_patterns(self):
        self.assertTrue(is_excluded(Path("skills/.git/HEAD")))
        self.assertTrue(is_excluded(Path("skills/__pycache__/module.pyc")))
        self.assertTrue(is_excluded(Path(".env")))
        self.assertTrue(is_excluded(Path("private/id_rsa")))
        self.assertTrue(is_excluded(Path("certs/signing.pem")))
        self.assertFalse(is_excluded(Path("skills/linux-engineer/SKILL.md")))
        self.assertFalse(is_excluded(Path("references/safety-policy.md")))

    def test_archive_is_reproducible_across_output_directories(self):
        import hashlib
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            previous = os.environ.get("SOURCE_DATE_EPOCH")
            os.environ["SOURCE_DATE_EPOCH"] = "1700000000"
            try:
                one = package_archive(self.repo_root, Path(first), version="repro-test")
                two = package_archive(self.repo_root, Path(second), version="repro-test")
            finally:
                if previous is None:
                    os.environ.pop("SOURCE_DATE_EPOCH", None)
                else:
                    os.environ["SOURCE_DATE_EPOCH"] = previous
            digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(digest(one), digest(two))
            with tarfile.open(one, "r:gz") as archive:
                names = archive.getnames()
                self.assertTrue(any("skills/linux-engineer/SKILL.md" in name for name in names))
                self.assertTrue(any("references/safety-policy.md" in name for name in names))
                self.assertTrue(any(name.endswith("/AGENTS.md") for name in names))
                self.assertFalse(any("__pycache__" in name or "/.git/" in name for name in names))

    def test_output_inside_packaged_source_tree_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Use a temporary fixture repository rather than touching the checkout.
            repo = Path(tmpdir) / "repo"
            (repo / "skills").mkdir(parents=True)
            (repo / "skills" / "sample").mkdir()
            (repo / "skills" / "sample" / "SKILL.md").write_text(
                "---\\nname: sample\\ndescription: Sample skill\\n---\\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                package_archive(repo, repo / "skills" / "dist")
            self.assertFalse((repo / "skills" / "dist").exists())

    def test_archive_rejects_invalid_source_date_epoch(self):
        previous = os.environ.get("SOURCE_DATE_EPOCH")
        os.environ["SOURCE_DATE_EPOCH"] = "not-an-epoch"
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                with self.assertRaises(ValueError):
                    package_archive(self.repo_root, Path(tmpdir))
        finally:
            if previous is None:
                os.environ.pop("SOURCE_DATE_EPOCH", None)
            else:
                os.environ["SOURCE_DATE_EPOCH"] = previous

    def test_claude_code_plugin_layout(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin = package_claude_code(self.repo_root, Path(tmpdir))
            self.assertTrue((plugin / ".claude-plugin" / "plugin.json").is_file())
            self.assertTrue((plugin / "skills" / "linux-engineer" / "SKILL.md").is_file())

    def test_codex_layout_uses_agents_skills(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bundle = package_codex(self.repo_root, Path(tmpdir))
            self.assertTrue((bundle / "AGENTS.md").is_file())
            self.assertTrue((bundle / ".agents" / "skills" / "linux-research" / "SKILL.md").is_file())
            self.assertFalse((bundle / "skills").exists())

    def test_packagers_do_not_delete_existing_artifacts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            existing = output / "codex-package"
            existing.mkdir()
            marker = existing / "keep.txt"
            marker.write_text("preserve", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                package_codex(self.repo_root, output)
            self.assertEqual(marker.read_text(encoding="utf-8"), "preserve")


if __name__ == "__main__":
    unittest.main()
