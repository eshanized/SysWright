#!/usr/bin/env python3
"""Install SysWright skills into every detected supported agent.

The installer is intentionally dependency-free and only manages the named
SysWright skill directories. It never removes or overwrites existing content.
"""

import argparse
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


@dataclass(frozen=True)
class Agent:
    name: str
    label: str
    executable: str
    config_dir: Path
    skill_dir: Path


def discover_agents(home: Optional[Path] = None, path: Optional[str] = None) -> list:
    """Return supported agents detected from executable or user config presence."""
    home = home or Path.home()
    agents = [
        Agent("claude", "Claude Code", "claude", home / ".claude", home / ".claude" / "skills"),
        Agent("codex", "OpenAI Codex", "codex", home / ".codex", home / ".agents" / "skills"),
    ]
    found = []
    for agent in agents:
        if shutil.which(agent.executable, path=path) or agent.config_dir.is_dir():
            found.append(agent)
    return found


def find_skills(repo_root: Path) -> list:
    skills_root = repo_root / "skills"
    if not skills_root.is_dir():
        raise FileNotFoundError("No skills/ directory found; run install.py from the SysWright checkout.")
    skills = []
    for candidate in sorted(skills_root.iterdir()):
        if candidate.is_symlink():
            raise ValueError("Refusing symlinked skill directory: {}".format(candidate))
        if candidate.is_dir() and (candidate / "SKILL.md").is_file():
            skills.append(candidate)
    if not skills:
        raise ValueError("No valid skills containing SKILL.md were found.")
    return skills


def plan_install(skills: Iterable[Path], agents: Iterable[Agent], scope: str,
                 repo_root: Path, cwd: Path) -> list:
    plans = []
    for agent in agents:
        if scope == "repo":
            if agent.name == "claude":
                destination = cwd / ".claude" / "skills"
            else:
                destination = cwd / ".agents" / "skills"
        else:
            destination = agent.skill_dir
        plans.append((agent, destination))
    return plans


def install(skills: list, plans: list, dry_run: bool = False) -> int:
    """Preflight every destination, then copy; existing skills are never overwritten."""
    conflicts = []
    for agent, destination in plans:
        if destination.exists() and (destination.is_symlink() or not destination.is_dir()):
            conflicts.append("{}: destination is not a real directory: {}".format(agent.label, destination))
            continue
        for skill in skills:
            target = destination / skill.name
            if target.exists() or target.is_symlink():
                conflicts.append("{}: {} already exists".format(agent.label, target))
    if conflicts:
        print("Installation aborted; no files were changed:", file=sys.stderr)
        for conflict in conflicts:
            print("  - " + conflict, file=sys.stderr)
        print("Move the conflicting skill directories aside before retrying.", file=sys.stderr)
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
        if detected:
            for agent in detected:
                print("{} ({})".format(agent.label, agent.executable))
        else:
            print("No supported agents detected.")
        return 0

    if args.agent:
        by_name = {agent.name: agent for agent in (
            Agent("claude", "Claude Code", "claude", Path.home() / ".claude",
                  Path.home() / ".claude" / "skills"),
            Agent("codex", "OpenAI Codex", "codex", Path.home() / ".codex",
                  Path.home() / ".agents" / "skills"),
        )}
        selected = [by_name[name] for name in args.agent]
    else:
        selected = detected

    if not selected:
        print("No supported agents detected. Install Claude Code or Codex, or use --agent.", file=sys.stderr)
        return 1

    plans = plan_install(skills, selected, args.scope, repo_root, Path.cwd())
    print("Found {} SysWright skills; targeting {} agent(s).".format(len(skills), len(plans)))
    if args.dry_run:
        print("Dry run: no files will be changed.")
    return install(skills, plans, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
