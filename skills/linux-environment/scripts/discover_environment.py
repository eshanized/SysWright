#!/usr/bin/env python3
"""
Linux Environment Discovery Tool
Part of Linux Engineering (Phase 1)

Performs safe, unprivileged, read-only discovery of the host or target Linux
environment, including distribution identity, kernel version, execution context
(native, container, VM), init system, and installed compiler toolchains.
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def parse_os_release(rootfs: Path = Path("/")) -> Dict[str, str]:
    """Parse /etc/os-release or /usr/lib/os-release without executing bash."""
    os_release_paths = [
        rootfs / "etc" / "os-release",
        rootfs / "usr" / "lib" / "os-release",
    ]
    data: Dict[str, str] = {}
    for p in os_release_paths:
        if p.is_file():
            try:
                with p.open("r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip('"').strip("'")
                            data[k] = v
                if data:
                    break
            except Exception:
                pass
    return data


def detect_distribution(rootfs: Path = Path("/")) -> Dict[str, Any]:
    """Detect distribution name, ID, version, and family."""
    os_rel = parse_os_release(rootfs)
    distro_id = os_rel.get("ID", "").lower()
    distro_name = os_rel.get("NAME", "Unknown Linux")
    distro_pretty = os_rel.get("PRETTY_NAME", distro_name)
    distro_version = os_rel.get("VERSION_ID", "")
    build_id = os_rel.get("BUILD_ID", "")
    id_like = os_rel.get("ID_LIKE", "").split()

    confidence = "high" if distro_id else "low"

    # Fallback heuristic if os-release is absent
    if not distro_id:
        if (rootfs / "etc" / "arch-release").is_file():
            distro_id = "arch"
            distro_name = "Arch Linux"
            confidence = "medium"
        elif (rootfs / "etc" / "debian_version").is_file():
            distro_id = "debian"
            distro_name = "Debian GNU/Linux"
            confidence = "medium"
        elif (rootfs / "etc" / "fedora-release").is_file():
            distro_id = "fedora"
            distro_name = "Fedora"
            confidence = "medium"

    return {
        "id": distro_id or "unknown",
        "name": distro_name,
        "pretty_name": distro_pretty,
        "version": distro_version,
        "build_id": build_id,
        "id_like": id_like,
        "confidence": confidence,
    }


def detect_kernel(rootfs: Path = Path("/")) -> Dict[str, Any]:
    """Detect active kernel release, version, and architecture."""
    # When testing against mock rootfs, check if mock proc/version exists
    proc_version = rootfs / "proc" / "version"
    release_str = platform.release()
    version_str = platform.version()
    machine_str = platform.machine()

    if rootfs != Path("/") and proc_version.is_file():
        try:
            content = proc_version.read_text(encoding="utf-8", errors="replace").strip()
            # Linux version 6.18.64-1-lts ...
            parts = content.split()
            if len(parts) >= 3 and parts[0] == "Linux" and parts[1] == "version":
                release_str = parts[2]
        except Exception:
            pass

    return {
        "release": release_str,
        "version": version_str,
        "architecture": machine_str,
        "is_lts": "lts" in release_str.lower(),
    }


def detect_execution_context(rootfs: Path = Path("/")) -> Dict[str, Any]:
    """Detect if running on native hardware, container, virtual machine, or chroot."""
    context_type = "native"
    details: List[str] = []

    # 1. Container check
    if (rootfs / ".dockerenv").is_file():
        context_type = "container"
        details.append("dockerenv-present")
    elif (rootfs / "run" / ".containerenv").is_file():
        context_type = "container"
        details.append("containerenv-present")

    cgroup_file = rootfs / "proc" / "1" / "cgroup"
    if cgroup_file.is_file():
        try:
            content = cgroup_file.read_text(encoding="utf-8", errors="replace")
            for marker in ("docker", "containerd", "lxc", "kubepods"):
                if marker in content:
                    context_type = "container"
                    details.append(f"cgroup-{marker}")
                    break
        except Exception:
            pass

    # 2. Virtual machine check (if not container)
    if context_type != "container":
        # Check systemd-detect-virt if available and rootfs is /
        if rootfs == Path("/") and shutil.which("systemd-detect-virt"):
            try:
                res = subprocess.run(
                    ["systemd-detect-virt", "--vm"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if res.returncode == 0 and res.stdout.strip() and res.stdout.strip() != "none":
                    context_type = "vm"
                    details.append(f"virt-{res.stdout.strip()}")
            except Exception:
                pass

        # Check dmi product name if available
        dmi_product = rootfs / "sys" / "class" / "dmi" / "id" / "product_name"
        if dmi_product.is_file():
            try:
                prod = dmi_product.read_text(encoding="utf-8", errors="replace").lower()
                for vm_marker in ("qemu", "kvm", "virtualbox", "vmware"):
                    if vm_marker in prod:
                        context_type = "vm"
                        details.append(f"dmi-{vm_marker}")
                        break
            except Exception:
                pass

    return {
        "type": context_type,
        "details": details,
        "confidence": "high" if details else "medium",
    }


def detect_init_system(rootfs: Path = Path("/")) -> Dict[str, Any]:
    """Detect the active init system safely."""
    init_name = "unknown"
    version = ""

    # Check for systemd
    if (rootfs / "run" / "systemd" / "system").is_dir():
        init_name = "systemd"
        if rootfs == Path("/") and shutil.which("systemd"):
            try:
                res = subprocess.run(
                    ["systemctl", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if res.returncode == 0:
                    first_line = res.stdout.splitlines()[0]
                    # systemd 256 (256.7-1-arch)
                    parts = first_line.split()
                    if len(parts) >= 2:
                        version = parts[1]
            except Exception:
                pass
    elif (rootfs / "sbin" / "init").is_file():
        init_name = "sysvinit-or-custom"

    return {
        "name": init_name,
        "version": version,
    }


def query_tool(binary_name: str, version_args: List[str] = None) -> Optional[Dict[str, str]]:
    """Query whether a tool exists in PATH and safely fetch its first version line."""
    if version_args is None:
        version_args = ["--version"]
    path = shutil.which(binary_name)
    if not path:
        return None
    version_str = "unknown"
    try:
        res = subprocess.run(
            [path] + version_args,
            capture_output=True,
            text=True,
            timeout=2,
        )
        if res.stdout:
            version_str = res.stdout.splitlines()[0].strip()
        elif res.stderr:
            version_str = res.stderr.splitlines()[0].strip()
    except Exception:
        pass
    return {"path": path, "version": version_str}


def detect_toolchains(rootfs: Path = Path("/")) -> Dict[str, Any]:
    """Detect available compilers, build systems, and development utilities."""
    # When inspecting mock rootfs other than /, return empty or mock data
    if rootfs != Path("/"):
        return {"compilers": {}, "build_systems": {}, "packaging": {}, "diagnostics": {}}

    compilers = {}
    for c, varg in [("gcc", ["--version"]), ("clang", ["--version"]), ("rustc", ["--version"])]:
        info = query_tool(c, varg)
        if info:
            compilers[c] = info

    build_systems = {}
    for b in ["meson", "cmake", "make", "ninja", "cargo"]:
        info = query_tool(b)
        if info:
            build_systems[b] = info

    packaging = {}
    for p in ["makepkg", "pkgctl", "dpkg", "rpm", "pacman", "apt", "dnf"]:
        info = query_tool(p)
        if info:
            packaging[p] = info

    diagnostics = {}
    for d, varg in [
        ("systemd-analyze", ["--version"]),
        ("namcap", ["-v"]),
        ("strace", ["-V"]),
        ("gdb", ["--version"]),
        ("perf", ["--version"]),
        ("bpftrace", ["--version"]),
    ]:
        info = query_tool(d, varg)
        if info:
            diagnostics[d] = info

    return {
        "compilers": compilers,
        "build_systems": build_systems,
        "packaging": packaging,
        "diagnostics": diagnostics,
    }


def discover_environment(rootfs_path: str = "/") -> Dict[str, Any]:
    """Master discovery function returning normalized environment descriptor."""
    rootfs = Path(rootfs_path)
    distro = detect_distribution(rootfs)
    kernel = detect_kernel(rootfs)
    context = detect_execution_context(rootfs)
    init = detect_init_system(rootfs)
    toolchains = detect_toolchains(rootfs)

    return {
        "distribution": distro,
        "kernel": kernel,
        "context": context,
        "init": init,
        "toolchains": toolchains,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Safe Linux Environment Discovery")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format")
    parser.add_argument("--rootfs", default="/", help="Path to root filesystem (useful for test fixtures)")
    args = parser.parse_args()

    data = discover_environment(args.rootfs)

    if args.format == "json":
        print(json.dumps(data, indent=2))
    else:
        distro = data["distribution"]
        kernel = data["kernel"]
        ctx = data["context"]
        print(f"Distribution : {distro['pretty_name']} (ID: {distro['id']})")
        print(f"Kernel       : {kernel['release']} ({kernel['architecture']})")
        print(f"Context      : {ctx['type']} ({', '.join(ctx['details']) or 'none'})")
        print(f"Init System  : {data['init']['name']} {data['init']['version']}")
        print(f"Compilers    : {', '.join(data['toolchains']['compilers'].keys()) or 'None'}")
        print(f"Build Systems: {', '.join(data['toolchains']['build_systems'].keys()) or 'None'}")
        print(f"Packaging    : {', '.join(data['toolchains']['packaging'].keys()) or 'None'}")


if __name__ == "__main__":
    main()
