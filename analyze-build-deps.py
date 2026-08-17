#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "packaging",
#     "pyyaml",
# ]
# ///
# SPDX-License-Identifier: Apache-2.0
"""Analyze build dependencies from fromager metadata.

.. note::

   This script was generated with the assistance of Claude (Anthropic).
   Review before relying on its output.

Scans fromager-build-system-requirements.txt and
fromager-build-backend-requirements.txt from RHOAI wheel data and
produces a ranked summary of build dependency usage.

Writes:
  - ``build-deps.txt`` -- human-readable ranked summary
  - ``build-deps.yaml`` -- all unique build requirements with
    normalized constraints and list of dependent packages

Usage::

    uv run analyze-build-deps.py
    uv run analyze-build-deps.py 3.6-EA1
"""

from __future__ import annotations

import argparse
import io
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml
from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name, canonicalize_version

DATA_DIR = Path("data")
DEFAULT_VERSION = "3.6-EA1"

FROMAGER_FILES = {
    "fromager-build-system-requirements.txt",
    "fromager-build-backend-requirements.txt",
}


def _parse_requirements(path: Path) -> list[Requirement]:
    """Parse requirements from a requirements file."""
    reqs: list[Requirement] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            reqs.append(Requirement(line))
        except InvalidRequirement:
            pass
    return reqs


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "version",
        nargs="?",
        default=DEFAULT_VERSION,
        help="RHOAI index version (default: %(default)s)",
    )
    ap.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help="Base data directory (default: %(default)s)",
    )
    args = ap.parse_args()

    rhoai_dir = args.data_dir / f"rhoai-{args.version}"
    if not rhoai_dir.is_dir():
        print(f"Error: {rhoai_dir} not found", file=sys.stderr)
        print("Run fetch-rhoai-metadata.py first.", file=sys.stderr)
        sys.exit(1)

    # dep_name -> {constraint_str: set of packages}
    dep_constraints: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: defaultdict(set)
    )
    all_packages: set[str] = set()

    for fromager_file in FROMAGER_FILES:
        for path in sorted(rhoai_dir.rglob(fromager_file)):
            ver_dir = path.parent
            pkg_dir = ver_dir.parent
            if pkg_dir == rhoai_dir or pkg_dir.parent == rhoai_dir:
                continue
            package = pkg_dir.name
            all_packages.add(package)
            for req in _parse_requirements(path):
                name = canonicalize_name(req.name)
                # Normalize the constraint: name + specifier + extras
                constraint = str(req)
                dep_constraints[name][constraint].add(package)

    # Build per-dep package sets (deduplicated across constraints)
    dep_packages: dict[str, set[str]] = {}
    for dep, constraints in dep_constraints.items():
        pkgs: set[str] = set()
        for users in constraints.values():
            pkgs.update(users)
        dep_packages[dep] = pkgs

    ranked = sorted(dep_packages.items(), key=lambda kv: (-len(kv[1]), kv[0]))

    # --- Text summary ---
    out = io.StringIO()
    out.write(f"Total unique packages: {len(all_packages)}\n")
    out.write(f"Total unique build dependencies: {len(ranked)}\n\n")

    out.write("Top build dependencies by usage count:\n")
    for dep, packages in ranked:
        out.write(f"  {len(packages):4d}x  {dep}\n")

    small_deps = [(dep, pkgs) for dep, pkgs in ranked if len(pkgs) <= 5]
    out.write(
        f"\nBuild dependencies with <= 5 dependents"
        f" ({len(small_deps)} of {len(ranked)}):\n"
    )
    for dep, packages in small_deps:
        pkg_list = ", ".join(sorted(packages))
        out.write(f"  {dep} ({len(packages)}): {pkg_list}\n")

    result = out.getvalue()
    print(result)

    txt_dest = rhoai_dir / "build-deps.txt"
    txt_dest.write_text(result)
    print(f"Wrote {txt_dest}", file=sys.stderr)

    # --- YAML with constraints ---
    yaml_data: dict[str, dict] = {}
    for dep, _packages in ranked:
        constraints = dep_constraints[dep]
        yaml_data[dep] = {
            "count": len(dep_packages[dep]),
            "constraints": sorted(constraints),
        }

    yaml_dest = rhoai_dir / "build-deps.yaml"
    with open(yaml_dest, "w") as f:
        yaml.dump(
            yaml_data, f, default_flow_style=False, sort_keys=False, width=120
        )
    print(f"Wrote {yaml_dest}", file=sys.stderr)

    # --- Normalized YAML (assuming latest versions) ---
    # Drop >= and > lower bounds (latest always satisfies them),
    # drop markers (environment-specific).  Keep <, <=, !=, ==, ~=
    # as effective constraints.
    norm_data: dict[str, dict] = {}
    for dep, _packages in ranked:
        constraints = dep_constraints[dep]
        # Map each raw constraint to its effective (normalized) form,
        # then count how many packages use each effective constraint.
        eff_counts: Counter[str] = Counter()
        for constraint_str, users in constraints.items():
            try:
                req = Requirement(constraint_str)
            except InvalidRequirement:
                eff_counts[constraint_str] += len(users)
                continue
            # Keep only upper bounds, exclusions, and pins.
            # Normalize versions with canonicalize_version so
            # <81 and <81.0.0 are deduplicated.
            kept = []
            for spec in req.specifier:
                if spec.operator in ("<", "<=", "!=", "==", "~="):
                    nver = canonicalize_version(spec.version)
                    kept.append(f"{spec.operator}{nver}")
            name = canonicalize_name(req.name)
            key = f"{name}{','.join(sorted(kept))}" if kept else name
            eff_counts[key] += len(users)
        norm_data[dep] = {
            "count": len(dep_packages[dep]),
            "constraints": dict(eff_counts.most_common()),
        }

    norm_dest = rhoai_dir / "build-deps-effective.yaml"
    with open(norm_dest, "w") as f:
        yaml.dump(
            norm_data, f, default_flow_style=False, sort_keys=False, width=120
        )
    print(f"Wrote {norm_dest}", file=sys.stderr)


if __name__ == "__main__":
    main()
