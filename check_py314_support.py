# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "aiohttp",
#     "aiohttp-client-cache[sqlite]",
#     "beautifulsoup4",
#     "packaging",
# ]
# ///
# ruff: noqa: T201
"""Check Python 3.14 compatibility for all RHOAI production indexes.

Collects unique package names from all production variants, then checks the
newest stable release on PyPI for each:

1. Requires-Python does not exclude 3.14
2. For packages shipped as platlib (platform-specific) wheels in RHOAI, the
   latest PyPI release has a cp314-compatible wheel (cp314, abi3, or
   py3-none-any)
3. Trove classifiers: flags packages that declare 3.12 support but lack 3.14

Usage:
    uv run rhoai_check_py314_support.py
"""

from __future__ import annotations

import asyncio
import json
import re
import sys
import urllib.parse
from dataclasses import dataclass, field

import pathlib

import aiohttp
import bs4
from aiohttp_client_cache import CachedSession, SQLiteBackend
import packaging.specifiers
import packaging.utils
import packaging.version

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PULP_API_URL = "https://packages.redhat.com/api/pulp/public-rhai/api/v3/distributions/"
PYPI_JSON_URL = "https://pypi.org/pypi/{name}/json"

CACHE_DIR = pathlib.Path(".cache")
CACHE_TTL = 4 * 3600  # 4 hours

RHOAI_CONCURRENCY = 50
PYPI_CONCURRENCY = 10

PRODUCT_VERSION = "rhoai-3.6"

TARGET_PYTHON = packaging.version.Version("3.14")
NEXT_PYTHON = packaging.version.Version("3.15")
_CP_RE = re.compile(r"^cp3(\d+)t?$")

_CLS_312 = "Programming Language :: Python :: 3.12"
_CLS_314 = "Programming Language :: Python :: 3.14"

# rhoai-{version}[-EA{n}]-{accelerator}[{accel_ver}]-{rhel}[-sdists][-test]
_NAME_RE = re.compile(
    r"^(rhoai-\d+\.\d+(?:-EA\d+)?)"  # product_version
    r"-([a-z]+)([\d.]*)"  # accelerator name + optional version
    r"-(ubi\d+)"  # rhel_version
    r"(?:-sdists)?"
    r"(?:-test)?$"
)

# ---------------------------------------------------------------------------
# Pulp distribution discovery
# ---------------------------------------------------------------------------


@dataclass
class Distribution:
    """Minimal Pulp distribution info."""

    name: str
    base_url: str
    product_version: str


def _parse_product_version(name: str) -> str | None:
    m = _NAME_RE.match(name)
    return m.group(1) if m else None


async def fetch_distributions(session: aiohttp.ClientSession) -> list[Distribution]:
    """Fetch all production distributions from Pulp."""
    results: list[Distribution] = []
    offset = 0
    limit = 100
    while True:
        async with session.get(
            PULP_API_URL, params={"limit": limit, "offset": offset}
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()
        for d in data.get("results", []):
            name = d["name"]
            base_url = d.get("base_url", "")
            pv = _parse_product_version(name)
            if (
                pv == PRODUCT_VERSION
                and name.endswith("-test")
                and not name.endswith(("-sdists", "-sdists-test"))
            ):
                results.append(
                    Distribution(name=name, base_url=base_url, product_version=pv)
                )
        if data.get("next") is None:
            break
        offset += limit
    return results


# ---------------------------------------------------------------------------
# RHOAI content scraping
# ---------------------------------------------------------------------------


@dataclass
class WheelInfo:
    """Parsed wheel file from a content listing."""

    filename: str
    name: str
    version: packaging.version.Version


def _parse_wheel_links(body: str) -> list[WheelInfo]:
    """Parse an HTML directory listing and extract wheel filenames."""
    soup = bs4.BeautifulSoup(body, "html.parser")
    wheels: list[WheelInfo] = []
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        filename = urllib.parse.unquote(href.split("/")[-1])
        if not filename.endswith(".whl"):
            continue
        try:
            name, version, _build, _tags = packaging.utils.parse_wheel_filename(
                filename
            )
        except packaging.utils.InvalidWheelFilename:
            continue
        wheels.append(WheelInfo(filename=filename, name=str(name), version=version))
    return wheels


async def scrape_content_listing(
    session: aiohttp.ClientSession, dist: Distribution
) -> list[WheelInfo]:
    """Scrape a Pulp content directory listing for wheel files.

    Hacky, but much, much fastern than Pulp's PyPI JSON API.
    """
    url = dist.base_url.rstrip("/") + "/"
    async with session.get(url) as resp:
        resp.raise_for_status()
        body = await resp.text()
    return _parse_wheel_links(body)


# ---------------------------------------------------------------------------
# Wheel / specifier helpers
# ---------------------------------------------------------------------------


def check_requires_python(spec_str: str | None) -> bool:
    """Return True if Requires-Python allows 3.14 (or is unset)."""
    return classify_requires_python(spec_str) != "excludes"


def classify_requires_python(spec_str: str | None) -> str:
    """Classify a Requires-Python specifier for 3.14 readiness.

    Returns one of:
    - "excludes": 3.14 is not allowed
    - "includes": 3.14 is allowed by a meaningful upper bound (<3.15 or <=3.15)
    - "open":     unset, unparseable, or no meaningful upper bound (incl.
                  silly bounds like <4.0 that don't actually cap near 3.14)
    """
    if not spec_str:
        return "open"
    try:
        spec = packaging.specifiers.SpecifierSet(spec_str)
    except packaging.specifiers.InvalidSpecifier:
        return "open"
    if TARGET_PYTHON not in spec:
        return "excludes"
    for s in spec:
        if s.operator in ("<", "<="):
            try:
                v = packaging.version.Version(s.version)
            except packaging.version.InvalidVersion:
                continue
            if v.release[:2] <= (NEXT_PYTHON.major, NEXT_PYTHON.minor):
                return "includes"
    return "open"


def is_platlib_wheel(filename: str) -> bool:
    """True if the wheel is platform-specific (platlib, not py3-none-any)."""
    return not filename.endswith("-none-any.whl")


def _is_cp314_compatible(filename: str) -> bool:
    """Check if a wheel filename indicates Python 3.14 compatibility.

    Compatible means one of:
    - cp314 interpreter tag (compiled for 3.14)
    - abi3 with cp3XX where XX <= 14 (stable ABI, forward-compatible)
    - py3 interpreter (generic Python 3, works on any 3.x)
    """
    try:
        _, _, _, tags = packaging.utils.parse_wheel_filename(filename)
    except packaging.utils.InvalidWheelFilename:
        return False
    for tag in tags:
        m = _CP_RE.match(tag.interpreter)
        if m:
            ver = int(m.group(1))
            # cp314 / cp314t — direct support
            if ver == 14:
                return True
            # cp3XX-abi3 — stable ABI, forward-compatible
            if tag.abi == "abi3" and ver <= 14:
                return True
        if tag.interpreter in ("py3", "py314"):
            return True
    return False


# ---------------------------------------------------------------------------
# PyPI checking (single JSON API call per package)
# ---------------------------------------------------------------------------


@dataclass
class PyPIResult:
    """Latest-version check result from PyPI."""

    latest_version: str | None = None
    requires_python: str | None = None
    requires_python_ok: bool = True
    requires_python_class: str = "open"
    has_cp314: bool = False  # any cp314-compatible wheel (native, abi3, or py3)
    has_cp314_native: bool = False  # cp314 or cp314t interpreter
    has_abi3: bool = False  # abi3 wheel with min version <= 3.14
    has_any_wheel: bool = False
    interpreters: set[str] = field(default_factory=set)
    not_on_pypi: bool = False
    has_312_classifier: bool = False
    has_314_classifier: bool = False
    release_date: str | None = None


async def check_pypi(
    session: aiohttp.ClientSession, name: str, sem: asyncio.Semaphore
) -> PyPIResult:
    """Fetch latest version info, wheel tags, and classifiers in one call."""
    canonical = packaging.utils.canonicalize_name(name)
    url = PYPI_JSON_URL.format(name=canonical)
    result = PyPIResult()

    async with sem:
        try:
            async with session.get(url) as resp:
                if resp.status == 404:
                    result.not_on_pypi = True
                    return result
                resp.raise_for_status()
                data = await resp.json()
        except Exception:
            result.not_on_pypi = True
            return result

    info = data.get("info", {})
    result.latest_version = info.get("version")
    result.requires_python = info.get("requires_python")
    result.requires_python_class = classify_requires_python(result.requires_python)
    result.requires_python_ok = result.requires_python_class != "excludes"

    # Trove classifiers
    classifiers: list[str] = info.get("classifiers") or []
    result.has_312_classifier = _CLS_312 in classifiers
    result.has_314_classifier = _CLS_314 in classifiers

    # Wheel tag analysis and release date from the latest version's files
    upload_dates: list[str] = []
    for f in data.get("urls", []):
        if ts := f.get("upload_time_iso_8601"):
            upload_dates.append(ts)
        fn = f.get("filename", "")
        if not fn.endswith(".whl"):
            continue
        if f.get("yanked", False):
            continue
        result.has_any_wheel = True
        try:
            _, _, _, tags = packaging.utils.parse_wheel_filename(fn)
        except packaging.utils.InvalidWheelFilename:
            continue
        for tag in tags:
            result.interpreters.add(tag.interpreter)
            m = _CP_RE.match(tag.interpreter)
            if m:
                ver = int(m.group(1))
                if ver == 14:
                    result.has_cp314_native = True
                if tag.abi == "abi3" and ver <= 14:
                    result.has_abi3 = True
        if _is_cp314_compatible(fn):
            result.has_cp314 = True
    if upload_dates:
        result.release_date = min(upload_dates)[:10]

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


@dataclass
class PackageInfo:
    """Per-package-name summary collected from RHOAI indexes."""

    name: str
    is_platlib: bool


CACHEDIR_TAG = (
    "Signature: 8a477f597d28d172789f06886806bc55\n"
    "# This file is a cache directory tag created by sdist-analyzer.\n"
    "# For information about cache directory tags see https://bford.info/cachedir/\n"
)


async def main():
    CACHE_DIR.mkdir(exist_ok=True)
    CACHE_DIR.joinpath("CACHEDIR.TAG").write_text(CACHEDIR_TAG)
    cache = SQLiteBackend(
        cache_name=str(CACHE_DIR.joinpath("check_py314.sqlite")),
        expire_after=CACHE_TTL,
    )
    async with CachedSession(cache=cache) as session:
        await session.delete_expired_responses()
        await _run(session)


async def _run(session: aiohttp.ClientSession):
    # ---- Step 1: Fetch RHOAI production distributions ----
    print(f"Fetching {PRODUCT_VERSION} production distributions ...", file=sys.stderr)
    dists = await fetch_distributions(session)

    if not dists:
        print(
            f"ERROR: No {PRODUCT_VERSION} production distributions found",
            file=sys.stderr,
        )
        return

    print(f"Found {len(dists)} distributions:", file=sys.stderr)
    for d in dists:
        print(f"  {d.name}", file=sys.stderr)

    # ---- Step 2: Scrape wheel listings and collect unique package names ----
    print("\nScraping wheel listings ...", file=sys.stderr)
    packages: dict[str, PackageInfo] = {}

    tasks = [scrape_content_listing(session, d) for d in dists]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for dist, wheels in zip(dists, results, strict=True):
        if isinstance(wheels, BaseException):
            print(f"  ERROR scraping {dist.name}: {wheels}", file=sys.stderr)
            continue
        print(f"  {dist.name}: {len(wheels)} wheels", file=sys.stderr)
        for w in wheels:
            if w.name not in packages:
                packages[w.name] = PackageInfo(name=w.name, is_platlib=False)
            if is_platlib_wheel(w.filename):
                packages[w.name].is_platlib = True

    print(f"\nUnique package names: {len(packages)}", file=sys.stderr)
    platlib_names = {n for n, p in packages.items() if p.is_platlib}
    pure_names = {n for n, p in packages.items() if not p.is_platlib}
    print(
        f"  platlib: {len(platlib_names)}  pure-python: {len(pure_names)}",
        file=sys.stderr,
    )

    # ---- Step 3: Query PyPI JSON API for each package ----
    print("Querying PyPI for latest versions ...", file=sys.stderr)
    pypi_sem = asyncio.Semaphore(PYPI_CONCURRENCY)
    pypi_tasks = {
        name: asyncio.create_task(check_pypi(session, name, pypi_sem))
        for name in sorted(packages)
    }
    await asyncio.gather(*pypi_tasks.values())
    pypi_results = {name: t.result() for name, t in pypi_tasks.items()}

    # ---- Step 4: Classify results ----
    rp_bad: list[tuple[str, PyPIResult]] = []
    rp_includes: list[tuple[str, PyPIResult]] = []
    platlib_cp314_ok: list[tuple[str, PyPIResult]] = []
    platlib_cp314_fail: list[tuple[str, PyPIResult]] = []
    platlib_not_on_pypi: list[str] = []
    platlib_no_wheels: list[tuple[str, PyPIResult]] = []
    pure_ok: list[str] = []
    pure_rp_bad: list[tuple[str, PyPIResult]] = []
    not_on_pypi: list[str] = []

    for name in sorted(packages):
        pkg = packages[name]
        pypi = pypi_results[name]

        if pypi.not_on_pypi:
            not_on_pypi.append(name)
            if pkg.is_platlib:
                platlib_not_on_pypi.append(name)
            continue

        if not pypi.requires_python_ok:
            rp_bad.append((name, pypi))
        elif pypi.requires_python_class == "includes":
            rp_includes.append((name, pypi))

        if pkg.is_platlib:
            if not pypi.has_any_wheel:
                platlib_no_wheels.append((name, pypi))
            elif pypi.has_cp314:
                platlib_cp314_ok.append((name, pypi))
            else:
                platlib_cp314_fail.append((name, pypi))
        else:
            if pypi.requires_python_ok:
                pure_ok.append(name)
            else:
                pure_rp_bad.append((name, pypi))

    # ---- Step 5: Print report ----
    print("\n=== REQUIRES-PYTHON ANALYSIS ===")
    print(f"\n  --- Excludes 3.14 ({len(rp_bad)}) ---")
    if not rp_bad:
        print("  None — all packages allow Python 3.14.")
    else:
        for name, pypi in rp_bad:
            kind = "platlib" if packages[name].is_platlib else "pure"
            print(
                f"  {name} ({kind})  latest: {pypi.latest_version}"
                f"  Requires-Python: {pypi.requires_python}"
            )

    print(f"\n  --- Includes 3.14 via upper bound (<3.15 or <=3.15) ({len(rp_includes)}) ---")
    if not rp_includes:
        print("  None.")
    else:
        for name, pypi in rp_includes:
            kind = "platlib" if packages[name].is_platlib else "pure"
            print(
                f"  {name} ({kind})  latest: {pypi.latest_version}"
                f"  Requires-Python: {pypi.requires_python}"
            )

    print("\n=== PLATLIB PACKAGES: cp314 WHEEL ON PyPI LATEST ===")

    if platlib_cp314_fail:
        print(f"\n  --- NO cp314 wheel ({len(platlib_cp314_fail)}) ---")
        for name, pypi in platlib_cp314_fail:
            interp = ", ".join(sorted(pypi.interpreters))
            rp_note = ""
            if not pypi.requires_python_ok:
                rp_note = f"  Requires-Python: {pypi.requires_python}"
            print(
                f"  {name}  latest: {pypi.latest_version}  interpreters: {interp}{rp_note}"
            )

    if platlib_not_on_pypi:
        print(f"\n  --- Not on PyPI ({len(platlib_not_on_pypi)}) ---")
        for name in platlib_not_on_pypi:
            print(f"  {name}")

    if platlib_no_wheels:
        print(f"\n  --- No stable wheels on PyPI ({len(platlib_no_wheels)}) ---")
        for name, pypi in platlib_no_wheels:
            print(f"  {name}  latest: {pypi.latest_version}")

    if platlib_cp314_ok:
        print(f"\n  --- cp314-compatible ({len(platlib_cp314_ok)}) ---")
        for name, pypi in platlib_cp314_ok:
            print(f"  {name}  latest: {pypi.latest_version}")

    # --- Classifier check: has 3.12 but not 3.14 (skip requires_python failures) ---
    rp_bad_names = {name for name, _ in rp_bad}
    cls_missing_314 = [
        (name, pypi_results[name])
        for name in sorted(packages)
        if name not in rp_bad_names
        and not pypi_results[name].not_on_pypi
        and pypi_results[name].has_312_classifier
        and not pypi_results[name].has_314_classifier
    ]
    print("\n=== TROVE CLASSIFIERS: has 3.12 but NOT 3.14 ===")
    if not cls_missing_314:
        print("None — all packages with a 3.12 classifier also have 3.14.")
    else:
        for name, pypi in cls_missing_314:
            kind = "platlib" if packages[name].is_platlib else "pure"
            date = pypi.release_date or "?"
            print(f"  {name} ({kind})  latest: {pypi.latest_version}  released: {date}")

    print("\n=== PURE-PYTHON PACKAGES ===")
    if pure_rp_bad:
        print(f"  Requires-Python excludes 3.14 ({len(pure_rp_bad)}):")
        for name, pypi in pure_rp_bad:
            print(
                f"    {name}  latest: {pypi.latest_version}"
                f"  Requires-Python: {pypi.requires_python}"
            )
    pure_not_on_pypi = [n for n in not_on_pypi if not packages[n].is_platlib]
    if pure_not_on_pypi:
        print(f"  Not on PyPI ({len(pure_not_on_pypi)}):")
        for name in pure_not_on_pypi:
            print(f"    {name}")
    print(f"  OK: {len(pure_ok)}")

    # ---- Summary ----
    def pct(n: int, d: int) -> str:
        return f"{100 * n / d:.1f}%" if d else "n/a"

    total = len(packages)
    on_pypi = total - len(not_on_pypi)
    rp_open = on_pypi - len(rp_bad) - len(rp_includes)
    has_314_cls = sum(1 for n in packages if pypi_results[n].has_314_classifier)
    has_314_native = sum(1 for n in packages if pypi_results[n].has_cp314_native)
    has_abi3 = sum(1 for n in packages if pypi_results[n].has_abi3)
    confirmed_ready_names = {
        n
        for n in packages
        if pypi_results[n].has_cp314_native
        or pypi_results[n].has_abi3
        or pypi_results[n].has_314_classifier
    }
    has_314_either = len(confirmed_ready_names)

    not_ready_names = {n for n, _ in rp_bad} | {n for n, _ in platlib_cp314_fail}
    not_ready = len(not_ready_names)

    # Packages with a 3.12 classifier but no 3.14 classifier are probably not
    # ready — unless stronger evidence (cp314/abi3 wheel) already confirms them
    # ready, or they are already confirmed not ready.
    probably_not_ready_names = (
        {name for name, _ in cls_missing_314}
        - confirmed_ready_names
        - not_ready_names
    )
    probably_not_ready = len(probably_not_ready_names)

    # Probably ready: pure-python OK + platlib with a cp314 wheel, minus the
    # ones downgraded to "probably not ready" by the classifier signal and the
    # ones already counted as confirmed ready.
    ready_names = (
        (set(pure_ok) | {n for n, _ in platlib_cp314_ok})
        - probably_not_ready_names
        - confirmed_ready_names
    )
    fully_ready = len(ready_names)
    print("\n--- Summary ---")
    print(f"  total packages:        {total}")
    print(f"  on PyPI:               {on_pypi}")
    print(f"  not on PyPI:           {len(not_on_pypi)}")
    print()
    print(f"  pure-python:           {len(pure_names)}")
    print(f"  platlib:               {len(platlib_names)}")
    print()
    print(f"  requires-python excludes 3.14: {len(rp_bad)}")
    print(f"  requires-python includes 3.14: {len(rp_includes)}")
    print(f"  requires-python open (incl. <4.0): {rp_open}")
    print()
    print(f"  platlib cp314 OK:      {len(platlib_cp314_ok)}")
    print(f"  platlib cp314 FAIL:    {len(platlib_cp314_fail)}")
    print(f"  platlib not-on-pypi:   {len(platlib_not_on_pypi)}")
    print(f"  platlib no-wheels:     {len(platlib_no_wheels)}")
    print()
    print(f"  3.12 classifier w/o 3.14: {len(cls_missing_314)}")
    print(f"  has cp314/cp314t wheel:  {has_314_native} / {on_pypi}")
    print(f"  has abi3 wheel:          {has_abi3} / {on_pypi}")
    print(f"  has 3.14 classifier:     {has_314_cls} / {on_pypi}")
    print()
    print(
        f"  confirmed 3.14-ready:    {has_314_either} / {on_pypi}"
        f"  ({pct(has_314_either, on_pypi)})"
    )
    print(
        f"  probably 3.14-ready:     {fully_ready} / {total}"
        f"  ({pct(fully_ready, total)})"
    )
    print(
        f"  probably NOT ready:      {probably_not_ready} / {total}"
        f"  ({pct(probably_not_ready, total)})"
    )
    print(
        f"  confirmed NOT ready:     {not_ready} / {total}"
        f"  ({pct(not_ready, total)})"
    )


if __name__ == "__main__":
    asyncio.run(main())
