#!/usr/bin/env python3
"""
Unit tests for check-references.py
Part of Syswright (Phase 1)
"""

import importlib.util
import tempfile
import unittest
from pathlib import Path

# Load check-references.py with importlib due to hyphen in filename
script_path = Path(__file__).resolve().parent.parent / "scripts" / "check-references.py"
spec = importlib.util.spec_from_file_location("check_references", script_path)
check_references = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_references)

extract_links_from_file = check_references.extract_links_from_file
validate_references = check_references.validate_references


class TestCheckReferences(unittest.TestCase):

    def test_repo_has_zero_broken_references(self):
        """Repository documentation must have 0 broken internal references."""
        repo_root = Path(__file__).resolve().parent.parent
        success, broken = validate_references(repo_root, check_external=False)
        self.assertTrue(success, f"Broken references found: {broken}")
        self.assertEqual(len(broken), 0)

    def test_link_extraction(self):
        """Test markdown link extractor."""
        with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as f:
            f.write("A link to [Local File](sub/path.md) and [Anchor](#heading).\n")
            f_path = Path(f.name)

        try:
            links = extract_links_from_file(f_path)
            self.assertEqual(len(links), 2)
            self.assertEqual(links[0][0], "Local File")
            self.assertEqual(links[0][1], "sub/path.md")
            self.assertEqual(links[1][0], "Anchor")
            self.assertEqual(links[1][1], "#heading")
        finally:
            f_path.unlink()

    def test_broken_link_detection(self):
        """Test that broken relative link is properly flagged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "skills").mkdir()
            md = root / "skills" / "doc.md"
            md.write_text("See [missing](nonexistent.md)", encoding="utf-8")

            success, broken = validate_references(root, check_external=False)
            self.assertFalse(success)
            self.assertIn("skills/doc.md", broken)
            self.assertTrue(any("nonexistent.md" in e for e in broken["skills/doc.md"]))


if __name__ == "__main__":
    unittest.main()
