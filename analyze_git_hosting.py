#!/usr/bin/env python3
"""Analyze PKG-INFO files to find projects without a git hosting URL.

Checks Home-page and Project-URL metadata entries for references to known
git hosting platforms (GitHub, GitLab, Bitbucket, Codeberg, SourceHut, Gitee,
etc.).  For projects with multiple versions, the latest version (by directory
name, sorted with packaging.version if available, otherwise lexicographically)
is used.
"""

import os
import re
import sys
from collections import Counter
from pathlib import Path

try:
    from packaging.version import Version, InvalidVersion

    def version_key(v):
        try:
            return (0, Version(v))
        except InvalidVersion:
            return (1, v)
except ImportError:
    def version_key(v):
        return v

DATA_DIR = Path("data/pypi")

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


def parse_metadata_header(pkg_info_path):
    """Parse the metadata header fields from a PKG-INFO file.

    Returns (home_page, project_urls) where project_urls is a list of
    (label, url) tuples.
    """
    home_page = None
    project_urls = []

    try:
        with open(pkg_info_path, encoding="utf-8", errors="replace") as f:
            for line in f:
                # Blank line marks start of description body
                if line.strip() == "":
                    break
                if line.startswith("Home-page:"):
                    home_page = line.split(":", 1)[1].strip()
                elif line.startswith("Project-URL:"):
                    value = line.split(":", 1)[1].strip()
                    # Format: "Label, URL"
                    if "," in value:
                        label, url = value.split(",", 1)
                        project_urls.append((label.strip(), url.strip()))
                    else:
                        project_urls.append(("", value))
    except OSError:
        pass

    return home_page, project_urls


def find_git_hosting(home_page, project_urls):
    """Return a set of matched git hosting domains from the URLs."""
    platforms = set()
    urls = [url for _label, url in project_urls]
    if home_page:
        urls.append(home_page)
    for url in urls:
        m = GIT_HOSTING_PATTERNS.search(url)
        if m:
            platforms.add(m.group(2))
    return platforms


def latest_version_dir(project_path):
    """Return the path to the latest version subdirectory."""
    versions = [
        d for d in os.listdir(project_path)
        if os.path.isdir(os.path.join(project_path, d))
    ]
    if not versions:
        return None
    versions.sort(key=version_key)
    return os.path.join(project_path, versions[-1])


def main():
    if not DATA_DIR.is_dir():
        print(f"Error: {DATA_DIR} not found", file=sys.stderr)
        sys.exit(1)

    projects = sorted(
        d for d in os.listdir(DATA_DIR)
        if os.path.isdir(os.path.join(DATA_DIR, d))
    )

    total = 0
    with_git = []
    without_git = []

    for project in projects:
        project_path = os.path.join(DATA_DIR, project)
        ver_dir = latest_version_dir(project_path)
        if ver_dir is None:
            continue

        pkg_info = os.path.join(ver_dir, "PKG-INFO")
        if not os.path.isfile(pkg_info):
            continue

        total += 1
        home_page, project_urls = parse_metadata_header(pkg_info)
        platforms = find_git_hosting(home_page, project_urls)

        if platforms:
            with_git.append((project, platforms))
        else:
            without_git.append((project, home_page, project_urls))

    # --- Report ---
    print(f"Total projects analyzed: {total}")
    print(f"Projects WITH git hosting URL: {len(with_git)}")
    print(f"Projects WITHOUT git hosting URL: {len(without_git)}")
    print(
        f"Percentage without git hosting: "
        f"{len(without_git) / total * 100:.1f}%"
    )
    print()
    print("=" * 72)
    print("Hosting platform usage:")
    print("=" * 72)
    platform_counts = Counter()
    for _project, platforms in with_git:
        for p in platforms:
            platform_counts[p] += 1
    for platform, count in platform_counts.most_common():
        print(f"  {platform:30s} {count:5d}  ({count / total * 100:.1f}%)")
    print()
    print("=" * 72)
    print("Projects WITH git hosting URL:")
    print("=" * 72)
    for project, platforms in with_git:
        print(f"  {project}: {', '.join(sorted(platforms))}")
    print()
    print("=" * 72)
    print("Projects WITHOUT git hosting URL in Home-page / Project-URL:")
    print("=" * 72)
    for project, home_page, project_urls in without_git:
        urls_info = []
        if home_page and home_page.upper() != "UNKNOWN":
            urls_info.append(f"Home-page: {home_page}")
        for label, url in project_urls:
            urls_info.append(f"Project-URL: {label}, {url}")
        if urls_info:
            print(f"  {project}")
            for info in urls_info:
                print(f"    {info}")
        else:
            print(f"  {project}  (no URLs)")


if __name__ == "__main__":
    main()
