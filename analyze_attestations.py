#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "packaging",
#     "pypi-simple",
#     "pyyaml",
#     "requests",
#     "tqdm",
# ]
# ///
# SPDX-License-Identifier: Apache-2.0
"""Analyze PyPI digital attestations (PEP 740) for packages in the RHOAI index.

For each project in packages.yaml, checks the latest version on PyPI for
Sigstore-based attestations via the Simple API's provenance_url attribute.
For packages with attestations, fetches the full provenance JSON to extract
publisher details (kind, repository, workflow).
"""

from __future__ import annotations

import argparse
import logging
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

import requests
import yaml
from packaging.version import InvalidVersion, Version
from pypi_simple import ACCEPT_JSON_ONLY, PyPISimple
from tqdm import tqdm

logger = logging.getLogger(__name__)

PYPI_INDEX = "https://pypi.org/simple/"
DATA_DIR = Path("data")
PACKAGES_YAML = "packages.yaml"


def _make_session(workers: int) -> requests.Session:
    """Create a requests session with connection pool sized for workers."""
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=workers, pool_maxsize=workers
    )
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def load_packages_yaml(path: str | Path) -> dict[str, list[str]]:
    """Load packages dict from YAML file."""
    with open(path) as f:
        data = yaml.safe_load(f)
    return data["packages"]


def latest_version(versions: list[str]) -> str:
    """Pick the latest version from a list using PEP 440 sorting."""
    def version_key(v: str) -> tuple[int, Version | str]:
        try:
            return (0, Version(v))
        except InvalidVersion:
            return (1, v)

    return max(versions, key=version_key)


@dataclass
class AttestationResult:
    """Result of checking attestations for a single project."""

    name: str
    version: str
    has_attestation: bool = False
    publisher_kind: str | None = None
    repository: str | None = None
    workflow: str | None = None
    error: str | None = None


def check_attestation(
    client: PyPISimple,
    name: str,
    version: str,
) -> AttestationResult:
    """Check if the latest version of a project has a digital attestation."""
    result = AttestationResult(name=name, version=version)

    # Strip local version suffix for PyPI lookup
    pypi_version = version
    try:
        parsed = Version(version)
        if parsed.local is not None:
            pypi_version = str(parsed.public)
    except InvalidVersion:
        pass

    try:
        page = client.get_project_page(name, timeout=30)
    except Exception as e:
        result.error = f"failed to fetch project page: {e}"
        return result

    # Filter packages matching the target version
    version_pkgs = [
        p for p in page.packages
        if p.version == pypi_version
    ]

    if not version_pkgs:
        result.error = f"no packages found for version {pypi_version}"
        return result

    # Check if any distribution file has a provenance_url
    pkg_with_provenance = None
    for pkg in version_pkgs:
        if pkg.provenance_url is not None:
            pkg_with_provenance = pkg
            break

    if pkg_with_provenance is None:
        return result

    result.has_attestation = True

    # Fetch full provenance JSON to get publisher details
    try:
        provenance = client.get_provenance(pkg_with_provenance, timeout=30)
        _extract_publisher_info(provenance, result)
    except Exception as e:
        logger.debug(
            "Failed to fetch provenance for %s==%s: %s", name, version, e
        )

    return result


def _extract_publisher_info(
    provenance: dict, result: AttestationResult
) -> None:
    """Extract publisher info from the provenance JSON."""
    # PEP 740 provenance format:
    # {
    #   "version": 1,
    #   "attestation_bundles": [
    #     {
    #       "publisher": {"kind": "GitHub", "claims": {...}, ...},
    #       "attestations": [...]
    #     }
    #   ]
    # }
    bundles = provenance.get("attestation_bundles", [])
    if not bundles:
        return

    publisher = bundles[0].get("publisher", {})
    result.publisher_kind = publisher.get("kind")

    claims = publisher.get("claims", {})
    if claims:
        result.repository = claims.get("repository")
        result.workflow = claims.get("workflow")

    # Some provenance formats put repository/workflow at the publisher level
    if result.repository is None:
        result.repository = publisher.get("repository")
    if result.workflow is None:
        result.workflow = publisher.get("workflow")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--packages-yaml",
        default=PACKAGES_YAML,
        help="Path to packages YAML file (default: %(default)s)",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help="Base data directory (default: %(default)s)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=16,
        help="Number of parallel workers (default: %(default)s)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    packages_yaml = args.data_dir / args.packages_yaml
    packages = load_packages_yaml(packages_yaml)
    logger.info("Loaded %d projects from %s", len(packages), packages_yaml)

    # Build tasks: (name, latest_version) for each project
    tasks: list[tuple[str, str]] = []
    for name, versions in packages.items():
        ver = latest_version(versions)
        tasks.append((name, ver))

    session = _make_session(args.workers)
    client = PyPISimple(PYPI_INDEX, session=session, accept=ACCEPT_JSON_ONLY)
    results: list[AttestationResult] = []
    errors: list[str] = []

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(check_attestation, client, name, ver): (name, ver)
            for name, ver in tasks
        }
        with tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Checking attestations",
        ) as pbar:
            for future in pbar:
                name, ver = futures[future]
                try:
                    result = future.result()
                except Exception as e:
                    logger.error(
                        "Unexpected error for %s==%s: %s", name, ver, e
                    )
                    errors.append(f"{name}=={ver}: {e}")
                    continue
                if result.error is not None:
                    logger.debug(
                        "%s==%s: %s", result.name, result.version, result.error
                    )
                results.append(result)

    # --- Report ---
    with_attestation = [r for r in results if r.has_attestation]
    without_attestation = [r for r in results if not r.has_attestation]
    total = len(results)

    print()
    print("=" * 72)
    print("PyPI Digital Attestation (PEP 740) Analysis")
    print("=" * 72)
    print(f"Total projects analyzed: {total}")
    print(f"Projects WITH attestations:    {len(with_attestation)}")
    print(f"Projects WITHOUT attestations: {len(without_attestation)}")
    if total > 0:
        pct = len(with_attestation) / total * 100
        print(f"Attestation coverage: {pct:.1f}%")
    if errors:
        print(f"Errors: {len(errors)}")

    # Publisher kind breakdown
    print()
    print("=" * 72)
    print("Publisher kind breakdown:")
    print("=" * 72)
    kind_counts: Counter[str] = Counter()
    for r in with_attestation:
        kind = r.publisher_kind or "unknown"
        kind_counts[kind] += 1
    for kind, count in kind_counts.most_common():
        print(f"  {kind:30s} {count:5d}  ({count / total * 100:.1f}%)")

    # Projects WITH attestations
    print()
    print("=" * 72)
    print("Projects WITH attestations:")
    print("=" * 72)
    for r in sorted(with_attestation, key=lambda r: r.name.lower()):
        parts = [f"{r.name}=={r.version}"]
        if r.publisher_kind:
            parts.append(f"publisher={r.publisher_kind}")
        if r.repository:
            parts.append(f"repo={r.repository}")
        if r.workflow:
            parts.append(f"workflow={r.workflow}")
        print(f"  {', '.join(parts)}")

    # Projects WITHOUT attestations
    print()
    print("=" * 72)
    print("Projects WITHOUT attestations:")
    print("=" * 72)
    for r in sorted(without_attestation, key=lambda r: r.name.lower()):
        print(f"  {r.name}=={r.version}")

    if errors:
        print()
        print("=" * 72)
        print("Errors:")
        print("=" * 72)
        for e in sorted(errors):
            print(f"  {e}")


if __name__ == "__main__":
    main()
