#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "packaging",
#     "pypi-simple",
#     "pyyaml",
#     "requests",
#     "tqdm",
#     "zipwire[requests]>=0.3.0",
# ]
# ///
# SPDX-License-Identifier: Apache-2.0
"""Fetch wheel metadata from a Red Hat PyPI index.

Uses pypi_simple to enumerate wheels from a Pulp simple index, then uses
zipwire to extract METADATA and fromager requirements files from each wheel's
dist-info directory into data/rhoai-3.5-cpu-ubi9-test/<name>/<version>/.

Optimized for re-runs: skips packages whose output directory already exists.
"""

from __future__ import annotations

import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
import yaml
from packaging.requirements import InvalidRequirement, Requirement
from pypi_simple import PyPISimple
from tqdm import tqdm
from zipwire import SyncRemoteWheel
from zipwire.backends import RequestsReader

logger = logging.getLogger(__name__)

RHAI_INDEX = (
    "https://packages.redhat.com/api/pypi/public-rhai/"
    "rhoai/3.5/cpu-ubi9-test/simple/"
)

EXTRACT_FILENAMES = {
    "METADATA",
    "fromager-build-backend-requirements.txt",
    "fromager-build-sdist-requirements.txt",
    "fromager-build-system-requirements.txt",
    "fromager-elf-requires.txt",
    "fromager-elf-provides.txt",
}

DATA_DIR = Path("data")
WHEEL_SUBDIR = "rhoai-3.5-cpu-ubi9-test"
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


def get_wheels_from_index(
    index_url: str, workers: int = 16
) -> dict[str, dict[str, str]]:
    """Get all wheels from the index.

    Returns {name: {version: wheel_url}}.
    """
    client = PyPISimple(index_url)
    project_names = list(client.stream_project_names(timeout=60))
    logger.info("Found %d projects in index", len(project_names))

    result: dict[str, dict[str, str]] = {}

    def _fetch(name: str) -> tuple[str, dict[str, str]]:
        page = client.get_project_page(name, timeout=30)
        versions: dict[str, str] = {}
        for pkg in page.packages:
            if pkg.package_type == "wheel" and pkg.version is not None:
                # keep first wheel per version
                if pkg.version not in versions:
                    versions[pkg.version] = pkg.url
        return name, versions

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(_fetch, name): name for name in project_names
        }
        with tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Fetching versions",
        ) as pbar:
            for future in pbar:
                name = futures[future]
                try:
                    name, versions = future.result()
                except Exception as e:
                    logger.warning("Failed to fetch %s: %s", name, e)
                    continue
                if versions:
                    result[name] = versions

    return result


def dump_packages_yaml(
    wheels: dict[str, dict[str, str]], path: Path
) -> None:
    """Write packages dict to YAML file (name: [versions])."""
    packages: dict[str, list[str]] = {
        name: sorted(versions) for name, versions in wheels.items()
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(
            {"packages": packages},
            f,
            default_flow_style=False,
            sort_keys=True,
        )
    logger.info("Wrote %d packages to %s", len(packages), path)


def fetch_wheel_metadata(
    name: str,
    version: str,
    wheel_url: str,
    dest_dir: Path,
    session: requests.Session,
) -> str | None:
    """Extract metadata files from a wheel using zipwire range requests.

    Returns an error string, or None on success.
    """
    dest = dest_dir / name / version
    if dest.is_dir():
        return None  # already done

    reader = RequestsReader(wheel_url, session=session)
    try:
        with SyncRemoteWheel(reader) as whl:
            extracted: dict[str, bytes] = {}
            for entry in whl.distinfolist():
                basename = entry.filename.rsplit("/", 1)[-1]
                if basename in EXTRACT_FILENAMES and entry.file_size > 0:
                    extracted[basename] = whl.read(entry)
    except Exception as e:
        logger.warning("Failed to read %s==%s: %s", name, version, e)
        return f"{name}=={version}: {e}"

    if not extracted:
        logger.warning("No metadata files found in %s==%s", name, version)
        return f"{name}=={version}: no metadata files"

    dest.mkdir(parents=True, exist_ok=True)
    for filename, data in extracted.items():
        (dest / filename).write_bytes(data)

    logger.debug(
        "Extracted %s==%s: %s", name, version, list(extracted.keys())
    )
    return None


def _parse_req_names(text: str) -> set[str]:
    """Parse requirement names from a requirements file, ignoring
    version constraints and optional (extras) requirements."""
    names: set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            req = Requirement(line)
        except InvalidRequirement:
            logger.warning("Invalid requirement: %s", line)
            continue
        # Skip optional/conditional requirements
        if req.marker is not None:
            continue
        names.add(req.name.lower())
    return names


def compare_build_requirements(dest_dir: Path) -> dict[str, dict[str, list[str]]]:
    """Compare backend vs build-system requirements across all packages.

    Returns {name: {version: [extra_packages]}} for packages where
    fromager-build-backend-requirements.txt has additional packages
    not in fromager-build-system-requirements.txt.
    """
    result: dict[str, dict[str, list[str]]] = {}

    for pkg_dir in sorted(dest_dir.iterdir()):
        if not pkg_dir.is_dir():
            continue
        for ver_dir in sorted(pkg_dir.iterdir()):
            if not ver_dir.is_dir():
                continue
            backend_file = ver_dir / "fromager-build-backend-requirements.txt"
            system_file = ver_dir / "fromager-build-system-requirements.txt"
            if not backend_file.exists() or not system_file.exists():
                continue

            backend_text = backend_file.read_text()
            system_text = system_file.read_text()
            backend_names = _parse_req_names(backend_text)
            system_names = _parse_req_names(system_text)

            extra = backend_names - system_names
            if extra:
                result.setdefault(pkg_dir.name, {})[ver_dir.name] = sorted(
                    extra
                )

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--index-url",
        default=RHAI_INDEX,
        help="Simple repository index URL (default: RHAI index)",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help="Base data directory (default: %(default)s)",
    )
    parser.add_argument(
        "--wheel-subdir",
        default=WHEEL_SUBDIR,
        help="Subdirectory under data-dir for wheel metadata "
        "(default: %(default)s)",
    )
    parser.add_argument(
        "--packages-yaml",
        default=PACKAGES_YAML,
        help="Packages YAML filename inside wheel-subdir "
        "(default: %(default)s)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=16,
        help="Number of parallel workers (default: %(default)s)",
    )
    parser.add_argument(
        "--skip-fetch",
        action="store_true",
        help="Only generate packages.yaml, skip wheel metadata fetching",
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

    dest_dir = args.data_dir / args.wheel_subdir
    packages_yaml = dest_dir / args.packages_yaml

    # Step 1: Get wheels from index
    logger.info("Fetching wheel list from %s", args.index_url)
    wheels = get_wheels_from_index(args.index_url, args.workers)
    dump_packages_yaml(wheels, packages_yaml)

    total_versions = sum(len(v) for v in wheels.values())
    logger.info(
        "Total: %d packages, %d unique versions",
        len(wheels),
        total_versions,
    )

    if args.skip_fetch:
        return

    # Step 2: Fetch wheel metadata in parallel
    dest_dir.mkdir(parents=True, exist_ok=True)
    tasks: list[tuple[str, str, str]] = []
    for name, versions in wheels.items():
        for version, url in versions.items():
            tasks.append((name, version, url))

    errors: list[str] = []
    session = _make_session(args.workers)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(
                fetch_wheel_metadata, name, version, url, dest_dir, session
            ): (name, version)
            for name, version, url in tasks
        }
        with tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Fetching wheel metadata",
        ) as pbar:
            for future in pbar:
                name, version = futures[future]
                try:
                    result = future.result()
                except Exception as e:
                    logger.error(
                        "Unexpected error for %s==%s: %s", name, version, e
                    )
                    errors.append(f"{name}=={version}: {e}")
                    continue
                if result is not None:
                    errors.append(result)

    logger.info(
        "Done: %d total, %d errors",
        len(tasks),
        len(errors),
    )
    if errors:
        logger.info("Errors:")
        for e in sorted(errors):
            logger.info("  %s", e)

    # Step 3: Compare build-backend vs build-system requirements
    extra_backend = compare_build_requirements(dest_dir)
    if extra_backend:
        extra_yaml = dest_dir / "extra_build_backend.yaml"
        with open(extra_yaml, "w") as f:
            yaml.dump(
                extra_backend, f, default_flow_style=False, sort_keys=True
            )
        total_extra = sum(
            len(v) for versions in extra_backend.values() for v in versions.values()
        )
        logger.info(
            "Wrote %d packages with extra build-backend deps to %s",
            len(extra_backend),
            extra_yaml,
        )
        for name, versions in sorted(extra_backend.items()):
            for version, pkgs in sorted(versions.items()):
                logger.info("  %s==%s: %s", name, version, pkgs)


if __name__ == "__main__":
    main()
