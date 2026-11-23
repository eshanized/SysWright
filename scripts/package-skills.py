#!/usr/bin/env python3
"""
Deterministic Skill Packaging Tool
Part of Syswright

Packages canonical Agent Skills and references into distribution artifacts:
- 'archive': Deterministic .tar.gz bundle for general Agent Skills runtimes.
- 'claude-code': Bundled plugin distribution for Claude Code.
- 'codex': Packaged directory layout for OpenAI Codex with AGENTS.md.

Guarantees:
- Path traversal protection.
- Deterministic archive timestamps (SOURCE_DATE_EPOCH support).
- Exclusion of secrets, VCS files (.git), and temporary artifacts.
- Validation gate before packaging.
"""

import argparse
import json
import os
import shutil
import sys
import tarfile
import time
from pathlib import Path
from typing import List, Set

# Import validator logic directly from sibling script
val_script = Path(__file__).parent / "validate-skills.py"
if val_script.is_file():
    import importlib.util
    spec = importlib.util.spec_from_file_location("validate_skills", val_script)
    val_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(val_mod)
    find_all_skills = val_mod.find_all_skills
    validate_skill_directory = val_mod.validate_skill_directory
else:
    find_all_skills = lambda root: []
    validate_skill_directory = None


EXCLUDE_PATTERNS = {
    ".git",
    ".gitignore",
    ".DS_Store",
    "__pycache__",
    ".pytest_cache",
    ".coverage",
    ".env",
    "node_modules",
}


def is_excluded(path: Path) -> bool:
    """Check if file or directory should be excluded from packages."""
    for part in path.parts:
        if part in EXCLUDE_PATTERNS or part.endswith(".pyc") or part.endswith(".swp"):
            return True
    return False


def safe_copy_file(src: Path, dst: Path, base_dst: Path) -> None:
    """Copy file ensuring dst does not escape base_dst (path traversal guard)."""
    dst_resolved = dst.resolve()
    base_resolved = base_dst.resolve()
    try:
        dst_resolved.relative_to(base_resolved)
    except ValueError:
        raise ValueError(f"Path traversal detected: {dst} is outside {base_dst}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def package_archive(repo_root: Path, output_dir: Path, version: str = "0.1.0") -> Path:
    """Create a deterministic .tar.gz distribution archive."""
    archive_name = f"syswright-{version}.tar.gz"
    output_dir.mkdir(parents=True, exist_ok=True)
    target_tar = output_dir / archive_name

    # Determine fixed timestamp for reproducible builds
    epoch_str = os.environ.get("SOURCE_DATE_EPOCH")
    mtime = int(epoch_str) if epoch_str and epoch_str.isdigit() else int(time.time())

    items_to_pack = ["skills", "references", "docs", "adapters", ".claude-plugin", "AGENTS.md"]

    def tar_filter(tarinfo: tarfile.TarInfo) -> tarfile.TarInfo:
        # Normalize ownership and permissions
        tarinfo.uid = 0
        tarinfo.gid = 0
        tarinfo.uname = "root"
        tarinfo.gname = "root"
        tarinfo.mtime = mtime
        if tarinfo.isreg():
            # Check executable bit
            if tarinfo.mode & 0o111:
                tarinfo.mode = 0o755
            else:
                tarinfo.mode = 0o644
        elif tarinfo.isdir():
            tarinfo.mode = 0o755
        return tarinfo

    with tarfile.open(target_tar, "w:gz") as tar:
        for item in sorted(items_to_pack):
            p = repo_root / item
            if not p.exists():
                continue
            if p.is_file():
                tar.add(p, arcname=f"syswright/{item}", filter=tar_filter)
            elif p.is_dir():
                for root, dirs, files in os.walk(p):
                    # Sort for determinism
                    dirs.sort()
                    files.sort()
                    for f in files:
                        fp = Path(root) / f
                        if is_excluded(fp):
                            continue
                        rel_in_repo = fp.relative_to(repo_root)
                        tar.add(fp, arcname=f"syswright/{rel_in_repo}", filter=tar_filter)

    return target_tar


def package_claude_code(repo_root: Path, output_dir: Path) -> Path:
    """Package skills and manifests into Claude Code plugin layout."""
    plugin_dir = output_dir / "claude-code-plugin"
    if plugin_dir.exists():
        shutil.rmtree(plugin_dir)
    plugin_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy .claude-plugin manifests
    manifest_src = repo_root / ".claude-plugin"
    if manifest_src.is_dir():
        for mf in manifest_src.glob("*.json"):
            safe_copy_file(mf, plugin_dir / ".claude-plugin" / mf.name, plugin_dir)

    # 2. Copy skills and references
    for folder in ["skills", "references"]:
        src_folder = repo_root / folder
        if src_folder.is_dir():
            for root, _, files in os.walk(src_folder):
                for f in files:
                    fp = Path(root) / f
                    if is_excluded(fp):
                        continue
                    rel = fp.relative_to(repo_root)
                    safe_copy_file(fp, plugin_dir / rel, plugin_dir)

    return plugin_dir


def package_codex(repo_root: Path, output_dir: Path) -> Path:
    """Package skills into OpenAI Codex layout with AGENTS.md."""
    codex_dir = output_dir / "codex-package"
    if codex_dir.exists():
        shutil.rmtree(codex_dir)
    codex_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy root AGENTS.md
    agents_md = repo_root / "AGENTS.md"
    if agents_md.is_file():
        safe_copy_file(agents_md, codex_dir / "AGENTS.md", codex_dir)

    # 2. Copy skills, references, and codex adapter configs
    for folder in ["skills", "references"]:
        src_folder = repo_root / folder
        if src_folder.is_dir():
            for root, _, files in os.walk(src_folder):
                for f in files:
                    fp = Path(root) / f
                    if is_excluded(fp):
                        continue
                    rel = fp.relative_to(repo_root)
                    safe_copy_file(fp, codex_dir / rel, codex_dir)

    adapter_src = repo_root / "adapters" / "codex"
    if adapter_src.is_dir():
        for root, _, files in os.walk(adapter_src):
            for f in files:
                fp = Path(root) / f
                if is_excluded(fp):
                    continue
                rel = fp.relative_to(adapter_src)
                safe_copy_file(fp, codex_dir / rel, codex_dir)

    return codex_dir


def main():
    parser = argparse.ArgumentParser(description="Deterministic Skill Packager")
    parser.add_argument(
        "--target",
        choices=["archive", "claude-code", "codex", "all"],
        default="archive",
        help="Target packaging distribution",
    )
    parser.add_argument("--output", default="dist", help="Output directory")
    parser.add_argument("--repo-root", default=".", help="Root directory of repository")
    parser.add_argument("--skip-validation", action="store_true", help="Skip pre-packaging validation")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    output_dir = Path(args.output).resolve()

    # Pre-packaging validation gate
    if not args.skip_validation and validate_skill_directory:
        skills = find_all_skills(repo_root)
        print(f"Running pre-packaging validation on {len(skills)} skills...")
        for sdir in skills:
            errs = validate_skill_directory(sdir)
            if errs:
                print(f"[FAIL] Pre-packaging validation failed for {sdir.name}:")
                for e in errs:
                    print(f"  - {e}")
                sys.exit(1)
        print("Pre-packaging validation PASSED.")

    targets = ["archive", "claude-code", "codex"] if args.target == "all" else [args.target]

    for t in targets:
        if t == "archive":
            art = package_archive(repo_root, output_dir)
            print(f"[OK] Packaged archive: {art}")
        elif t == "claude-code":
            art = package_claude_code(repo_root, output_dir)
            print(f"[OK] Packaged Claude Code plugin: {art}")
        elif t == "codex":
            art = package_codex(repo_root, output_dir)
            print(f"[OK] Packaged OpenAI Codex layout: {art}")

    print("SUCCESS: Packaging completed.")


if __name__ == "__main__":
    main()
