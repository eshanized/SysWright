#!/usr/bin/env python3
"""Tests for the multi-agent SysWright installer."""

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "install.py"
SPEC = importlib.util.spec_from_file_location("syswright_install", SCRIPT)
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class InstallerTests(unittest.TestCase):
    def make_skill(self, root, name="example"):
        skill = root / "skills" / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: example\ndescription: Example skill\n---\n", encoding="utf-8")
        return skill

    def test_detects_agents_by_executable_or_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            (home / ".codex").mkdir()
            with mock.patch.object(installer.shutil, "which", return_value=None):
                agents = installer.discover_agents(home=home, path="")
            self.assertEqual([agent.name for agent in agents], ["codex"])

    def test_installs_to_every_selected_agent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            skill = self.make_skill(root)
            claude = installer.Agent("claude", "Claude Code", "claude", Path(tmp) / ".claude",
                                     Path(tmp) / ".claude" / "skills")
            codex = installer.Agent("codex", "OpenAI Codex", "codex", Path(tmp) / ".codex",
                                    Path(tmp) / ".agents" / "skills")
            plans = installer.plan_install([skill], [claude, codex], "user", root, root)
            self.assertEqual(installer.install([skill], plans), 0)
            self.assertTrue((claude.skill_dir / "example" / "SKILL.md").is_file())
            self.assertTrue((codex.skill_dir / "example" / "SKILL.md").is_file())

    def test_dry_run_does_not_create_destinations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            skill = self.make_skill(root)
            agent = installer.Agent("codex", "Codex", "codex", Path(tmp) / ".codex",
                                    Path(tmp) / ".agents" / "skills")
            self.assertEqual(installer.install([skill], [(agent, agent.skill_dir)], dry_run=True), 0)
            self.assertFalse(agent.skill_dir.exists())

    def test_conflict_aborts_all_agents_before_copying(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            skill = self.make_skill(root)
            first = installer.Agent("claude", "Claude", "claude", Path(tmp) / ".claude",
                                    Path(tmp) / ".claude" / "skills")
            second = installer.Agent("codex", "Codex", "codex", Path(tmp) / ".codex",
                                     Path(tmp) / ".agents" / "skills")
            (second.skill_dir / "example").mkdir(parents=True)
            self.assertEqual(installer.install([skill], [(first, first.skill_dir), (second, second.skill_dir)]), 2)
            self.assertFalse((first.skill_dir / "example").exists())

    def test_rejects_symlinked_skill_contents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            skill = self.make_skill(root)
            outside = Path(tmp) / "outside"
            outside.write_text("external", encoding="utf-8")
            try:
                (skill / "external.txt").symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("Symlink creation unavailable")
            with self.assertRaises(ValueError):
                installer.find_skills(root)


if __name__ == "__main__":
    unittest.main()
