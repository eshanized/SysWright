#!/usr/bin/env python3
"""
Unit tests for validate-skills.py
Part of Syswright (Phase 1)
"""

import importlib.util
import tempfile
import unittest
from pathlib import Path

# Load validate-skills.py with importlib due to hyphen in filename
script_path = Path(__file__).resolve().parent.parent / "scripts" / "validate-skills.py"
spec = importlib.util.spec_from_file_location("validate_skills", script_path)
validate_skills = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_skills)

NAME_REGEX = validate_skills.NAME_REGEX
extract_frontmatter = validate_skills.extract_frontmatter
parse_simple_yaml = validate_skills.parse_simple_yaml
validate_skill_directory = validate_skills.validate_skill_directory
FrontmatterParseError = validate_skills.FrontmatterParseError


class TestValidateSkills(unittest.TestCase):

    def test_canonical_skills_pass_validation(self):
        """All canonical skills in the repository must pass validation."""
        repo_root = Path(__file__).resolve().parent.parent
        skills_root = repo_root / "skills"
        for sdir in skills_root.iterdir():
            if sdir.is_dir() and (sdir / "SKILL.md").is_file():
                errors = validate_skill_directory(sdir)
                self.assertEqual(errors, [], f"Skill '{sdir.name}' failed validation: {errors}")

    def test_name_regex(self):
        """Test name validation regex according to Agent Skills spec."""
        self.assertTrue(NAME_REGEX.match("linux-engineer"))
        self.assertTrue(NAME_REGEX.match("arch-packaging-1"))
        self.assertTrue(NAME_REGEX.match("test"))
        self.assertFalse(NAME_REGEX.match("Linux-Engineer"))  # No uppercase
        self.assertFalse(NAME_REGEX.match("-test"))           # No leading hyphen
        self.assertFalse(NAME_REGEX.match("test-"))           # No trailing hyphen
        self.assertFalse(NAME_REGEX.match("test--name"))       # No consecutive hyphens
        self.assertFalse(NAME_REGEX.match("test_name"))       # No underscores

    def test_yaml_frontmatter_parser(self):
        """Test zero-dependency YAML frontmatter parser."""
        sample = """
name: my-skill
description: |
  A multiline description
  spanning two lines.
compatibility: "Linux only"
metadata:
  author: "Tester"
  fork: true
"""
        data = parse_simple_yaml(sample)
        self.assertEqual(data["name"], "my-skill")
        self.assertIn("A multiline description", data["description"])
        self.assertEqual(data["compatibility"], "Linux only")
        self.assertIsInstance(data["metadata"], dict)
        self.assertEqual(data["metadata"]["author"], "Tester")
        self.assertTrue(data["metadata"]["fork"])

    def test_malformed_frontmatter_missing_dashes(self):
        """Test error when opening dashes are missing."""
        content = "name: invalid\ndescription: missing frontmatter dashes"
        with self.assertRaises(FrontmatterParseError):
            extract_frontmatter(content)

    def test_malformed_frontmatter_unclosed(self):
        """Test error when closing dashes are missing."""
        content = "---\nname: invalid\ndescription: unclosed\n"
        with self.assertRaises(FrontmatterParseError):
            extract_frontmatter(content)

    def test_broken_relative_link_detection(self):
        """Test detection of broken relative file references in SKILL.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdir = Path(tmpdir) / "test-skill"
            sdir.mkdir()
            skill_md = sdir / "SKILL.md"
            skill_md.write_text(
                "---\nname: test-skill\ndescription: Test skill\n---\n"
                "# Instructions\nSee [broken link](references/missing.md) here.\n",
                encoding="utf-8",
            )
            errors = validate_skill_directory(sdir)
            self.assertTrue(any("broken relative reference" in e.lower() for e in errors))

    def test_mismatched_directory_name(self):
        """Test error when frontmatter name does not match directory name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdir = Path(tmpdir) / "dir-name"
            sdir.mkdir()
            skill_md = sdir / "SKILL.md"
            skill_md.write_text(
                "---\nname: different-name\ndescription: Test skill\n---\n",
                encoding="utf-8",
            )
            errors = validate_skill_directory(sdir)
            self.assertTrue(any("does not match directory name" in e.lower() for e in errors))


if __name__ == "__main__":
    unittest.main()
