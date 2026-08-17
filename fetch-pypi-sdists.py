#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "packaging>=24.2",
#     "pypi-simple",
#     "pyyaml",
#     "requests",
#     "tqdm",
# ]
# ///
# SPDX-License-Identifier: Apache-2.0
"""Fetch sdist metadata files from PyPI for RHOAI packages.

.. note::

   This script was generated with the assistance of Claude (Anthropic).
   Review before relying on its output.

Scans local RHOAI wheel data (previously fetched by
``fetch-rhoai-metadata.py``) to discover package names and versions,
then downloads source distributions from PyPI and extracts PKG-INFO,
pyproject.toml, and setup.py into data/pypi/<name>/<version>/.

Optimized for re-runs: skips packages whose output directory already exists.

Usage::

    uv run fetch-pypi-sdists.py
    uv run fetch-pypi-sdists.py 3.6-EA1
"""

from __future__ import annotations

import argparse
import io
import logging
import tarfile
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import packaging.metadata
import requests
import yaml
from packaging.version import Version
from pypi_simple import PyPISimple
from tqdm import tqdm

logger = logging.getLogger(__name__)

PYPI_INDEX = "https://pypi.org/simple/"

EXTRACT_FILENAMES = {"PKG-INFO", "pyproject.toml", "setup.py"}
MAX_FIELD_LEN = 512

DATA_DIR = Path("data")
DEFAULT_VERSION = "3.6-EA1"


def _shrink_pkg_info(raw: bytes) -> bytes:
    """Drop description body and truncate license/summary in PKG-INFO.

    Uses the same format as wheel METADATA (RFC 822).
    Returns original bytes on parse failure.
    """
    try:
        metadata = packaging.metadata.Metadata.from_email(raw)
        metadata.description = None
        metadata.description_content_type = None
        if metadata.license and len(metadata.license) > MAX_FIELD_LEN:
            metadata.license = metadata.license[:MAX_FIELD_LEN - 3] + "..."
        if metadata.summary and len(metadata.summary) > MAX_FIELD_LEN:
            metadata.summary = metadata.summary[:MAX_FIELD_LEN - 3] + "..."
        return metadata.as_rfc822().as_bytes()
    except Exception:
        return raw

def _make_session(workers: int) -> requests.Session:
    """Create a requests session with connection pool sized for workers."""
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=workers, pool_maxsize=workers
    )
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def scan_local_packages(rhoai_dir: Path) -> dict[str, list[str]]:
    """Scan local RHOAI data directory for package names and versions.

    Looks at ``data/rhoai-<version>/<index>/<package>/<version>/``
    directories created by ``fetch-rhoai-metadata.py``.  Returns
    ``{name: [versions]}`` with duplicates across indexes merged.
    """
    packages: dict[str, set[str]] = {}
    for index_dir in sorted(rhoai_dir.iterdir()):
        if not index_dir.is_dir():
            continue
        for pkg_dir in index_dir.iterdir():
            if not pkg_dir.is_dir():
                continue
            for ver_dir in pkg_dir.iterdir():
                if not ver_dir.is_dir():
                    continue
                packages.setdefault(pkg_dir.name, set()).add(ver_dir.name)
    return {name: sorted(versions) for name, versions in sorted(packages.items())}


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
                fobj = tf.extractfile(member)
                if fobj is not None:
                    content = fobj.read()
                    if parts[1] == "PKG-INFO":
                        content = _shrink_pkg_info(content)
                    dest.joinpath(parts[1]).write_bytes(content)
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
                content = zf.read(name)
                if parts[1] == "PKG-INFO":
                    content = _shrink_pkg_info(content)
                dest.joinpath(parts[1]).write_bytes(content)


class FetchResult:
    """Result of a fetch_sdist call."""

    __slots__ = ("error", "name", "reason", "version")

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
    pypi_client: PyPISimple,
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

    try:
        page = pypi_client.get_project_page(name, timeout=30)
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
    parser.add_argument(
        "--workers",
        type=int,
        default=16,
        help="Number of parallel download workers (default: %(default)s)",
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

    rhoai_dir = args.data_dir / f"rhoai-{args.version}"
    pypi_dir = args.data_dir / "pypi"

    if not rhoai_dir.is_dir():
        logger.error("No local data at %s", rhoai_dir)
        logger.error("Run fetch-rhoai-metadata.py first.")
        return

    # Step 1: Scan local data for package names and versions
    packages = scan_local_packages(rhoai_dir)
    total_versions = sum(len(v) for v in packages.values())
    logger.info(
        "Found %d packages, %d versions in %s",
        len(packages),
        total_versions,
        rhoai_dir,
    )

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
    pypi_client = PyPISimple(PYPI_INDEX, session=session)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(fetch_sdist, name, version, pypi_dir, session, pypi_client): (
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

    # Write missing sdist info for later analysis
    if missing:
        no_sdist_path = args.data_dir / "pypi-no-sdist.yaml"
        with open(no_sdist_path, "w") as f:
            yaml.dump(missing, f, default_flow_style=False, sort_keys=True)
        total_missing = sum(
            len(v) for by_name in missing.values() for v in by_name.values()
        )
        logger.info("Wrote %d missing sdist entries to %s", total_missing, no_sdist_path)
        for reason, by_name in sorted(missing.items()):
            count = sum(len(v) for v in by_name.values())
            logger.info("  %s: %d versions", reason, count)

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
