#!/usr/bin/env python3
"""Build safe, reproducible SysWright distribution artifacts."""

import argparse
import gzip
import importlib.util
import os
import shutil
import stat
import sys
import tarfile
import tempfile
from pathlib import Path

val_script = Path(__file__).with_name("validate-skills.py")
spec = importlib.util.spec_from_file_location("validate_skills", val_script)
val_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(val_mod)
find_all_skills = val_mod.find_all_skills
validate_skill_directory = val_mod.validate_skill_directory

EXCLUDE_NAMES = {
    ".git", ".github", ".gitignore", ".DS_Store", "__pycache__",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", ".coverage",
    "node_modules", ".venv", "venv",
}
SECRET_NAMES = {
    ".env", ".env.local", ".env.production", ".npmrc", ".pypirc",
    "id_rsa", "id_ed25519", "credentials",
}
SECRET_SUFFIXES = {".pem", ".p12", ".pfx", ".key"}


def is_excluded(path: Path) -> bool:
    """Return whether a repository-relative path is intentionally excluded."""
    for part in path.parts:
        if part in EXCLUDE_NAMES or part in SECRET_NAMES:
            return True
        if part.startswith(".env.") or part.endswith((".pyc", ".swp", ".tmp")):
            return True
        if Path(part).suffix.lower() in SECRET_SUFFIXES:
            return True
    return False


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _validate_source(src: Path, base_src: Path) -> Path:
    """Reject symlinks, special files, and source paths outside the repository."""
    base = base_src.resolve(strict=True)
    if src.is_symlink():
        raise ValueError(f"Refusing to package symlink: {src}")
    resolved = src.resolve(strict=True)
    if not _inside(resolved, base):
        raise ValueError(f"Source escapes repository root: {src}")
    current = src
    while current != base_src and current != current.parent:
        if current.is_symlink():
            raise ValueError(f"Refusing symlinked source path: {current}")
        current = current.parent
    if not stat.S_ISREG(src.stat().st_mode):
        raise ValueError(f"Refusing non-regular source file: {src}")
    return resolved


def safe_copy_file(src: Path, dst: Path, base_dst: Path, base_src: Path | None = None) -> None:
    """Copy a regular repository file without following source or destination symlinks."""
    if base_src is None:
        base_src = src.parent
    _validate_source(src, base_src)
    base = base_dst.resolve(strict=True)
    parent = dst.parent
    parent.mkdir(parents=True, exist_ok=True)
    if dst.is_symlink() or parent.is_symlink():
        raise ValueError(f"Refusing symlinked destination: {dst}")
    destination = dst.resolve(strict=False)
    if not _inside(destination, base):
        raise ValueError(f"Destination escapes output directory: {dst}")
    shutil.copy2(src, dst, follow_symlinks=False)


def _iter_source_files(root: Path, repo_root: Path):
    """Yield sorted regular files, rejecting every encountered symlink."""
    if root.is_symlink():
        raise ValueError(f"Refusing symlinked package root: {root}")
    if not root.exists():
        return
    if root.is_file():
        _validate_source(root, repo_root)
        if not is_excluded(root.relative_to(repo_root)):
            yield root
        return
    if not root.is_dir():
        raise ValueError(f"Unsupported package input: {root}")

    for current, dirs, files in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        kept_dirs = []
        for name in sorted(dirs):
            candidate = current_path / name
            if is_excluded(candidate.relative_to(repo_root)):
                continue
            if candidate.is_symlink():
                raise ValueError(f"Refusing symlinked directory: {candidate}")
            if not candidate.is_dir():
                raise ValueError(f"Unsupported directory entry: {candidate}")
            kept_dirs.append(name)
        dirs[:] = kept_dirs
        for name in sorted(files):
            candidate = current_path / name
            if is_excluded(candidate.relative_to(repo_root)):
                continue
            _validate_source(candidate, repo_root)
            yield candidate


def _source_date_epoch() -> int:
    value = os.environ.get("SOURCE_DATE_EPOCH", "0")
    try:
        epoch = int(value)
    except ValueError as exc:
        raise ValueError("SOURCE_DATE_EPOCH must be a non-negative integer") from exc
    if epoch < 0:
        raise ValueError("SOURCE_DATE_EPOCH must be a non-negative integer")
    return epoch


def package_archive(repo_root: Path, output_dir: Path, version: str = "0.1.0") -> Path:
    """Create a byte-for-byte reproducible gzip-compressed tar archive."""
    repo_root = repo_root.resolve(strict=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"syswright-{version}.tar.gz"
    mtime = _source_date_epoch()
    items = ["skills", "references", "docs", "adapters", ".claude-plugin", "AGENTS.md"]

    with target.open("xb") as raw:
        # Explicit gzip metadata avoids the wall-clock timestamp written by w:gz.
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=mtime, compresslevel=9) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as archive:
                for item in sorted(items):
                    source = repo_root / item
                    if not source.exists() and not source.is_symlink():
                        continue
                    for file_path in _iter_source_files(source, repo_root):
                        relative = file_path.relative_to(repo_root).as_posix()
                        info = archive.gettarinfo(str(file_path), arcname=f"syswright/{relative}")
                        info.uid = info.gid = 0
                        info.uname = info.gname = "root"
                        info.mtime = mtime
                        info.mode = 0o755 if file_path.stat().st_mode & 0o111 else 0o644
                        with file_path.open("rb") as stream:
                            archive.addfile(info, stream)
    return target


def _copy_tree_files(source_root: Path, destination_root: Path, repo_root: Path) -> None:
    if not source_root.exists() and not source_root.is_symlink():
        return
    for source in _iter_source_files(source_root, repo_root):
        relative = source.relative_to(source_root)
        safe_copy_file(source, destination_root / relative, destination_root, repo_root)


def _new_output_directory(path: Path) -> Path:
    """Create a fresh artifact directory; never recursively delete user data."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.mkdir(exist_ok=False)
    return path


def package_claude_code(repo_root: Path, output_dir: Path) -> Path:
    """Create a Claude Code plugin directory without destructive replacement."""
    repo_root = repo_root.resolve(strict=True)
    plugin_dir = _new_output_directory(output_dir / "claude-code-plugin")
    manifest_src = repo_root / ".claude-plugin"
    _copy_tree_files(manifest_src, plugin_dir / ".claude-plugin", repo_root)
    for folder in ("skills", "references"):
        _copy_tree_files(repo_root / folder, plugin_dir / folder, repo_root)
    return plugin_dir


def package_codex(repo_root: Path, output_dir: Path) -> Path:
    """Create a Codex bundle with skills at the documented .agents/skills path."""
    repo_root = repo_root.resolve(strict=True)
    codex_dir = _new_output_directory(output_dir / "codex-package")

    agents_md = repo_root / "AGENTS.md"
    if agents_md.exists():
        safe_copy_file(agents_md, codex_dir / "AGENTS.md", codex_dir, repo_root)

    skills_root = repo_root / "skills"
    if skills_root.is_dir():
        for skill_dir in sorted(skills_root.iterdir()):
            if skill_dir.is_symlink():
                raise ValueError(f"Refusing symlinked skill directory: {skill_dir}")
            if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").is_file():
                continue
            destination = codex_dir / ".agents" / "skills" / skill_dir.name
            _copy_tree_files(skill_dir, destination, repo_root)

    references = repo_root / "references"
    _copy_tree_files(references, codex_dir / "references", repo_root)
    return codex_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Safe SysWright skill packager")
    parser.add_argument("--target", choices=["archive", "claude-code", "codex", "all"], default="archive")
    parser.add_argument("--output", default="dist")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--skip-validation", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve(strict=True)
    output_dir = Path(args.output).resolve()
    if not args.skip_validation:
        skills = find_all_skills(repo_root)
        if not skills:
            parser.error(f"No skills found under {repo_root / 'skills'}")
        failures = []
        for skill in skills:
            errors = validate_skill_directory(skill)
            if errors:
                failures.extend(f"{skill.name}: {error}" for error in errors)
        if failures:
            print("Pre-packaging validation failed:", file=sys.stderr)
            print("\n".join(f"  - {error}" for error in failures), file=sys.stderr)
            return 1

    targets = ["archive", "claude-code", "codex"] if args.target == "all" else [args.target]
    try:
        for target in targets:
            if target == "archive":
                artifact = package_archive(repo_root, output_dir)
            elif target == "claude-code":
                artifact = package_claude_code(repo_root, output_dir)
            else:
                artifact = package_codex(repo_root, output_dir)
            print(f"[OK] {target}: {artifact}")
    except (OSError, ValueError, tarfile.TarError) as exc:
        print(f"[FAIL] Packaging aborted: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
