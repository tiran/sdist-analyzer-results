#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "packaging",
#     "pypi-attestations",
#     "pypi-simple",
#     "pyyaml",
#     "requests",
#     "tqdm",
# ]
# ///
# SPDX-License-Identifier: Apache-2.0
"""Analyze PyPI digital attestations (PEP 740) for RHOAI packages.

.. note::

   This script was generated with the assistance of Claude (Anthropic).
   Review before relying on its output.

Scans local PyPI data (previously fetched by ``fetch-pypi-sdists.py``)
to discover package names, then checks the latest version of each on
PyPI for Sigstore-based attestations via the Simple API's provenance_url
attribute.  Writes results to ``data/pypi/pypi-attestations.yaml``.

Usage::

    uv run analyze-attestations.py
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
import pypi_attestations
from packaging.version import InvalidVersion, Version
from pypi_simple import ACCEPT_JSON_ONLY, PyPISimple
from tqdm import tqdm

logger = logging.getLogger(__name__)

PYPI_INDEX = "https://pypi.org/simple/"
DATA_DIR = Path("data")


def _make_session(workers: int) -> requests.Session:
    """Create a requests session with connection pool sized for workers."""
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=workers, pool_maxsize=workers
    )
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def scan_local_packages(pypi_dir: Path) -> dict[str, list[str]]:
    """Scan local PyPI data directory for package names and versions."""
    packages: dict[str, set[str]] = {}
    for pkg_dir in sorted(pypi_dir.iterdir()):
        if not pkg_dir.is_dir():
            continue
        for ver_dir in pkg_dir.iterdir():
            if not ver_dir.is_dir():
                continue
            packages.setdefault(pkg_dir.name, set()).add(ver_dir.name)
    return {name: sorted(versions) for name, versions in sorted(packages.items())}


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
    ref: str | None = None
    commit: str | None = None
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
    provenance_dict: dict, result: AttestationResult
) -> None:
    """Extract publisher info from a PEP 740 provenance dict.

    Uses pypi_attestations to parse the provenance model and decode
    Fulcio certificate claims (ref, commit) from the Sigstore bundle.
    """
    prov = pypi_attestations.Provenance.model_validate(provenance_dict)
    if not prov.attestation_bundles:
        return

    bundle = prov.attestation_bundles[0]
    publisher = bundle.publisher
    result.publisher_kind = publisher.kind

    if hasattr(publisher, "repository"):
        result.repository = publisher.repository
    if hasattr(publisher, "workflow"):
        result.workflow = publisher.workflow

    # Extract ref and commit from Fulcio certificate claims
    if not bundle.attestations:
        return
    try:
        claims = bundle.attestations[0].certificate_claims
        # Fulcio OIDs: https://github.com/sigstore/fulcio/blob/main/docs/oid-info.md
        result.commit = claims.get("1.3.6.1.4.1.57264.1.13")  # source repo digest
        result.ref = claims.get("1.3.6.1.4.1.57264.1.14")     # source repo ref
    except Exception:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
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

    pypi_dir = args.data_dir / "pypi"
    if not pypi_dir.is_dir():
        logger.error("No local data at %s", pypi_dir)
        logger.error("Run fetch-pypi-sdists.py first.")
        return

    packages = scan_local_packages(pypi_dir)
    logger.info("Found %d projects in %s", len(packages), pypi_dir)

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

    # --- Build output ---
    with_attestation = [r for r in results if r.has_attestation]
    without_attestation = [r for r in results if not r.has_attestation]
    total = len(results)

    kind_counts: Counter[str] = Counter()
    attested: dict[str, dict[str, str | None]] = {}
    for r in sorted(with_attestation, key=lambda r: r.name.lower()):
        kind = r.publisher_kind or "unknown"
        kind_counts[kind] += 1
        entry: dict[str, str | None] = {"version": r.version}
        if r.publisher_kind:
            entry["publisher"] = r.publisher_kind
        if r.repository:
            entry["repository"] = r.repository
        if r.workflow:
            entry["workflow"] = r.workflow
        if r.ref:
            entry["ref"] = r.ref
        if r.commit:
            entry["commit"] = r.commit
        attested[r.name] = entry

    not_attested = {
        r.name: r.version
        for r in sorted(without_attestation, key=lambda r: r.name.lower())
    }

    output = {
        "note": "Only the latest version of each package was checked.",
        "summary": {
            "total": total,
            "with_attestation": len(with_attestation),
            "without_attestation": len(without_attestation),
            "coverage_pct": round(len(with_attestation) / total * 100, 1) if total else 0,
            "publisher_kinds": dict(kind_counts.most_common()),
        },
        "with_attestation": attested,
        "without_attestation": not_attested,
    }
    if errors:
        output["errors"] = sorted(errors)

    dest = args.data_dir / "pypi-attestations.yaml"
    with open(dest, "w") as f:
        yaml.dump(output, f, default_flow_style=False, sort_keys=False)

    logger.info("Wrote %s", dest)
    logger.info(
        "Total: %d, with attestation: %d (%.1f%%), without: %d",
        total,
        len(with_attestation),
        len(with_attestation) / total * 100 if total else 0,
        len(without_attestation),
    )


if __name__ == "__main__":
    main()
