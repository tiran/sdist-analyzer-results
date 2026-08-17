#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "packaging>=24.2",
# ]
# ///
# SPDX-License-Identifier: Apache-2.0
"""Analyze METADATA files to find projects without a git hosting URL.

.. note::

   This script was generated with the assistance of Claude (Anthropic).
   Review before relying on its output.

Scans METADATA files from RHOAI wheel data (previously fetched by
``fetch-rhoai-metadata.py``) and checks Home-page and Project-URL
entries for references to known git hosting platforms.  For projects
with multiple versions, the latest version is used.

Usage::

    uv run analyze-git-hosting.py
    uv run analyze-git-hosting.py 3.6-EA1
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import packaging.metadata
from packaging.version import InvalidVersion, Version

DATA_DIR = Path("data")
DEFAULT_VERSION = "3.6-EA1"

# Patterns that indicate a git hosting platform
GIT_HOSTING_PATTERNS = re.compile(
    r"https?://"
    r"(www\.)?"
    r"("
    r"github\.com|"
    r"gitlab\.com|"
    r"gitlab\.[a-z]+\.[a-z]+|"       # self-hosted GitLab instances
    r"bitbucket\.org|"
    r"codeberg\.org|"
    r"sr\.ht|"
    r"sourcehut\.org|"
    r"gitee\.com|"
    r"sourceforge\.net|"
    r"code\.google\.com|"
    r"pagure\.io|"
    r"salsa\.debian\.org|"
    r"framagit\.org|"
    r"git\.savannah\.gnu\.org|"
    r"git\.launchpad\.net|"
    r"code\.launchpad\.net|"
    r"launchpad\.net|"
    r"foss\.heptapod\.net|"           # Heptapod (Mercurial/Git hosting)
    r"opendev\.org"                   # OpenDev (OpenStack Git hosting)
    r")",
    re.IGNORECASE,
)


def _version_key(v: str) -> tuple[int, Version | str]:
    try:
        return (0, Version(v))
    except InvalidVersion:
        return (1, v)


def scan_packages(rhoai_dir: Path) -> dict[str, dict[str, Path]]:
    """Scan RHOAI data for packages with METADATA files.

    Returns ``{name: {version: metadata_path}}``.
    """
    packages: dict[str, dict[str, Path]] = {}
    for index_dir in sorted(rhoai_dir.iterdir()):
        if not index_dir.is_dir():
            continue
        for pkg_dir in index_dir.iterdir():
            if not pkg_dir.is_dir():
                continue
            for ver_dir in pkg_dir.iterdir():
                if not ver_dir.is_dir():
                    continue
                metadata = ver_dir.joinpath("METADATA")
                if metadata.is_file():
                    packages.setdefault(pkg_dir.name, {})[ver_dir.name] = metadata
    return packages


def parse_metadata_urls(
    metadata_path: Path,
) -> tuple[str | None, dict[str, str]]:
    """Parse Home-page and Project-URL from a METADATA file.

    Returns ``(home_page, {label: url})``.
    """
    try:
        raw = metadata_path.read_bytes()
        d, _body = packaging.metadata.parse_email(raw)
    except Exception:
        return None, {}
    home_page = d.get("home_page")
    project_urls = d.get("project_urls") or {}
    return home_page, project_urls


def find_git_hosting(
    home_page: str | None, project_urls: dict[str, str]
) -> set[str]:
    """Return matched git hosting domains from the URLs."""
    platforms: set[str] = set()
    urls = list(project_urls.values())
    if home_page:
        urls.append(home_page)
    for url in urls:
        m = GIT_HOSTING_PATTERNS.search(url)
        if m:
            platforms.add(m.group(2))
    return platforms


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "version",
        nargs="?",
        default=DEFAULT_VERSION,
        help="RHOAI index version (default: %(default)s)",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help="Base data directory (default: %(default)s)",
    )
    args = parser.parse_args()

    rhoai_dir = args.data_dir.joinpath(f"rhoai-{args.version}")
    if not rhoai_dir.is_dir():
        print(f"Error: {rhoai_dir} not found", file=sys.stderr)
        print("Run fetch-rhoai-metadata.py first.", file=sys.stderr)
        sys.exit(1)

    packages = scan_packages(rhoai_dir)

    total = 0
    with_git: list[tuple[str, set[str]]] = []
    without_git: list[tuple[str, str | None, dict[str, str]]] = []

    for name, versions in sorted(packages.items()):
        # Use latest version
        latest = max(versions, key=_version_key)
        metadata_path = versions[latest]

        total += 1
        home_page, project_urls = parse_metadata_urls(metadata_path)
        platforms = find_git_hosting(home_page, project_urls)

        if platforms:
            with_git.append((name, platforms))
        else:
            without_git.append((name, home_page, project_urls))

    # --- Report ---
    out = io.StringIO()
    out.write("=" * 72 + "\n")
    out.write("Projects WITHOUT git hosting URL in Home-page / Project-URL:\n")
    out.write("=" * 72 + "\n")
    for project, home_page, project_urls in without_git:
        urls_info: list[str] = []
        if home_page and home_page.upper() != "UNKNOWN":
            urls_info.append(f"Home-page: {home_page}")
        for label, url in project_urls.items():
            urls_info.append(f"Project-URL: {label}, {url}")
        if urls_info:
            out.write(f"  {project}\n")
            for info in urls_info:
                out.write(f"    {info}\n")
        else:
            out.write(f"  {project}  (no URLs)\n")
    out.write("\n")
    out.write("=" * 72 + "\n")
    out.write("Projects WITH git hosting URL:\n")
    out.write("=" * 72 + "\n")
    # Group projects by platform
    platform_projects: dict[str, list[str]] = defaultdict(list)
    for project, platforms in with_git:
        for p in platforms:
            platform_projects[p].append(project)
    for platform in sorted(platform_projects, key=lambda p: -len(platform_projects[p])):
        projects = sorted(platform_projects[platform])
        out.write(f"  {platform}: {', '.join(projects)}\n")
    out.write("\n")
    out.write("=" * 72 + "\n")
    out.write("Hosting platform usage:\n")
    out.write("=" * 72 + "\n")
    platform_counts: Counter[str] = Counter()
    for _project, platforms in with_git:
        for p in platforms:
            platform_counts[p] += 1
    for platform, count in platform_counts.most_common():
        out.write(f"  {platform:30s} {count:5d}  ({count / total * 100:.1f}%)\n")
    out.write(f"\nTotal projects analyzed: {total}\n")
    out.write(f"Projects WITH git hosting URL: {len(with_git)}\n")
    out.write(f"Projects WITHOUT git hosting URL: {len(without_git)}\n")
    if total > 0:
        out.write(
            f"Percentage without git hosting: "
            f"{len(without_git) / total * 100:.1f}%\n"
        )

    result = out.getvalue()
    print(result)

    dest = rhoai_dir / "git-hosting.txt"
    dest.write_text(result)
    print(f"Wrote {dest}", file=sys.stderr)


if __name__ == "__main__":
    main()
