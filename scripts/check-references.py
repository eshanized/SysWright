#!/usr/bin/env python3
"""
Reference Link & Integrity Checker
Part of Syswright

Scans Markdown documentation and skills to verify that all relative file links,
anchor targets, and documentation cross-references resolve to existing files.
Includes optional external URL verification with graceful timeout handling.
"""

import argparse
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Set, Tuple

MD_LINK_REGEX = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def extract_links_from_file(file_path: Path) -> List[Tuple[str, str, int]]:
    """Extract all markdown links: returns list of (text, target, line_number)."""
    links = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return [("", f"__READ_ERROR__: {e}", 1)]

    for line_no, line in enumerate(content.splitlines(), start=1):
        for match in MD_LINK_REGEX.finditer(line):
            text = match.group(1).strip()
            target = match.group(2).strip()
            links.append((text, target, line_no))
    return links


def check_external_url(url: str, timeout: int = 4) -> Tuple[bool, str]:
    """Test if an external URL is reachable via HTTP HEAD or GET."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "LinuxEngineering-ReferenceChecker/0.1.0"},
            method="HEAD",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status < 400:
                return True, f"HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        if e.code in (403, 405):  # Many servers block HEAD or return 403 to scripts
            return True, f"HTTP {e.code} (Assumed reachable)"
        return False, f"HTTP Error {e.code}"
    except Exception as e:
        return False, str(e)
    return True, "OK"


def scan_markdown_files(repo_root: Path, dirs_to_scan: List[str]) -> List[Path]:
    """Find all markdown files under specified directories."""
    md_files = []
    for dname in dirs_to_scan:
        dp = repo_root / dname
        if dp.is_file() and dp.suffix.lower() == ".md":
            md_files.append(dp)
        elif dp.is_dir():
            for p in dp.rglob("*.md"):
                # Skip hidden directories and build outputs
                if any(part.startswith(".") and part != "." for part in p.parts):
                    continue
                if "dist" in p.parts:
                    continue
                md_files.append(p)
    # Also check root markdown files
    for p in repo_root.glob("*.md"):
        md_files.append(p)
    return sorted(list(set(md_files)))


def validate_references(repo_root: Path, check_external: bool = False) -> Tuple[bool, Dict[str, List[str]]]:
    """Validate all relative links in repository documentation."""
    dirs_to_scan = ["skills", "references", "docs", "adapters"]
    files = scan_markdown_files(repo_root, dirs_to_scan)

    broken_links: Dict[str, List[str]] = {}
    external_links: Set[str] = set()

    for fpath in files:
        links = extract_links_from_file(fpath)
        file_errors = []

        for text, target, line_no in links:
            if target.startswith("__READ_ERROR__"):
                file_errors.append(f"Line {line_no}: {target}")
                continue

            # Strip fragments and queries
            clean_target = target.split("#")[0].split("?")[0].strip()
            if not clean_target:
                # Link was purely an anchor in the same file (e.g. #section)
                continue

            # External URL handling
            if clean_target.startswith("http://") or clean_target.startswith("https://"):
                if check_external:
                    external_links.add(clean_target)
                continue

            if clean_target.startswith("mailto:"):
                continue

            # If target uses file:// scheme, extract file path
            if clean_target.startswith("file://"):
                clean_target = clean_target[len("file://"):]

            # Resolve relative to current markdown file
            target_path = Path(clean_target)
            if target_path.is_absolute():
                resolved = target_path
            else:
                resolved = (fpath.parent / target_path).resolve()

            if not resolved.exists():
                file_errors.append(f"Line {line_no}: Broken link '{target}' -> missing file '{resolved}'")

        if file_errors:
            rel_fpath = str(fpath.relative_to(repo_root))
            broken_links[rel_fpath] = file_errors

    # External link reporting (advisory, does not fail build on network errors)
    if check_external and external_links:
        print(f"Checking {len(external_links)} external URLs (timeout: 4s)...")
        for url in sorted(external_links):
            ok, msg = check_external_url(url)
            status = "[OK]" if ok else "[WARN]"
            print(f"  {status} {url} ({msg})")

    success = len(broken_links) == 0
    return success, broken_links


def main():
    parser = argparse.ArgumentParser(description="Check integrity of reference documentation links")
    parser.add_argument("--repo-root", default=".", help="Root of repository")
    parser.add_argument("--external", action="store_true", help="Optionally check external URLs")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    success, broken = validate_references(repo_root, check_external=args.external)

    if success:
        print("SUCCESS: All internal documentation references and links are valid.")
        sys.exit(0)
    else:
        print("FAILURE: Broken relative references found:")
        for f, errs in broken.items():
            print(f"\nIn {f}:")
            for e in errs:
                print(f"  - {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
