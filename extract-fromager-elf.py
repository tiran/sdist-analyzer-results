# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "beautifulsoup4",
#     "packaging",
#     "tqdm",
#     "zipwire[httpx2]",
# ]
# ///
"""Extract fromager*.txt files from RHOAI platlib wheels and analyze ELF deps.

Fetches all matching indexes from the Pulp API, scrapes the content listing
for platform-specific wheels, then uses zipwire's AsyncRemoteWheel over
HTTP/2 to extract files matching ``fromager*.txt`` without downloading
full wheel archives.  After extraction, analyzes ELF requires/provides
and writes a report per index.

Usage::

    uv run docs/extract_fromager.py
    uv run docs/extract_fromager.py 3.6-EA1 test
    uv run docs/extract_fromager.py 3.5 prod
"""

from __future__ import annotations

import argparse
import asyncio
import fnmatch
import io
import pathlib
import re
import urllib.parse

import bs4
import httpx2
import packaging.utils
from tqdm import tqdm
from zipwire import AsyncRemoteWheel
from zipwire.backends import Httpx2AsyncReader

PULP_API_URL = "https://packages.redhat.com/api/pulp/public-rhai/api/v3/distributions/"
PULP_CONTENT_BASE_URL = "https://packages.redhat.com/api/pulp-content/public-rhai"

# -- ELF analysis constants (from analyze_elf_requires.py) --

ELF_REQUIRES = "fromager-elf-requires.txt"
ELF_PROVIDES = "fromager-elf-provides.txt"
NO_FROMAGER_MARKER = ".no-fromager-elf"

# Match the library name before the first '(' or end of line.
_LIB_RE = re.compile(r"^([^\s(]+)")

# Libraries guaranteed by the manylinux_2_34 platform tag plus dynamic
# linkers and rtld.  These are always available and uninteresting for
# dependency analysis.
_IGNORE_LIBS = {
    # dynamic linkers (per architecture)
    "ld-linux-aarch64.so.1",
    "ld-linux-x86-64.so.2",
    "ld64.so.1",
    "ld64.so.2",
    "rtld",
    # manylinux_2_34 allow list
    "libGL.so.1",
    "libICE.so.6",
    "libSM.so.6",
    "libX11.so.6",
    "libXext.so.6",
    "libXrender.so.1",
    "libanl.so.1",
    "libatomic.so.1",
    "libc.so.6",
    "libdl.so.2",
    "libexpat.so.1",
    "libgcc_s.so.1",
    "libglib-2.0.so.0",
    "libgobject-2.0.so.0",
    "libgthread-2.0.so.0",
    "libm.so.6",
    "libmvec.so.1",
    "libnsl.so.1",
    "libpthread.so.0",
    "libresolv.so.2",
    "librt.so.1",
    "libstdc++.so.6",
    "libutil.so.1",
    "libz.so.1",
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


def parse_platlib_wheels(body: str, base_url: str) -> list[dict[str, str]]:
    """Parse an HTML content listing for platlib (platform-specific) wheels."""
    soup = bs4.BeautifulSoup(body, "html.parser")
    wheels: list[dict[str, str]] = []
    for anchor in soup.find_all("a", href=True):
        href: str = anchor["href"]
        filename = urllib.parse.unquote(href.rsplit("/", 1)[-1].split("#", 1)[0])
        if not filename.endswith(".whl"):
            continue
        try:
            wname, wver, _build, tags = packaging.utils.parse_wheel_filename(filename)
        except packaging.utils.InvalidWheelFilename:
            continue
        # skip pure-python wheels (purelib)
        if all(tag.platform == "any" for tag in tags):
            continue
        url = urllib.parse.urljoin(base_url, href.split("#", 1)[0])
        wheels.append(
            {
                "filename": filename,
                "url": url,
                "name": str(wname),
                "version": str(wver),
            }
        )
    return wheels


async def extract_fromager(
    client: httpx2.AsyncClient,
    wheel: dict[str, str],
    output_dir: pathlib.Path,
    sem: asyncio.Semaphore,
    pbar: tqdm[None],
) -> int:
    """Extract fromager*.txt from a single remote wheel via zipwire."""
    async with sem:
        try:
            reader = Httpx2AsyncReader(wheel["url"], client=client)
            async with AsyncRemoteWheel(reader) as whl:
                matches = [
                    info
                    for info in whl.infolist()
                    if fnmatch.fnmatch(info.filename.rsplit("/", 1)[-1], "fromager*.txt")
                ]
                output_dir.mkdir(parents=True, exist_ok=True)
                if not matches:
                    output_dir.joinpath(NO_FROMAGER_MARKER).write_text(
                        f"No fromager*.txt files found in {wheel['filename']}\n"
                    )
                    return 0
                written = 0
                for info in matches:
                    if info.file_size == 0:
                        continue
                    data = await whl.read(info)
                    if not data:
                        continue
                    basename = info.filename.rsplit("/", 1)[-1]
                    output_dir.joinpath(basename).write_bytes(data)
                    written += 1
                if not written:
                    output_dir.joinpath(NO_FROMAGER_MARKER).write_text(
                        f"All fromager*.txt files empty in {wheel['filename']}\n"
                    )
                return written
        finally:
            pbar.update(1)


async def process_index(
    client: httpx2.AsyncClient,
    index: dict[str, str],
    version: str,
    base_dir: pathlib.Path,
    sem: asyncio.Semaphore,
) -> list[dict[str, str]]:
    """Scrape one index and extract fromager files from its platlib wheels.

    Returns the full list of platlib wheels found in the content listing.
    """
    index_name = index["index_name"]
    content_url = f"{PULP_CONTENT_BASE_URL}/rhoai/{version}/{index_name}/"

    resp = await client.get(content_url)
    resp.raise_for_status()
    wheels = parse_platlib_wheels(resp.text, content_url)

    tasks = []
    skipped = 0
    for w in wheels:
        out = base_dir / index_name / w["name"] / w["version"]
        if out.exists():
            skipped += 1
            continue
        tasks.append((w, out))

    total = len(wheels)
    new = len(tasks)
    if not tasks:
        tqdm.write(f"[{index_name}] {total} platlib wheels, all {skipped} cached")
        return wheels

    tqdm.write(f"[{index_name}] {total} platlib wheels ({skipped} cached, {new} new)")

    pbar = tqdm(total=new, desc=index_name, unit="whl", leave=False)
    coros = [extract_fromager(client, w, out, sem, pbar) for w, out in tasks]
    results = await asyncio.gather(*coros, return_exceptions=True)
    pbar.close()

    extracted = sum(r for r in results if isinstance(r, int))
    errors = [r for r in results if isinstance(r, BaseException)]
    for err in errors:
        tqdm.write(f"[{index_name}] error: {err}")
    tqdm.write(f"[{index_name}] extracted {extracted} files, {len(errors)} errors")
    return wheels


# -- ELF analysis --


def _parse_lib_names(path: pathlib.Path) -> set[str]:
    """Extract shared library names from an elf-requires or elf-provides file."""
    libs: set[str] = set()
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = _LIB_RE.match(line)
        if m:
            libs.add(m.group(1))
    return libs


def _collect_elf_data(
    search_dir: pathlib.Path,
) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Collect per-project ELF provides and requires.

    Returns ``({lib: {providers}}, {lib: {requirers}})``.
    """
    provides: dict[str, set[str]] = {}
    requires: dict[str, set[str]] = {}

    for prov_file in sorted(search_dir.rglob(ELF_PROVIDES)):
        project = prov_file.parent.parent.name
        for lib in _parse_lib_names(prov_file):
            provides.setdefault(lib, set()).add(project)

    for req_file in sorted(search_dir.rglob(ELF_REQUIRES)):
        project = req_file.parent.parent.name
        for lib in _parse_lib_names(req_file):
            requires.setdefault(lib, set()).add(project)

    return provides, requires


def _format_external_report(
    requires: dict[str, set[str]],
    provided_libs: set[str],
) -> str | None:
    """Format report for external (unresolved) library dependencies.

    These are libraries not in the manylinux baseline and not provided
    by any wheel in the index.
    """
    ignore = _IGNORE_LIBS | provided_libs
    lib_projects = {lib: projs for lib, projs in requires.items() if lib not in ignore}
    if not lib_projects:
        return None

    ranked = sorted(lib_projects.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    max_lib = max(len(lib) for lib in lib_projects)
    max_count = len(str(len(ranked[0][1])))

    out = io.StringIO()
    out.write("External shared library dependencies\n")
    out.write("=" * 36 + "\n\n")
    out.write(f"{'Library':<{max_lib}}  {'Count':>{max_count}}  Projects\n")
    out.write(f"{'-' * max_lib}  {'-' * max_count}  --------\n")
    total_refs = 0
    for lib, projects in ranked:
        count = len(projects)
        total_refs += count
        names = ", ".join(sorted(projects))
        out.write(f"{lib:<{max_lib}}  {count:>{max_count}}  {names}\n")
    out.write(f"\n{len(lib_projects)} unique libraries across {total_refs} project references\n")
    return out.getvalue()


def _format_inter_wheel_report(
    provides: dict[str, set[str]],
    requires: dict[str, set[str]],
) -> str | None:
    """Format report for inter-wheel shared library dependencies.

    Shows libraries that are provided by one wheel and required by a
    different wheel (self-provides are excluded).
    """
    inter_deps: dict[str, tuple[set[str], set[str]]] = {}
    for lib in sorted(provides):
        if lib in _IGNORE_LIBS:
            continue
        if lib not in requires:
            continue
        providers = provides[lib]
        requirers = requires[lib] - providers  # exclude self-requires
        if requirers:
            inter_deps[lib] = (providers, requirers)

    if not inter_deps:
        return None

    max_lib = max(len(lib) for lib in inter_deps)

    out = io.StringIO()
    out.write("Inter-wheel shared library dependencies\n")
    out.write("=" * 39 + "\n\n")
    out.write(f"{'Library':<{max_lib}}  Provided by -> Required by\n")
    out.write(f"{'-' * max_lib}  {'-' * 27}\n")
    for lib in sorted(inter_deps):
        providers, requirers = inter_deps[lib]
        prov_str = ", ".join(sorted(providers))
        req_str = ", ".join(sorted(requirers))
        out.write(f"{lib:<{max_lib}}  {prov_str} -> {req_str}\n")
    out.write(
        f"\n{len(inter_deps)} shared libraries provided by wheels and used by other wheels\n"
    )
    return out.getvalue()


def analyze_elf(search_dir: pathlib.Path) -> str | None:
    """Run ELF analysis on a directory tree.

    Returns a combined report with two sections:

    1. External dependencies -- libraries not provided by any wheel and
       not in the manylinux baseline.
    2. Inter-wheel dependencies -- libraries provided by one wheel and
       consumed by another.

    Returns None when no ELF requires data is found.
    """
    provides, requires = _collect_elf_data(search_dir)
    if not requires:
        return None

    provided_libs = set(provides)
    parts: list[str] = []

    ext = _format_external_report(requires, provided_libs)
    if ext:
        parts.append(ext)

    inter = _format_inter_wheel_report(provides, requires)
    if inter:
        parts.append(inter)

    return "\n\n".join(parts) if parts else None


async def main() -> None:
    ap = argparse.ArgumentParser(
        description="Extract fromager*.txt from RHOAI platlib wheels",
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

        sem = asyncio.Semaphore(10)
        # {index_name: [wheel, ...]} - all platlib wheels seen per index
        all_wheels: dict[str, list[dict[str, str]]] = {}
        for index in indexes:
            wheels = await process_index(client, index, version, base_dir, sem)
            all_wheels[index["index_name"]] = wheels

    # Run ELF analysis per index
    if not base_dir.is_dir():
        return
    for index_dir in sorted(base_dir.iterdir()):
        if not index_dir.is_dir():
            continue
        report = analyze_elf(index_dir)
        if report is None:
            tqdm.write(f"[{index_dir.name}] no ELF requires data")
            continue
        dest = index_dir / "elf-analysis.txt"
        dest.write_text(report)
        tqdm.write(f"[{index_dir.name}] wrote {dest}")

    # Report wheels without ELF data - check every scraped platlib
    # wheel, including those that had no fromager files at all (no
    # output directory created).  Deduplicate across indexes.
    no_elf: dict[str, set[str]] = {}  # {name: {versions}}
    for idx_name, wheels in all_wheels.items():
        for w in wheels:
            wdir = base_dir / idx_name / w["name"] / w["version"]
            has_elf = (
                wdir.joinpath(ELF_REQUIRES).is_file() or wdir.joinpath(ELF_PROVIDES).is_file()
            )
            if not has_elf:
                no_elf.setdefault(w["name"], set()).add(w["version"])

    # Combined analysis across all indexes
    parts: list[str] = []
    combined = analyze_elf(base_dir)
    if combined:
        parts.append(combined)

    if no_elf:
        out = io.StringIO()
        out.write("Packages without fromager-elf-requires/provides\n")
        out.write("=" * 47 + "\n\n")
        for name, vers in sorted(no_elf.items()):
            out.write(f"{name} ({', '.join(sorted(vers))})\n")
        out.write(f"\n{len(no_elf)} packages\n")
        no_elf_text = out.getvalue()
        parts.append(no_elf_text)

        tqdm.write(f"\n{len(no_elf)} packages without fromager-elf-requires/provides:")
        fmt = [f"{n} ({', '.join(sorted(v))})" for n, v in sorted(no_elf.items())]
        tqdm.write("  " + ", ".join(fmt))

    if parts:
        dest = base_dir / "elf-analysis.txt"
        dest.write_text("\n\n".join(parts))
        tqdm.write(f"Wrote combined analysis: {dest}")

    tqdm.write("Done.")


if __name__ == "__main__":
    asyncio.run(main())
