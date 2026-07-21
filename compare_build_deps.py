#!/usr/bin/env python3
"""Compare fromager build-system-requirements with pyproject.toml build-system.requires.

Iterates over all rhoai-3.5-cpu-ubi9-test packages and compares the fromager
build-system-requirements.txt (from Red Hat wheels) with the build-system.requires
from the corresponding PyPI sdist pyproject.toml.

Reports:
  - EXTRA: deps in fromager but not in pyproject.toml
  - MISSING: deps in pyproject.toml but not in fromager
"""

import sys
import tomllib
from collections import defaultdict
from pathlib import Path

from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name

BASE = Path(__file__).resolve().parent / "data"
RHOAI = BASE / "rhoai-3.5-cpu-ubi9-test"
PYPI = BASE / "pypi"


def parse_fromager(path: Path) -> set[str]:
    """Parse fromager-build-system-requirements.txt and return canonicalized names."""
    names = set()
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            req = Requirement(line)
            names.add(canonicalize_name(req.name))
        except InvalidRequirement:
            print(f"  WARNING: could not parse fromager line: {line!r}", file=sys.stderr)
    return names


def parse_pyproject_build_requires(path: Path) -> set[str] | None:
    """Parse build-system.requires from pyproject.toml.

    Returns None if pyproject.toml does not exist, has no build-system table,
    or has no requires key.
    """
    if not path.exists():
        return None
    try:
        data = tomllib.loads(path.read_text())
    except Exception as e:
        print(f"  WARNING: could not parse {path}: {e}", file=sys.stderr)
        return None

    build_system = data.get("build-system")
    if build_system is None:
        return None
    requires = build_system.get("requires")
    if requires is None:
        return None

    names = set()
    for req_str in requires:
        try:
            req = Requirement(req_str)
            names.add(canonicalize_name(req.name))
        except InvalidRequirement:
            print(
                f"  WARNING: could not parse pyproject.toml requirement: {req_str!r}",
                file=sys.stderr,
            )
    return names


def main():
    # Collect all fromager files
    fromager_files = sorted(RHOAI.glob("*/*/fromager-build-system-requirements.txt"))
    print(f"Found {len(fromager_files)} fromager-build-system-requirements.txt files\n")

    # extra_deps[dep_name] = list of (pkg, version)
    extra_deps: dict[str, list[tuple[str, str]]] = defaultdict(list)
    # missing_deps[dep_name] = list of (pkg, version)
    missing_deps: dict[str, list[tuple[str, str]]] = defaultdict(list)

    skipped_no_pyproject = 0
    skipped_no_build_system = 0
    compared = 0
    identical = 0

    for fromager_path in fromager_files:
        version = fromager_path.parent.name
        name = fromager_path.parent.parent.name

        pyproject_path = PYPI / name / version / "pyproject.toml"

        if not pyproject_path.exists():
            skipped_no_pyproject += 1
            continue

        pypi_names = parse_pyproject_build_requires(pyproject_path)
        if pypi_names is None:
            skipped_no_build_system += 1
            continue

        fromager_names = parse_fromager(fromager_path)
        compared += 1

        extra = fromager_names - pypi_names
        missing = pypi_names - fromager_names

        if not extra and not missing:
            identical += 1
            continue

        for dep in extra:
            extra_deps[dep].append((name, version))
        for dep in missing:
            missing_deps[dep].append((name, version))

    # Print summary stats
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total fromager files:                  {len(fromager_files)}")
    print(f"Skipped (no pyproject.toml in pypi):   {skipped_no_pyproject}")
    print(f"Skipped (no build-system.requires):    {skipped_no_build_system}")
    print(f"Compared:                              {compared}")
    print(f"Identical:                             {identical}")
    print(f"With differences:                      {compared - identical}")
    print()

    # Print EXTRA deps (in fromager but not in pyproject.toml)
    print("=" * 80)
    print("EXTRA DEPS (in fromager but NOT in pyproject.toml build-system.requires)")
    print("=" * 80)
    if not extra_deps:
        print("  (none)")
    else:
        for dep_name in sorted(extra_deps.keys()):
            pkgs = sorted(extra_deps[dep_name])
            print(f"\n  {dep_name}  ({len(pkgs)} package-versions affected):")
            for pkg, ver in pkgs:
                print(f"    - {pkg}/{ver}")

    print()

    # Print MISSING deps (in pyproject.toml but not in fromager)
    print("=" * 80)
    print("MISSING DEPS (in pyproject.toml build-system.requires but NOT in fromager)")
    print("=" * 80)
    if not missing_deps:
        print("  (none)")
    else:
        for dep_name in sorted(missing_deps.keys()):
            pkgs = sorted(missing_deps[dep_name])
            print(f"\n  {dep_name}  ({len(pkgs)} package-versions affected):")
            for pkg, ver in pkgs:
                print(f"    - {pkg}/{ver}")


if __name__ == "__main__":
    main()
