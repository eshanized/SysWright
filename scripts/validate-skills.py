#!/usr/bin/env python3
"""
Agent Skills Validator (Zero External Dependencies)
Part of Syswright

Validates skill directories against the Agent Skills open specification (agentskills.io).
Checks SKILL.md existence, YAML frontmatter syntax, name/directory matching,
field constraints, and internal relative file reference integrity.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class FrontmatterParseError(Exception):
    """Raised when YAML frontmatter is malformed."""
    pass


def parse_simple_yaml(yaml_text: str) -> Dict[str, Any]:
    """
    Parse a subset of YAML suitable for Agent Skills frontmatter
    using only Python standard library. Handles mappings, scalar strings,
    quoted strings, multiline blocks (| and >), booleans, and 1-level nested maps.
    """
    lines = yaml_text.splitlines()
    data: Dict[str, Any] = {}
    current_key: Optional[str] = None
    multiline_key: Optional[str] = None
    multiline_type: Optional[str] = None
    multiline_lines: List[str] = []
    nested_map_key: Optional[str] = None

    idx = 0
    while idx < len(lines):
        line = lines[idx]
        stripped = line.strip()

        # Handle multiline blocks
        if multiline_key is not None:
            if line.startswith("  ") or not stripped:
                # Continuation of multiline block
                multiline_lines.append(line[2:] if line.startswith("  ") else "")
                idx += 1
                continue
            else:
                # End of multiline block
                joined = "\n".join(multiline_lines)
                if multiline_type == ">":
                    joined = " ".join([l.strip() for l in multiline_lines if l.strip()])
                if nested_map_key:
                    data[nested_map_key][multiline_key] = joined.strip()
                else:
                    data[multiline_key] = joined.strip()
                multiline_key = None
                multiline_type = None
                multiline_lines = []

        # Skip blank lines and full-line comments
        if not stripped or stripped.startswith("#"):
            idx += 1
            continue

        # Check for nested indentation (2 spaces)
        if line.startswith("  ") and not line.startswith("    "):
            if not nested_map_key:
                raise FrontmatterParseError(f"Unexpected indentation at line {idx+1}: {line}")
            subline = line.strip()
            if ":" not in subline:
                raise FrontmatterParseError(f"Malformed nested key-value at line {idx+1}: {line}")
            k, v = subline.split(":", 1)
            k = k.strip()
            v = v.strip()
            if v in ("|", ">"):
                multiline_key = k
                multiline_type = v
                multiline_lines = []
            elif (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                data[nested_map_key][k] = v[1:-1]
            elif v.lower() in ("true", "yes", "on"):
                data[nested_map_key][k] = True
            elif v.lower() in ("false", "no", "off"):
                data[nested_map_key][k] = False
            else:
                data[nested_map_key][k] = v
            idx += 1
            continue

        # Non-indented line -> top-level key
        nested_map_key = None
        if ":" not in line:
            raise FrontmatterParseError(f"Expected key-value pair at line {idx+1}: {line}")

        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip()

        if not v:
            # Could be start of a nested map (e.g. metadata:)
            data[k] = {}
            nested_map_key = k
        elif v in ("|", ">"):
            multiline_key = k
            multiline_type = v
            multiline_lines = []
        elif (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            data[k] = v[1:-1]
        elif v.lower() in ("true", "yes", "on"):
            data[k] = True
        elif v.lower() in ("false", "no", "off"):
            data[k] = False
        else:
            data[k] = v

        idx += 1

    # Finalize any trailing multiline block
    if multiline_key is not None:
        joined = "\n".join(multiline_lines)
        if multiline_type == ">":
            joined = " ".join([l.strip() for l in multiline_lines if l.strip()])
        if nested_map_key:
            data[nested_map_key][multiline_key] = joined.strip()
        else:
            data[multiline_key] = joined.strip()

    return data


def extract_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """Extract YAML frontmatter and body from markdown text."""
    lines = content.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise FrontmatterParseError("SKILL.md must start with '---' on the first line.")

    fm_lines = []
    closing_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            closing_idx = i
            break
        fm_lines.append(lines[i])

    if closing_idx == -1:
        raise FrontmatterParseError("SKILL.md missing closing '---' for frontmatter.")

    yaml_text = "".join(fm_lines)
    body = "".join(lines[closing_idx + 1:])
    parsed = parse_simple_yaml(yaml_text)
    return parsed, body


NAME_REGEX = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ALLOWED_FRONTMATTER_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
MD_LINK_REGEX = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def validate_skill_directory(skill_dir: Path) -> List[str]:
    """
    Validate a single skill directory against Agent Skills spec.
    Returns list of error messages (empty list if valid).
    """
    errors: List[str] = []
    dir_name = skill_dir.name

    if not skill_dir.is_dir():
        return [f"'{skill_dir}' is not a directory."]

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [f"Missing required SKILL.md in {skill_dir}"]

    try:
        content = skill_md.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Failed to read SKILL.md: {e}"]

    try:
        fm, body = extract_frontmatter(content)
    except FrontmatterParseError as e:
        return [f"Frontmatter parse error in {skill_md}: {e}"]

    # Reject unknown top-level fields instead of silently accepting non-standard metadata.
    for field in sorted(set(fm) - ALLOWED_FRONTMATTER_FIELDS):
        errors.append(f"Unsupported frontmatter field: '{field}'")

    # 1. Validate 'name'
    name = fm.get("name")
    if not name:
        errors.append("Missing required frontmatter field: 'name'")
    elif not isinstance(name, str):
        errors.append("'name' field must be a string")
    else:
        if len(name) < 1 or len(name) > 64:
            errors.append(f"'name' length ({len(name)}) must be between 1 and 64 characters")
        if not NAME_REGEX.match(name):
            errors.append(f"'name' '{name}' invalid: must be lowercase alphanumeric and single hyphens only")
        if name != dir_name:
            errors.append(f"'name' '{name}' does not match directory name '{dir_name}'")

    # 2. Validate 'description'
    desc = fm.get("description")
    if not desc:
        errors.append("Missing required frontmatter field: 'description'")
    elif not isinstance(desc, str):
        errors.append("'description' field must be a string")
    else:
        if len(desc) < 1 or len(desc) > 1024:
            errors.append(f"'description' length ({len(desc)}) must be between 1 and 1024 characters")

    # 3. Validate 'compatibility' (optional)
    if "compatibility" in fm:
        compat = fm["compatibility"]
        if not isinstance(compat, str):
            errors.append("'compatibility' field must be a string if present")
        elif len(compat) > 500:
            errors.append(f"'compatibility' length ({len(compat)}) exceeds 500 characters")

    # 4. Validate optional string fields and metadata mapping.
    for field in ("license", "allowed-tools"):
        if field in fm and not isinstance(fm[field], str):
            errors.append(f"'{field}' field must be a string")
    if "metadata" in fm:
        meta = fm["metadata"]
        if not isinstance(meta, dict):
            errors.append("'metadata' field must be a key-value mapping")
        else:
            for mk, mv in meta.items():
                if not isinstance(mk, str) or not isinstance(mv, str):
                    errors.append(f"metadata key '{mk}' and its value must both be strings")

    # 5. Validate internal file references in body
    for match in MD_LINK_REGEX.finditer(body):
        link_target = match.group(2).split("#")[0].strip()
        if not link_target or link_target.startswith("http://") or link_target.startswith("https://") or link_target.startswith("mailto:"):
            continue
        # Resolve target relative to skill_dir
        target_path = (skill_dir / link_target).resolve()
        if not target_path.exists():
            errors.append(f"Broken relative reference in SKILL.md: '{link_target}' (resolved to {target_path})")

    return errors


def find_all_skills(base_dir: Path) -> List[Path]:
    """Find all skill directories containing SKILL.md under base_dir/skills or base_dir."""
    skills_root = base_dir / "skills"
    if skills_root.is_dir():
        dirs = [p for p in skills_root.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()]
        return sorted(dirs)
    return []


def main():
    parser = argparse.ArgumentParser(description="Validate Agent Skills compliance")
    parser.add_argument("skill_dirs", nargs="*", help="Optional skill directory paths to validate")
    parser.add_argument("--repo-root", default=".", help="Root directory of the repository")
    parser.add_argument("--strict-spec", action="store_true", help="Also run upstream skills-ref (must be installed)")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    target_dirs = [Path(p).resolve() for p in args.skill_dirs] if args.skill_dirs else find_all_skills(repo_root)

    if not target_dirs:
        print("No skill directories found to validate.")
        sys.exit(1)

    if args.strict_spec and not shutil.which("skills-ref"):
        parser.error("--strict-spec requires the upstream 'skills-ref' executable on PATH")

    all_passed = True
    seen_names: Set[str] = set()

    print(f"Validating {len(target_dirs)} skill(s)...")
    for sdir in target_dirs:
        errors = validate_skill_directory(sdir)
        if args.strict_spec:
            result = subprocess.run(
                ["skills-ref", "validate", str(sdir)],
                capture_output=True, text=True, check=False,
            )
            if result.returncode:
                detail = (result.stdout + "\\n" + result.stderr).strip()
                errors.append("Upstream skills-ref validation failed" + (f": {detail}" if detail else ""))
        skill_name = sdir.name

        if skill_name in seen_names:
            errors.append(f"Duplicate skill name detected: '{skill_name}'")
        seen_names.add(skill_name)

        if errors:
            all_passed = False
            print(f"\n[FAIL] {sdir.name} ({sdir})")
            for err in errors:
                print(f"  - ERROR: {err}")
        else:
            print(f"[PASS] {sdir.name}")

    if all_passed:
        print(f"\nSUCCESS: All {len(target_dirs)} skills passed validation.")
        sys.exit(0)
    else:
        print("\nFAILURE: One or more validation errors were found.")
        sys.exit(1)


if __name__ == "__main__":
    main()
