#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "beautifulsoup4",
#     "packaging>=24.2",
#     "tqdm",
#     "zipwire[httpx2]",
# ]
# ///
"""Extract fromager files, METADATA, and WHEEL from RHOAI wheels.

.. note::

   This script was generated with the assistance of Claude (Anthropic).
   Review before relying on its output.

Fetches all matching indexes from the Pulp API, scrapes the content listing
for ALL wheels (purelib and platlib), then uses zipwire's AsyncRemoteWheel
over HTTP/2 to extract fromager*.txt files plus dist-info METADATA and
WHEEL without downloading full wheel archives.

METADATA is parsed with ``packaging.metadata`` and re-serialised with the
description body dropped and license/summary truncated to 512 characters.
If parsing fails, the original METADATA is written and a marker file
``.metadata-parse-error`` is created.

Usage::

    uv run fetch-rhoai-metadata.py
    uv run fetch-rhoai-metadata.py 3.6-EA1 test
    uv run fetch-rhoai-metadata.py 3.5 prod
"""

from __future__ import annotations

import argparse
import asyncio
import json
import pathlib
import re
import urllib.parse

import bs4
import httpx2
import packaging.metadata
import packaging.utils
from tqdm import tqdm
from zipwire import AsyncRemoteWheel
from zipwire.backends import Httpx2AsyncReader

PULP_API_URL = "https://packages.redhat.com/api/pulp/public-rhai/api/v3/distributions/"
PULP_CONTENT_BASE_URL = "https://packages.redhat.com/api/pulp-content/public-rhai"

METADATA_PARSE_ERROR_MARKER = ".metadata-parse-error"
MAX_FIELD_LEN = 512

# Files to extract from the dist-info directory
_EXTRACT_FILENAMES = {
    "METADATA",
    "WHEEL",
    "fromager-build-backend-requirements.txt",
    "fromager-build-sdist-requirements.txt",
    "fromager-build-system-requirements.txt",
    "fromager-elf-provides.txt",
    "fromager-elf-requires.txt",
}

# rhoai-{version}[-EA{n}]-{accelerator}[{accel_ver}]-{rhel}[-sdists][-test]
_NAME_RE = re.compile(
    r"^(rhoai-\d+\.\d+(?:-EA\d+)?)"  # product_version
    r"-([a-z]+)([\d.]*)"  # accelerator name + optional version
    r"-(ubi\d+)"  # rhel_version
    r"(?:-sdists)?"
    r"(?:-test)?$"
)


async def fetch_indexes(
    client: httpx2.AsyncClient,
    version: str,
    test: bool,
) -> list[dict[str, str]]:
    """Fetch matching indexes from the Pulp distributions API."""
    results: list[dict[str, str]] = []
    expected_pv = f"rhoai-{version}"
    offset = 0
    limit = 100
    while True:
        resp = await client.get(PULP_API_URL, params={"limit": limit, "offset": offset})
        resp.raise_for_status()
        data = resp.json()
        for d in data.get("results", []):
            name: str = d["name"]
            if _NAME_RE.match(name) is None:
                continue
            if not name.startswith(expected_pv + "-"):
                continue
            if "-sdists" in name:
                continue
            is_test = name.endswith("-test")
            if test != is_test:
                continue
            index_name = name.removeprefix(expected_pv + "-")
            results.append({"name": name, "index_name": index_name})
        if data.get("next") is None:
            break
        offset += limit
    return results


class WheelIndex:
    """Parsed wheel listing for an index."""

    def __init__(self) -> None:
        self.wheels: list[dict[str, str]] = []
        self.purelib_names: set[str] = set()
        self.platlib_names: set[str] = set()
        self.manylinux_names: set[str] = set()


def parse_all_wheels(body: str, base_url: str) -> WheelIndex:
    """Parse an HTML content listing for ALL wheels (purelib + platlib).

    For platlib wheels, only includes x86_64 builds to avoid duplicating
    metadata across architectures.  Tracks purelib/platlib/manylinux
    package names for wheel-counts.json.
    """
    soup = bs4.BeautifulSoup(body, "html.parser")
    result = WheelIndex()
    for anchor in soup.find_all("a", href=True):
        href: str = anchor["href"]
        filename = urllib.parse.unquote(href.rsplit("/", 1)[-1].split("#", 1)[0])
        if not filename.endswith(".whl"):
            continue
        try:
            wname, wver, _build, tags = packaging.utils.parse_wheel_filename(filename)
        except packaging.utils.InvalidWheelFilename:
            continue
        name = str(wname)
        is_purelib = all(tag.platform == "any" for tag in tags)
        if is_purelib:
            result.purelib_names.add(name)
        else:
            result.platlib_names.add(name)
            if any(tag.platform.startswith("manylinux") for tag in tags):
                result.manylinux_names.add(name)
            # Only fetch x86_64 platlib wheels
            if not any(tag.platform.endswith("x86_64") for tag in tags):
                continue
        url = urllib.parse.urljoin(base_url, href.split("#", 1)[0])
        result.wheels.append(
            {
                "filename": filename,
                "url": url,
                "name": name,
                "version": str(wver),
            }
        )
    return result



def _shrink_metadata(raw: bytes) -> bytes:
    """Parse METADATA, drop description, truncate license/summary.

    Returns the re-serialised bytes.  Raises on parse failure.
    """
    metadata = packaging.metadata.Metadata.from_email(raw)
    metadata.description = None
    metadata.description_content_type = None
    if metadata.license and len(metadata.license) > MAX_FIELD_LEN:
        metadata.license = metadata.license[:MAX_FIELD_LEN - 3] + "..."
    if metadata.summary and len(metadata.summary) > MAX_FIELD_LEN:
        metadata.summary = metadata.summary[:MAX_FIELD_LEN - 3] + "..."
    return metadata.as_rfc822().as_bytes()


async def extract_wheel_files(
    client: httpx2.AsyncClient,
    wheel: dict[str, str],
    output_dir: pathlib.Path,
    sem: asyncio.Semaphore,
    pbar: tqdm[None],
) -> int:
    """Extract fromager files, METADATA, and WHEEL from a remote wheel."""
    async with sem:
        try:
            reader = Httpx2AsyncReader(wheel["url"], client=client)
            async with AsyncRemoteWheel(reader) as whl:
                extracted: dict[str, bytes] = {}
                for entry in whl.distinfolist():
                    basename = entry.filename.rsplit("/", 1)[-1]
                    if basename in _EXTRACT_FILENAMES and entry.file_size > 0:
                        extracted[basename] = await whl.read(entry)

                if not extracted:
                    return 0

                output_dir.mkdir(parents=True, exist_ok=True)
                for basename, data in extracted.items():
                    if basename == "METADATA":
                        try:
                            data = _shrink_metadata(data)
                        except Exception as exc:
                            output_dir.joinpath(METADATA_PARSE_ERROR_MARKER).write_text(
                                f"Failed to parse METADATA: {exc}\n"
                            )
                    output_dir.joinpath(basename).write_bytes(data)
                return len(extracted)
        finally:
            pbar.update(1)


WHEEL_COUNTS_FILE = "wheel-counts.json"


async def process_index(
    client: httpx2.AsyncClient,
    index: dict[str, str],
    version: str,
    base_dir: pathlib.Path,
    sem: asyncio.Semaphore,
) -> None:
    """Scrape one index and extract metadata from all wheels."""
    index_name = index["index_name"]
    content_url = f"{PULP_CONTENT_BASE_URL}/rhoai/{version}/{index_name}/"

    resp = await client.get(content_url)
    if resp.status_code == 404:
        tqdm.write(f"[{index_name}] not found (404), skipping")
        return
    resp.raise_for_status()
    wi = parse_all_wheels(resp.text, content_url)

    # Write wheel counts for ELF analysis script
    index_dir = base_dir / index_name
    index_dir.mkdir(parents=True, exist_ok=True)
    counts = {
        "purelib_packages": sorted(wi.purelib_names),
        "platlib_packages": sorted(wi.platlib_names),
        "manylinux_packages": sorted(wi.manylinux_names),
    }
    index_dir.joinpath(WHEEL_COUNTS_FILE).write_text(
        json.dumps(counts, indent=2) + "\n"
    )

    tasks = []
    skipped = 0
    for w in wi.wheels:
        out = index_dir / w["name"] / w["version"]
        # Skip if METADATA already extracted
        if out.joinpath("METADATA").exists():
            skipped += 1
            continue
        tasks.append((w, out))

    total = len(wi.wheels)
    new = len(tasks)
    if not tasks:
        tqdm.write(f"[{index_name}] {total} wheels, all {skipped} cached")
        return

    tqdm.write(f"[{index_name}] {total} wheels ({skipped} cached, {new} new)")

    pbar = tqdm(total=new, desc=index_name, unit="whl", leave=False)
    coros = [extract_wheel_files(client, w, out, sem, pbar) for w, out in tasks]
    results = await asyncio.gather(*coros, return_exceptions=True)
    pbar.close()

    extracted = sum(r for r in results if isinstance(r, int))
    errors = [r for r in results if isinstance(r, BaseException)]
    for err in errors:
        tqdm.write(f"[{index_name}] error: {err}")
    tqdm.write(f"[{index_name}] extracted {extracted} files, {len(errors)} errors")


async def main() -> None:
    ap = argparse.ArgumentParser(
        description="Extract fromager files and dist-info metadata from RHOAI wheels",
    )
    ap.add_argument(
        "version",
        nargs="?",
        default="3.6-EA1",
        help="RHOAI index version (default: 3.6-EA1)",
    )
    ap.add_argument(
        "index_type",
        nargs="?",
        default="test",
        choices=["test", "prod"],
        help="index type (default: test)",
    )
    ap.add_argument(
        "--workers",
        type=int,
        default=10,
        help="max concurrent wheel downloads (default: %(default)s)",
    )
    args = ap.parse_args()

    test: bool = args.index_type == "test"
    version: str = args.version
    base_dir = pathlib.Path("data") / f"rhoai-{version}"

    async with httpx2.AsyncClient(http2=True, follow_redirects=True, timeout=120) as client:
        tqdm.write(f"Fetching indexes for rhoai-{version} (test={test}) ...")
        indexes = await fetch_indexes(client, version, test)
        if not indexes:
            tqdm.write("No matching indexes found.")
            return
        indexes.sort(key=lambda d: d["name"])
        names = ", ".join(d["index_name"] for d in indexes)
        tqdm.write(f"Found {len(indexes)} indexes: {names}")

        sem = asyncio.Semaphore(args.workers)
        for index in indexes:
            await process_index(client, index, version, base_dir, sem)

    tqdm.write("Done.")


if __name__ == "__main__":
    asyncio.run(main())
