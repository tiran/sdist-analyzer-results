#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "packaging>=24.2",
#     "pypi-attestations",
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
import re
import tarfile
import zipfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

import packaging.metadata
import pypi_attestations
import requests
import yaml
from packaging.version import InvalidVersion, Version
from pypi_simple import ACCEPT_JSON_ONLY, PyPISimple
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


@dataclass
class FetchResult:
    """Result of a fetch_sdist call."""

    name: str
    version: str
    error: str | None = None
    # reason for missing sdist: "not on PyPI", "no sdist", etc.
    reason: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.reason is None


@dataclass
class ReleaseInfo:
    """PyPI release info for the latest version of a package."""

    version: str
    release_date: str | None = None
    wheel_tags: list[str] = field(default_factory=list)
    has_attestation: bool = False
    publisher: str | None = None
    repository: str | None = None
    workflow: str | None = None
    ref: str | None = None
    commit: str | None = None

    def as_dict(self) -> dict:
        """Return a dict with only non-empty fields for YAML output."""
        d: dict = {"version": self.version}
        if self.release_date:
            d["release_date"] = self.release_date
        if self.wheel_tags:
            d["wheel_tags"] = self.wheel_tags
        d["has_attestation"] = self.has_attestation
        if self.publisher:
            d["publisher"] = self.publisher
        if self.repository:
            d["repository"] = self.repository
        if self.workflow:
            d["workflow"] = self.workflow
        if self.ref:
            d["ref"] = self.ref
        if self.commit:
            d["commit"] = self.commit
        return d


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


# Match cpXY python tags; extract major.minor
_CP_RE = re.compile(r"^cp(\d)(\d+)$")


def _latest_version(versions: list[str]) -> str:
    """Pick the latest version using PEP 440 sorting."""
    def key(v: str) -> tuple[int, Version | str]:
        try:
            return (0, Version(v))
        except InvalidVersion:
            return (1, v)
    return max(versions, key=key)


def _is_relevant_wheel(filename: str) -> bool:
    """Check if a wheel is relevant: py3/manylinux, Python >= 3.12 or abi3."""
    if not filename.endswith(".whl"):
        return False
    parts = filename.removesuffix(".whl").split("-")
    if len(parts) < 5:
        return False
    py_tag, abi_tag, plat_tag = parts[-3], parts[-2], parts[-1]

    # Platform filter: only "any" or manylinux for relevant architectures
    _RELEVANT_ARCHS = ("x86_64", "aarch64", "ppc64le", "s390x")
    if plat_tag == "any":
        pass
    elif plat_tag.startswith("manylinux"):
        if not any(plat_tag.endswith(arch) for arch in _RELEVANT_ARCHS):
            return False
    else:
        return False

    # abi3 wheels are compatible with any Python >= the specified version
    if abi_tag == "abi3":
        return True

    # py3-none-any (pure Python)
    if py_tag == "py3" and abi_tag == "none":
        return True

    # cpXY wheels: require Python >= 3.12
    m = _CP_RE.match(py_tag)
    if m:
        major, minor = int(m.group(1)), int(m.group(2))
        return major >= 3 and minor >= 12

    # py3X tags
    if py_tag.startswith("py3") and len(py_tag) >= 4:
        try:
            return int(py_tag[3:]) >= 12
        except ValueError:
            pass

    return False


def fetch_release_info(
    name: str,
    version: str,
    pypi_client: PyPISimple,
) -> ReleaseInfo | None:
    """Fetch release info and attestations from PyPI Simple API."""
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
        return None

    version_pkgs = [p for p in page.packages if p.version == pypi_version]
    if not version_pkgs:
        return None

    # Earliest upload date across all files for this version
    upload_times = [p.upload_time for p in version_pkgs if p.upload_time]
    release_date = str(min(upload_times).date()) if upload_times else None

    # Collect relevant wheel tags
    wheel_tags: set[str] = set()
    for p in version_pkgs:
        if p.package_type == "wheel" and _is_relevant_wheel(p.filename):
            parts = p.filename.removesuffix(".whl").split("-")
            wheel_tags.add("-".join(parts[-3:]))

    info = ReleaseInfo(
        version=pypi_version,
        release_date=release_date,
        wheel_tags=sorted(wheel_tags),
    )

    # Check for PEP 740 attestations
    pkg_with_provenance = next(
        (p for p in version_pkgs if p.provenance_url is not None), None
    )
    if pkg_with_provenance is None:
        return info

    info.has_attestation = True
    try:
        prov_dict = pypi_client.get_provenance(pkg_with_provenance, timeout=30)
        prov = pypi_attestations.Provenance.model_validate(prov_dict)
        if prov.attestation_bundles:
            bundle = prov.attestation_bundles[0]
            publisher = bundle.publisher
            info.publisher = publisher.kind
            if hasattr(publisher, "repository"):
                info.repository = publisher.repository
            if hasattr(publisher, "workflow"):
                info.workflow = publisher.workflow
            # Extract ref and commit from Fulcio certificate claims
            if bundle.attestations:
                try:
                    claims = bundle.attestations[0].certificate_claims
                    info.ref = claims.get("1.3.6.1.4.1.57264.1.14")
                    info.commit = claims.get("1.3.6.1.4.1.57264.1.13")
                except Exception:
                    pass
    except Exception:
        pass

    return info


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

    # Statistics: packages missing some or all sdists
    # Collect all missing package names and their missing version counts
    missing_pkg_versions: dict[str, int] = {}
    for by_name in missing.values():
        for name, versions in by_name.items():
            missing_pkg_versions[name] = (
                missing_pkg_versions.get(name, 0) + len(versions)
            )
    total_pkg_versions = {name: len(versions) for name, versions in packages.items()}
    all_missing = sorted(
        name for name, n_missing in missing_pkg_versions.items()
        if n_missing >= total_pkg_versions.get(name, 0)
    )
    some_missing = sorted(
        name for name, n_missing in missing_pkg_versions.items()
        if n_missing < total_pkg_versions.get(name, 0)
    )
    n_total = len(packages)
    n_all = len(all_missing)
    n_some = len(some_missing)
    n_full = n_total - n_all - n_some

    logger.info("Package sdist coverage:")
    logger.info("  %d packages total", n_total)
    logger.info("  %d with all sdists available (%.1f%%)", n_full, n_full / n_total * 100 if n_total else 0)
    logger.info("  %d missing some sdists (%.1f%%)", n_some, n_some / n_total * 100 if n_total else 0)
    logger.info("  %d missing all sdists (%.1f%%)", n_all, n_all / n_total * 100 if n_total else 0)
    if all_missing:
        logger.info("  Packages with no sdists: %s", ", ".join(all_missing))

    # Write missing sdist info with statistics
    no_sdist_path = args.data_dir / "pypi-no-sdist.yaml"
    output: dict = {
        "summary": {
            "total_packages": n_total,
            "all_sdists_available": n_full,
            "missing_some_sdists": n_some,
            "missing_all_sdists": n_all,
        },
    }
    if all_missing:
        output["packages_without_any_sdist"] = all_missing
    if some_missing:
        output["packages_missing_some_sdists"] = some_missing
    output.update(missing)
    with open(no_sdist_path, "w") as f:
        yaml.dump(output, f, default_flow_style=False, sort_keys=False)
    logger.info("Wrote %s", no_sdist_path)

    logger.info(
        "Done: %d total versions, %d errors",
        len(tasks),
        len(errors),
    )
    if errors:
        logger.info("Errors:")
        for e in sorted(errors):
            logger.info("  %s", e)

    # Step 3: Fetch PyPI release info + attestations for latest version
    logger.info("Fetching PyPI release info for %d packages ...", len(packages))
    release_tasks = []
    for name, versions in packages.items():
        ver = _latest_version(versions)
        release_tasks.append((name, ver))

    # Use JSON accept header for upload_time and provenance_url
    pypi_json_client = PyPISimple(PYPI_INDEX, session=session, accept=ACCEPT_JSON_ONLY)
    releases: dict[str, ReleaseInfo] = {}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(fetch_release_info, name, ver, pypi_json_client): name
            for name, ver in release_tasks
        }
        with tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Fetching release info",
        ) as pbar:
            for future in pbar:
                name = futures[future]
                try:
                    info = future.result()
                except Exception as e:
                    logger.debug("Failed to fetch release info for %s: %s", name, e)
                    continue
                if info is not None:
                    releases[name] = info

    # Attestation statistics
    n_attested = sum(1 for r in releases.values() if r.has_attestation)
    publisher_counts: Counter[str] = Counter()
    ref_counts: Counter[str] = Counter()
    for r in releases.values():
        if not r.has_attestation:
            continue
        publisher_counts[r.publisher or "unknown"] += 1
        if not r.ref:
            ref_counts["unknown"] += 1
        elif r.ref.startswith("refs/tags/"):
            ref_counts["tag"] += 1
        elif r.ref in ("refs/heads/main", "refs/heads/master"):
            ref_counts["main/master"] += 1
        else:
            ref_counts["other branch"] += 1

    releases_path = args.data_dir / "pypi-releases.yaml"
    output_releases: dict = {
        "note": "Only the latest version of each package was checked.",
        "summary": {
            "total": len(releases),
            "with_attestation": n_attested,
            "without_attestation": len(releases) - n_attested,
            "coverage_pct": round(n_attested / len(releases) * 100, 1) if releases else 0,
            "publisher_kinds": dict(publisher_counts.most_common()),
            "ref_types": dict(ref_counts.most_common()),
        },
        "packages": {name: info.as_dict() for name, info in sorted(releases.items())},
    }
    with open(releases_path, "w") as f:
        yaml.dump(output_releases, f, default_flow_style=False, sort_keys=False)

    logger.info(
        "Wrote %d release entries to %s (%d with attestations)",
        len(releases), releases_path, n_attested,
    )


if __name__ == "__main__":
    main()
