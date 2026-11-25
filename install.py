#!/usr/bin/env python3
"""Install SysWright skills into every detected supported agent.

The installer is dependency-free, installs only canonical skill directories,
and never removes or overwrites existing content.
"""

import argparse
import shutil
import sys
from pathlib import Path
from typing import Iterable, Optional


class Agent:
    def __init__(self, name: str, label: str, executable: str, config_dir: Path, skill_dir: Path):
        self.name = name
        self.label = label
        self.executable = executable
        self.config_dir = config_dir
        self.skill_dir = skill_dir


def discover_agents(home: Optional[Path] = None, path: Optional[str] = None) -> list:
    """Detect supported agents from their executable or user config directory."""
    home = home or Path.home()
    agents = [
        Agent("claude", "Claude Code", "claude", home / ".claude", home / ".claude" / "skills"),
        Agent("codex", "OpenAI Codex", "codex", home / ".codex", home / ".agents" / "skills"),
    ]
    return [agent for agent in agents
            if shutil.which(agent.executable, path=path) or agent.config_dir.is_dir()]


def find_skills(repo_root: Path) -> list:
    """Find canonical skills and reject symlinks anywhere in their trees."""
    skills_root = repo_root / "skills"
    if not skills_root.is_dir():
        raise FileNotFoundError("No skills/ directory found; run install.py from the SysWright checkout.")
    skills = []
    for candidate in sorted(skills_root.iterdir()):
        if candidate.is_symlink():
            raise ValueError("Refusing symlinked skill directory: {}".format(candidate))
        if not candidate.is_dir() or not (candidate / "SKILL.md").is_file():
            continue
        for entry in candidate.rglob("*"):
            if entry.is_symlink():
                raise ValueError("Refusing symlink inside skill '{}': {}".format(candidate.name, entry))
        skills.append(candidate)
    if not skills:
        raise ValueError("No valid skills containing SKILL.md were found.")
    return skills


def plan_install(skills: Iterable[Path], agents: Iterable[Agent], scope: str,
                 repo_root: Path, cwd: Path) -> list:
    """Resolve the per-agent installation root for user or repository scope."""
    plans = []
    for agent in agents:
        if scope == "repo":
            parent = ".claude" if agent.name == "claude" else ".agents"
            destination = cwd / parent / "skills"
        else:
            destination = agent.skill_dir
        plans.append((agent, destination))
    return plans


def _has_symlink_component(path: Path) -> bool:
    """Check existing path components without resolving through symlinks."""
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        if current.is_symlink():
            return True
    return False


def install(skills: list, plans: list, dry_run: bool = False) -> int:
    """Preflight all targets, then copy; conflicts abort the entire operation."""
    conflicts = []
    for agent, destination in plans:
        if _has_symlink_component(destination):
            conflicts.append("{}: destination path contains a symlink: {}".format(agent.label, destination))
            continue
        if destination.exists() and not destination.is_dir():
            conflicts.append("{}: destination is not a directory: {}".format(agent.label, destination))
            continue
        for skill in skills:
            target = destination / skill.name
            if target.exists() or target.is_symlink():
                conflicts.append("{}: {} already exists".format(agent.label, target))
    if conflicts:
        print("Installation aborted; no files were changed:", file=sys.stderr)
        for conflict in conflicts:
            print("  - " + conflict, file=sys.stderr)
        print("Move conflicting skill directories aside before retrying.", file=sys.stderr)
        return 2

    for agent, destination in plans:
        print("{} -> {}".format(agent.label, destination))
        if dry_run:
            continue
        destination.mkdir(parents=True, exist_ok=True)
        for skill in skills:
            shutil.copytree(skill, destination / skill.name, symlinks=False)
            print("  installed {}".format(skill.name))
    return 0


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Install SysWright skills for all detected supported AI coding agents."
    )
    parser.add_argument("--agent", action="append", choices=("claude", "codex"),
                        help="Install only for this agent (repeatable); default: all detected agents.")
    parser.add_argument("--scope", choices=("user", "repo"), default="user",
                        help="Install for the current user (default) or current working repository.")
    parser.add_argument("--dry-run", action="store_true", help="Show destinations without writing files.")
    parser.add_argument("--list-agents", action="store_true", help="List detected agents and exit.")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent,
                        help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    try:
        skills = find_skills(repo_root)
    except (FileNotFoundError, ValueError) as exc:
        parser.error(str(exc))

    detected = discover_agents()
    if args.list_agents:
        for agent in detected:
            print("{} ({})".format(agent.label, agent.executable))
        if not detected:
            print("No supported agents detected.")
        return 0

    if args.agent:
        home = Path.home()
        supported = {
            "claude": Agent("claude", "Claude Code", "claude", home / ".claude", home / ".claude" / "skills"),
            "codex": Agent("codex", "OpenAI Codex", "codex", home / ".codex", home / ".agents" / "skills"),
        }
        selected = [supported[name] for name in dict.fromkeys(args.agent)]
    else:
        selected = detected

    if not selected:
        print("No supported agents detected. Install Claude Code or Codex, or specify --agent.",
              file=sys.stderr)
        return 1

    plans = plan_install(skills, selected, args.scope, repo_root, Path.cwd())
    print("Found {} SysWright skills; targeting {} agent(s).".format(len(skills), len(plans)))
    if args.dry_run:
        print("Dry run: no files will be changed.")
    return install(skills, plans, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
