#!/usr/bin/env python3
"""
Unit tests for discover_environment.py
Part of Syswright (Phase 1)
"""

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "linux-environment" / "scripts"))
from discover_environment import discover_environment, parse_os_release


class TestDiscoverEnvironment(unittest.TestCase):

    def setUp(self):
        self.fixtures_dir = Path(__file__).resolve().parent.parent / "evals" / "fixtures"

    def test_live_environment_discovery(self):
        """Test safe discovery on active system."""
        data = discover_environment("/")
        self.assertIn("distribution", data)
        self.assertIn("kernel", data)
        self.assertIn("context", data)
        self.assertIn("init", data)
        self.assertIn("toolchains", data)
        self.assertTrue(data["kernel"]["release"])

    def test_fixture_arch_linux(self):
        """Test discovery on Arch Linux fixture."""
        data = discover_environment(str(self.fixtures_dir / "arch"))
        distro = data["distribution"]
        self.assertEqual(distro["id"], "arch")
        self.assertEqual(distro["name"], "Arch Linux")
        self.assertEqual(data["kernel"]["release"], "6.18.64-1-lts")
        self.assertTrue(data["kernel"]["is_lts"])

    def test_fixture_debian(self):
        """Test discovery on Debian 12 fixture."""
        data = discover_environment(str(self.fixtures_dir / "debian"))
        distro = data["distribution"]
        self.assertEqual(distro["id"], "debian")
        self.assertEqual(distro["version"], "12")
        self.assertIn("bookworm", distro["pretty_name"].lower())

    def test_fixture_fedora(self):
        """Test discovery on Fedora 41 fixture."""
        data = discover_environment(str(self.fixtures_dir / "fedora"))
        distro = data["distribution"]
        self.assertEqual(distro["id"], "fedora")
        self.assertEqual(distro["version"], "41")

    def test_fixture_ubuntu(self):
        """Test discovery on Ubuntu 24.04 fixture."""
        data = discover_environment(str(self.fixtures_dir / "ubuntu"))
        distro = data["distribution"]
        self.assertEqual(distro["id"], "ubuntu")
        self.assertEqual(distro["version"], "24.04")
        self.assertIn("debian", distro["id_like"])

    def test_fixture_unknown_distro(self):
        """Test discovery on custom/unknown distribution fixture."""
        data = discover_environment(str(self.fixtures_dir / "unknown"))
        distro = data["distribution"]
        self.assertEqual(distro["id"], "embeddedos")
        self.assertEqual(distro["name"], "EmbeddedLinuxOS")

    def test_fixture_container(self):
        """Test container execution context detection."""
        data = discover_environment(str(self.fixtures_dir / "container"))
        ctx = data["context"]
        self.assertEqual(ctx["type"], "container")
        self.assertTrue(any("docker" in d for d in ctx["details"]))

    def test_fixture_virtual_machine(self):
        """Test virtual machine execution context detection."""
        data = discover_environment(str(self.fixtures_dir / "vm"))
        ctx = data["context"]
        self.assertEqual(ctx["type"], "vm")
        self.assertTrue(any("kvm" in d or "qemu" in d for d in ctx["details"]))

    def test_fixture_minimal_missing_files(self):
        """Test graceful degradation on minimal rootfs without os-release."""
        data = discover_environment(str(self.fixtures_dir / "minimal"))
        self.assertEqual(data["distribution"]["id"], "unknown")
        self.assertEqual(data["distribution"]["confidence"], "low")


if __name__ == "__main__":
    unittest.main()
