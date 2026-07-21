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
"""Fetch sdist metadata files from PyPI for packages in a Red Hat PyPI index.

Uses pypi_simple to enumerate packages/versions from a Red Hat simple index,
then downloads source distributions from PyPI and extracts PKG-INFO,
pyproject.toml, and setup.py into data/pypi/<name>/<version>/.

Optimized for re-runs: skips packages whose output directory already exists.
"""

from __future__ import annotations

import argparse
import io
import logging
import os
import tarfile
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
import yaml
from packaging.version import Version
from pypi_simple import PyPISimple
from tqdm import tqdm

logger = logging.getLogger(__name__)

RHAI_INDEX = (
    "https://packages.redhat.com/api/pypi/public-rhai/"
    "rhoai/3.5/cpu-ubi9-test/simple/"
)
PYPI_INDEX = "https://pypi.org/simple/"

EXTRACT_FILENAMES = {"PKG-INFO", "pyproject.toml", "setup.py"}

DATA_DIR = Path("data")
PACKAGES_YAML = "packages.yaml"
NO_SDIST_YAML = "no_sdist.yaml"

def _make_session(workers: int) -> requests.Session:
    """Create a requests session with connection pool sized for workers."""
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=workers, pool_maxsize=workers
    )
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def _fetch_versions(
    client: PyPISimple, name: str
) -> tuple[str, list[str]]:
    """Fetch unique versions for a single project from a simple index."""
    page = client.get_project_page(name, timeout=30)
    versions: set[str] = set()
    for pkg in page.packages:
        if pkg.version is not None:
            versions.add(pkg.version)
    return name, sorted(versions)


def get_packages_from_index(
    index_url: str, workers: int = 16
) -> dict[str, list[str]]:
    """Get all packages and their unique versions from a simple index."""
    client = PyPISimple(index_url)
    packages: dict[str, list[str]] = {}

    project_names = list(client.stream_project_names(timeout=60))
    logger.info("Found %d projects in index", len(project_names))

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(_fetch_versions, client, name): name
            for name in project_names
        }
        with tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Fetching versions",
        ) as pbar:
            for future in pbar:
                name = futures[future]
                try:
                    _, versions = future.result()
                except Exception as e:
                    logger.warning("Failed to fetch %s: %s", name, e)
                    continue
                if versions:
                    packages[name] = versions

    return packages


def dump_packages_yaml(
    packages: dict[str, list[str]], path: str | Path = PACKAGES_YAML
) -> None:
    """Write packages dict to YAML file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(
            {"packages": packages},
            f,
            default_flow_style=False,
            sort_keys=True,
        )
    logger.info("Wrote %d packages to %s", len(packages), path)


def load_packages_yaml(path: str | Path = PACKAGES_YAML) -> dict[str, list[str]]:
    """Load packages dict from YAML file."""
    with open(path) as f:
        data = yaml.safe_load(f)
    return data["packages"]


def _extract_from_tar(
    resp: requests.Response, dest: Path, filename: str
) -> None:
    """Stream a tar.gz/.tar.bz2 response and extract target files."""
    # Determine compression from content or just try gzip
    mode = "r|gz"
    if filename.endswith(".tar.bz2"):
        mode = "r|bz2"
    elif filename.endswith(".tar.xz"):
        mode = "r|xz"

    found = set()
    with tarfile.open(fileobj=resp.raw, mode=mode) as tf:
        for member in tf:
            if member.isdir():
                continue
            parts = member.name.split("/")
            # sdist has one top-level dir; files directly inside it
            if len(parts) == 2 and parts[1] in EXTRACT_FILENAMES:
                data = tf.extractfile(member)
                if data is not None:
                    (dest / parts[1]).write_bytes(data.read())
                    found.add(parts[1])
            # early exit once we've found all possible files
            if found == EXTRACT_FILENAMES:
                break


def _extract_from_zip(
    resp: requests.Response, dest: Path, filename: str
) -> None:
    """Download a .zip sdist and extract target files."""
    content = resp.content
    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        for name in zf.namelist():
            parts = name.split("/")
            if len(parts) == 2 and parts[1] in EXTRACT_FILENAMES:
                data = zf.read(name)
                (dest / parts[1]).write_bytes(data)


class FetchResult:
    """Result of a fetch_sdist call."""

    __slots__ = ("name", "version", "error", "reason")

    def __init__(
        self,
        name: str,
        version: str,
        error: str | None = None,
        reason: str | None = None,
    ) -> None:
        self.name = name
        self.version = version
        self.error = error
        # reason for missing sdist: "not on PyPI", "no sdist", etc.
        self.reason = reason

    @property
    def ok(self) -> bool:
        return self.error is None and self.reason is None


def fetch_sdist(
    name: str,
    version: str,
    pypi_dir: Path,
    session: requests.Session,
) -> FetchResult:
    """Find and extract metadata files from a PyPI sdist."""
    dest = pypi_dir / name / version
    if dest.is_dir():
        return FetchResult(name, version)  # already done

    # Strip local version suffix (e.g. "1.2.3+redhat" -> "1.2.3") since
    # PyPI does not allow local versions (PEP 440).
    pypi_version = version
    try:
        parsed = Version(version)
        if parsed.local is not None:
            pypi_version = str(parsed.public)
    except Exception:
        pass

    pypi = PyPISimple(PYPI_INDEX)
    try:
        page = pypi.get_project_page(name, timeout=30)
    except Exception:
        logger.warning("Project %s not found on PyPI", name)
        return FetchResult(name, version, reason="not on PyPI")

    sdists = [
        p
        for p in page.packages
        if p.package_type == "sdist" and p.version == pypi_version
    ]
    if not sdists:
        logger.debug("No sdist for %s==%s on PyPI", name, version)
        return FetchResult(name, version, reason="no sdist")

    sdist = sdists[0]
    try:
        resp = session.get(sdist.url, stream=True, timeout=120)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.warning("Failed to download %s: %s", sdist.filename, e)
        return FetchResult(name, version, error=f"download failed: {e}")

    dest.mkdir(parents=True, exist_ok=True)
    try:
        if sdist.filename.endswith(".zip"):
            _extract_from_zip(resp, dest, sdist.filename)
        else:
            _extract_from_tar(resp, dest, sdist.filename)
    except Exception as e:
        logger.warning("Failed to extract %s: %s", sdist.filename, e)
        # Remove incomplete directory
        for f in dest.iterdir():
            f.unlink()
        dest.rmdir()
        return FetchResult(name, version, error=f"extract failed: {e}")

    extracted = [f.name for f in dest.iterdir()]
    logger.info("Extracted %s==%s: %s", name, version, extracted)
    return FetchResult(name, version)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--index-url",
        default=RHAI_INDEX,
        help="Simple repository index URL (default: RHAI index)",
    )
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
        help="Number of parallel download workers (default: %(default)s)",
    )
    parser.add_argument(
        "--no-sdist-yaml",
        default=NO_SDIST_YAML,
        help="Path to missing sdists YAML file (default: %(default)s)",
    )
    parser.add_argument(
        "--skip-fetch",
        action="store_true",
        help="Only generate packages.yaml, skip sdist fetching",
    )
    parser.add_argument(
        "--reuse-yaml",
        action="store_true",
        help="Reuse existing packages.yaml instead of fetching from index",
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

    # Derive paths from data dir
    packages_yaml = args.data_dir / args.packages_yaml
    no_sdist_yaml = args.data_dir / args.no_sdist_yaml
    pypi_dir = args.data_dir / "pypi"

    # Step 1: Get packages from index or reuse YAML
    if args.reuse_yaml and packages_yaml.exists():
        logger.info("Reusing existing %s", packages_yaml)
        packages = load_packages_yaml(packages_yaml)
    else:
        logger.info("Fetching package list from %s", args.index_url)
        packages = get_packages_from_index(args.index_url, args.workers)
        dump_packages_yaml(packages, packages_yaml)

    total_versions = sum(len(v) for v in packages.values())
    logger.info(
        "Total: %d packages, %d unique versions",
        len(packages),
        total_versions,
    )

    if args.skip_fetch:
        return

    # Step 2: Fetch sdists in parallel
    pypi_dir.mkdir(parents=True, exist_ok=True)
    tasks: list[tuple[str, str]] = []
    for name, versions in packages.items():
        for version in versions:
            tasks.append((name, version))

    errors: list[str] = []
    # missing sdists: {reason: {name: [versions]}}
    missing: dict[str, dict[str, list[str]]] = {}
    session = _make_session(args.workers)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(fetch_sdist, name, version, pypi_dir, session): (
                name,
                version,
            )
            for name, version in tasks
        }
        with tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Fetching sdists",
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
                if result.reason is not None:
                    by_reason = missing.setdefault(result.reason, {})
                    by_reason.setdefault(result.name, []).append(
                        result.version
                    )
                elif result.error is not None:
                    errors.append(
                        f"{result.name}=={result.version}: {result.error}"
                    )

    # Write missing sdist info
    if missing:
        with open(no_sdist_yaml, "w") as f:
            yaml.dump(missing, f, default_flow_style=False, sort_keys=True)
        total_missing = sum(
            len(v) for by_name in missing.values() for v in by_name.values()
        )
        logger.info(
            "Wrote %d missing sdist entries to %s",
            total_missing,
            no_sdist_yaml,
        )

    logger.info(
        "Done: %d total, %d errors",
        len(tasks),
        len(errors),
    )
    if errors:
        logger.info("Errors:")
        for e in sorted(errors):
            logger.info("  %s", e)


if __name__ == "__main__":
    main()
