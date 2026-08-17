#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "tqdm",
# ]
# ///
"""Analyze ELF shared library dependencies from RHOAI wheel metadata.

.. note::

   This script was generated with the assistance of Claude (Anthropic).
   Review before relying on its output.

Reads fromager-elf-requires/provides metadata previously extracted by
``fetch-rhoai-metadata.py`` and writes Markdown reports
(``elf-analysis.md``) per index and combined.  Reports include summary
statistics, Mermaid bar charts, external/inter-wheel dependency tables,
and dependency complexity classifications.

Usage::

    uv run analyze-elf-deps.py
    uv run analyze-elf-deps.py 3.6-EA1
"""

from __future__ import annotations

import argparse
import io
import json
import pathlib
import re
import typing

from tqdm import tqdm

# -- ELF analysis constants (from analyze_elf_requires.py) --

ELF_REQUIRES = "fromager-elf-requires.txt"
ELF_PROVIDES = "fromager-elf-provides.txt"

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

# Library name prefixes to ignore.  These are provided by specific wheels
# (e.g. torch) and don't need to appear in the external dependency report.
# Also used as an accelerator-specific signal for dependency classification.
# Subset of _NEVER_BUNDLE_LIBS that are AI accelerator runtime libraries
# (CUDA, ROCm, UCX).  Packages depending on these are classified as
# "accelerator-specific" rather than just "unbundleable".
_ACCELERATOR_LIBS = {
    # PyTorch runtime (provided by torch wheel)
    "libc10.so",
    "libc10_cuda.so",
    "libc10_hip.so",
    "libtorch.so",
    "libtorch_cpu.so",
    "libtorch_cuda.so",
    "libtorch_hip.so",
    "libtorch_python.so",
    # NVIDIA CUDA
    "libcublas.so.12",
    "libcublas.so.13",
    "libcublasLt.so.12",
    "libcublasLt.so.13",
    "libcuda.so.1",
    "libcudart.so.12",
    "libcudart.so.13",
    "libcudnn.so.9",
    "libcufft.so.11",
    "libcufft.so.12",
    "libcufile.so.0",
    "libcurand.so.10",
    "libcusolver.so.12",
    "libcusparse.so.12",
    "libcusparseLt.so.0",
    "libnccl.so.2",
    "libnppicc.so.12",
    "libnppicc.so.13",
    "libnvJitLink.so.12",
    "libnvJitLink.so.13",
    "libnvjpeg.so.12",
    "libnvjpeg.so.13",
    "libnvrtc.so.12",
    "libnvrtc.so.13",
    "libnvshmem_host.so.3",
    # AMD ROCm
    "libMIOpen.so.1",
    "libamd_comgr.so.3",
    "libamdhip64.so.7",
    "libhipblas.so.3",
    "libhipblaslt.so.1",
    "libhipfft.so.0",
    "libhipfftw.so.0",
    "libhiprand.so.1",
    "libhiprtc.so.7",
    "libhipsolver.so.1",
    "libhipsparse.so.4",
    "libhipsparselt.so.0",
    "libhsa-runtime64.so.1",
    "librccl.so.1",
    "librocblas.so.5",
    "librocm_smi64.so.1",
    "librocprofiler-register.so.0",
    "librocrand.so.1",
    "librocsolver.so.0",
    "libroctracer64.so.4",
    "libroctx64.so.4",
    # UCX -- GPU interconnect
    "libucp.so.0",
    "libucs.so.0",
}

# Libraries that could be vendored / statically linked into wheels so that
# the resulting wheel becomes manylinux-compatible without an external
# system dependency.
_BUNDLEABLE_LIBS = {
    # ECMWF GRIB codec -- bundled copy links against system libgomp,
    # image codecs (libjpeg, libopenjp2, libpng) at runtime
    "libeccodes.so.0.1",
    "libjasper.so.4",           # JPEG-2000, transitive dep of libeccodes
    "libev.so.4",
    "libloguru.so.2",
    "libutf8proc.so.2",
    # math / science
    "libqhull_r.so.7",
    # database clients / archive / messaging -- bundleable but
    # transitively depend on security libraries (libssl, libkrb5);
    # bundled copies will link against the system's OpenSSL/Kerberos
    "libmariadb.so.3",          # -> libssl, libcrypto
    "libpq.so.5",               # -> libssl, libcrypto, libgssapi_krb5, libkrb5
    "libre2.so.9",
    "libtbb.so.2",
    "libthrift-0.15.0.so",
    "libyaml-0.so.2",
    "libzip.so.5",              # -> libcrypto
    "libzmq.so.5",              # -> libgssapi_krb5, libkrb5, libcrypto
}

# Libraries not yet classified as bundleable or unbundleable.  Listing
# them here keeps the "unknown" report section clean -- only truly
# unexpected libraries show up there.
# Libraries provided by other Python wheels in the index (cross-wheel
# dependencies).  These are not external system deps -- they are resolved
# by installing the providing wheel alongside the consuming one.
_WHEEL_PROVIDED_LIBS = {
    "libz3.so",             # provided by z3-solver wheel (unversioned soname)
    "libz3.so.4.15",        # versioned soname (also provided by z3-solver)
    "libtvm_ffi.so",        # provided by apache-tvm-ffi wheel
}

# Libraries not yet classified as bundleable or unbundleable.  Listing
# them here keeps the "unknown" report section clean -- only truly
# unexpected libraries show up there.
_UNDECIDED_LIBS: set[str] = set()

# Libraries that must NEVER be bundled into wheels -- either because of
# security / certification requirements (OpenSSL, Kerberos), because
# they are provided by the accelerator runtime / driver stack, because
# they must match the system runtime (MPI, kernel interfaces, OpenMP/BLAS),
# because they are used by many packages (image codecs, compression),
# or because they transitively depend on unbundleable libraries (e.g.
# libcurl -> libssl + libkrb5, libeccodes -> libgomp).
_NEVER_BUNDLE_LIBS = {
    # crypto / auth -- must use system-provided versions
    "libcrypto.so.3",
    "libcrypt.so.2",            # password hashing (glibc)
    "libgssapi_krb5.so.2",
    "libk5crypto.so.3",
    "libkeyutils.so.1",        # kernel key management
    "libkrb5.so.3",
    "libkrb5support.so.0",     # Kerberos support library
    "libcom_err.so.2",         # MIT error table (Kerberos / e2fsprogs)
    "libssl.so.3",
    # SASL / LDAP / NSS -- authentication and directory services
    "libsasl2.so.3",
    "libldap.so.2",
    "liblber.so.2",
    "libnss3.so",
    "libnssutil3.so",
    "libnspr4.so",
    # NVIDIA CUDA
    "libcublas.so.12",
    "libcublas.so.13",
    "libcublasLt.so.12",
    "libcublasLt.so.13",
    "libcuda.so.1",
    "libcudart.so.12",
    "libcudart.so.13",
    "libcudnn.so.9",
    "libcufft.so.11",
    "libcufft.so.12",
    "libcufile.so.0",
    "libcurand.so.10",
    "libcusolver.so.12",
    "libcusparse.so.12",
    "libcusparseLt.so.0",
    "libnccl.so.2",
    "libnppicc.so.12",
    "libnppicc.so.13",
    "libnvJitLink.so.12",
    "libnvJitLink.so.13",
    "libnvjpeg.so.12",
    "libnvjpeg.so.13",
    "libnvrtc.so.12",
    "libnvrtc.so.13",
    "libnvshmem_host.so.3",
    # AMD ROCm
    "libMIOpen.so.1",
    "libamd_comgr.so.3",
    "libamdhip64.so.7",
    "libhipblas.so.3",
    "libhipblaslt.so.1",
    "libhipfft.so.0",
    "libhipfftw.so.0",
    "libhiprand.so.1",
    "libhiprtc.so.7",
    "libhipsolver.so.1",
    "libhipsparse.so.4",
    "libhipsparselt.so.0",
    "libhsa-runtime64.so.1",
    "librccl.so.1",
    "librocblas.so.5",
    "librocm_smi64.so.1",
    "librocprofiler-register.so.0",
    "librocrand.so.1",
    "librocsolver.so.0",
    "libroctracer64.so.4",
    "libroctx64.so.4",
    # UCX
    "libucp.so.0",
    "libucs.so.0",
    # MPI -- must match system MPI, network fabric, and job scheduler
    "libmpi.so.40",
    "libmpi_cxx.so.40",
    # math / science -- must match system runtime to avoid conflicts;
    # libgfortran is also a transitive dep of libopenblas
    "libgfortran.so.5",
    "libgmp.so.10",
    "libgomp.so.1",
    "libopenblaso.so.0",
    "libopenblasp.so.0",
    # security / kernel interfaces
    "libselinux.so.1",
    # system networking
    "libtirpc.so.3",            # Sun RPC
    "libaio.so.1",
    "libdebuginfod.so.1",
    "libnuma.so.1",
    "libpython3.12.so.1.0",
    "libsqlite3.so.0",         # always present (Python depends on it)
    # image codecs -- used by multiple packages (Pillow, opencv,
    # torchvision, docling-parse, etc.), use system versions
    "libjbig.so.2.1",
    "libjpeg.so.62",
    "liblcms2.so.2",
    "libpng16.so.16",
    "libopenjp2.so.7",
    "libtiff.so.5",
    "libwebp.so.7",
    "libwebpdemux.so.2",
    "libwebpmux.so.3",
    # XML / XSLT -- security-sensitive, use system versions
    "libexslt.so.0",
    "libxml2.so.2",
    "libxslt.so.1",
    # compression -- typically available on all systems
    "libbz2.so.1",
    "libzstd.so.1",
    "liblz4.so.1",
    "liblzma.so.5",
    "libsnappy.so.1",
    # ABI-specific platform library; always present because
    # Python's ctypes module depends on it
    "libffi.so.8",
    "libunwind.so.8",
    # terminal -- needs system terminfo database
    "libncurses.so.6",
    "libtinfo.so.6",
    # ODBC -- needs system-installed database drivers
    "libodbc.so.2",
    # OCR -- needs system tessdata files
    "liblept.so.5",
    "libtesseract.so.4",
    # font rendering -- transitive deps: libharfbuzz, libpng, libbz2, libbrotli
    "libfreetype.so.6",
    # FFmpeg / multimedia -- large, licensing, HW acceleration
    "libavcodec.so.60",
    "libavdevice.so.60",
    "libavfilter.so.9",
    "libavformat.so.60",
    "libavutil.so.58",
    "libswresample.so.4",
    "libswscale.so.7",
    # GIS -- libgeos_c requires libgeos (large C++ geometry engine)
    "libgeos_c.so.1",
    # ICU -- too large to bundle (~30 MB libicudata), but typically
    # available on systems where gdb is installed (gdb depends on ICU)
    "libicui18n.so.67",
    "libicuuc.so.67",
    # GIS projection -- transitive deps: libcurl -> libssl, libkrb5
    "libproj.so.25",
    # networking -- transitively depends on libssl / libkrb5
    "libcurl.so.4",
    # GDAL -- 96 transitive deps including libssl, libgomp, libopenblaso
    "libgdal.so.36",
    # HDF5 -- large, may need MPI variant; libnetcdf depends on it
    "libhdf5.so.310",
    "libhdf5_hl.so.310",
    # NetCDF -- transitively depends on libcurl -> libssl / libkrb5
    "libnetcdf.so.19",
}

WHEEL_COUNTS_FILE = "wheel-counts.json"

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
    """Format report for external (unresolved) library dependencies as Markdown.

    These are libraries not in the manylinux baseline and not provided
    by any wheel in the index.
    """
    lib_projects = {
        lib: projs
        for lib, projs in requires.items()
        if not lib in _IGNORE_LIBS and lib not in provided_libs
    }
    if not lib_projects:
        return None

    ranked = sorted(lib_projects.items(), key=lambda kv: (-len(kv[1]), kv[0]))

    out = io.StringIO()
    out.write("| Library | Count | Projects |\n")
    out.write("|:---|---:|:---|\n")
    total_refs = 0
    for lib, projects in ranked:
        count = len(projects)
        total_refs += count
        names = ", ".join(sorted(projects))
        out.write(f"| {lib} | {count} | {names} |\n")
    out.write(
        f"\n{len(lib_projects)} unique libraries across {total_refs} project references\n"
    )
    return out.getvalue()


def _format_inter_wheel_report(
    provides: dict[str, set[str]],
    requires: dict[str, set[str]],
) -> str | None:
    """Format report for inter-wheel shared library dependencies as Markdown.

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

    out = io.StringIO()
    out.write("| Library | Provided by | Required by |\n")
    out.write("|:---|:---|:---|\n")
    for lib in sorted(inter_deps):
        providers, requirers = inter_deps[lib]
        prov_str = ", ".join(sorted(providers))
        req_str = ", ".join(sorted(requirers))
        out.write(f"| {lib} | {prov_str} | {req_str} |\n")
    out.write(
        f"\n{len(inter_deps)} shared libraries provided by wheels and used by other wheels\n"
    )
    return out.getvalue()


def _classify_projects(
    requires: dict[str, set[str]],
    provided_libs: set[str],
) -> dict[str, dict[str, set[str]] | list[str]]:
    """Classify projects by external shared library dependency complexity.

    Returns a dict with keys:
    ``manylinux_only``, ``could_bundle``, ``accelerator``,
    ``has_unbundleable``, ``undecided``, ``unknown_external``.
    Each value is a ``{project: {external_libs}}`` dict (or a list for
    manylinux_only).
    """
    # Collect all projects, then build {project: {external_libs}}
    all_projects: set[str] = set()
    project_libs: dict[str, set[str]] = {}
    for lib, projects in requires.items():
        all_projects.update(projects)
        if lib in _IGNORE_LIBS or lib in provided_libs:
            continue
        for proj in projects:
            project_libs.setdefault(proj, set()).add(lib)

    # Also find projects with accelerator deps (including ignored libc10*/libtorch*)
    accel_projects: set[str] = set()
    for lib, projects in requires.items():
        if lib in _ACCELERATOR_LIBS:
            accel_projects.update(projects)

    manylinux_only: list[str] = sorted(all_projects - set(project_libs) - accel_projects)
    could_bundle: dict[str, set[str]] = {}
    accelerator: dict[str, set[str]] = {}
    has_unbundleable: dict[str, set[str]] = {}
    undecided: dict[str, set[str]] = {}
    unknown_external: dict[str, set[str]] = {}

    known = _BUNDLEABLE_LIBS | _NEVER_BUNDLE_LIBS | _UNDECIDED_LIBS | _WHEEL_PROVIDED_LIBS

    for proj in sorted(accel_projects - set(project_libs)):
        accelerator[proj] = set()

    for project, libs in sorted(project_libs.items()):
        if project in accel_projects:
            accelerator[project] = libs
        elif libs <= _BUNDLEABLE_LIBS:
            could_bundle[project] = libs
        elif libs & _NEVER_BUNDLE_LIBS:
            has_unbundleable[project] = libs
        elif libs <= known:
            undecided[project] = libs
        else:
            unknown_external[project] = libs

    return {
        "manylinux_only": manylinux_only,
        "could_bundle": could_bundle,
        "accelerator": accelerator,
        "has_unbundleable": has_unbundleable,
        "undecided": undecided,
        "unknown_external": unknown_external,
    }


def _format_dependency_complexity_report(
    requires: dict[str, set[str]],
    provided_libs: set[str],
) -> str | None:
    """Format the dependency complexity classification as Markdown."""
    cl = _classify_projects(requires, provided_libs)
    manylinux_only = cl["manylinux_only"]
    could_bundle = cl["could_bundle"]
    accelerator = cl["accelerator"]
    has_unbundleable = cl["has_unbundleable"]
    undecided = cl["undecided"]
    unknown_external = cl["unknown_external"]

    total = (
        len(manylinux_only) + len(could_bundle) + len(accelerator)
        + len(has_unbundleable) + len(undecided) + len(unknown_external)
    )
    if not total:
        return None

    out = io.StringIO()

    if manylinux_only:
        out.write(f"### Manylinux-only ({len(manylinux_only)} packages)\n\n")
        out.write(
            "These packages only depend on manylinux baseline libraries\n"
            "and/or libraries provided by other wheels in the index.\n\n"
        )
        out.write(", ".join(sorted(manylinux_only)) + "\n\n")

    if could_bundle:
        out.write(f"### Could become manylinux by bundling ({len(could_bundle)} packages)\n\n")
        out.write(
            "All external deps are vendorable -- bundling them would make\n"
            "these wheels manylinux-compatible.\n\n"
        )
        out.write("| Package | Libraries |\n")
        out.write("|:---|:---|\n")
        for project in sorted(could_bundle):
            libs_str = ", ".join(sorted(could_bundle[project]))
            out.write(f"| {project} | {libs_str} |\n")
        out.write("\n")

    if accelerator:
        out.write(f"### AI accelerator-specific ({len(accelerator)} packages)\n\n")
        out.write(
            "Depend on CUDA, ROCm, or PyTorch runtime libraries.\n"
            "These must be provided by the accelerator platform.\n\n"
        )
        out.write("| Package | Additional libraries |\n")
        out.write("|:---|:---|\n")
        for project in sorted(accelerator):
            libs = accelerator[project]
            libs_str = ", ".join(sorted(libs)) if libs else ""
            out.write(f"| {project} | {libs_str} |\n")
        out.write("\n")

    if has_unbundleable:
        out.write(f"### Unbundleable external dependencies ({len(has_unbundleable)} packages)\n\n")
        out.write(
            "At least one external dep must never be bundled (crypto,\n"
            "system runtime, etc.) and must be provided by the platform.\n"
            "This includes indirect dependencies (e.g. libmariadb depends\n"
            "on OpenSSL, libpq depends on OpenSSL + Kerberos).\n\n"
        )
        out.write("| Package | Libraries |\n")
        out.write("|:---|:---|\n")
        for project in sorted(has_unbundleable):
            libs = has_unbundleable[project]
            never = sorted(libs & _NEVER_BUNDLE_LIBS)
            rest = sorted(libs - _NEVER_BUNDLE_LIBS)
            parts = ", ".join(never)
            if rest:
                parts += " (+ " + ", ".join(rest) + ")"
            out.write(f"| {project} | {parts} |\n")
        out.write("\n")

    if undecided:
        out.write(f"### Undecided external dependencies ({len(undecided)} packages)\n\n")
        out.write(
            "All external deps are known but not yet classified as\n"
            "bundleable or unbundleable.\n\n"
        )
        out.write("| Package | Libraries |\n")
        out.write("|:---|:---|\n")
        for project in sorted(undecided):
            libs_str = ", ".join(sorted(undecided[project]))
            out.write(f"| {project} | {libs_str} |\n")
        out.write("\n")

    if unknown_external:
        out.write(f"### Unknown external dependencies ({len(unknown_external)} packages)\n\n")
        out.write("External deps not present in any classification list.\n\n")
        out.write("| Package | Count | Libraries |\n")
        out.write("|:---|---:|:---|\n")
        for project in sorted(unknown_external):
            libs = unknown_external[project]
            libs_str = ", ".join(sorted(libs))
            out.write(f"| {project} | {len(libs)} | {libs_str} |\n")
        out.write("\n")

    out.write(
        f"**Total:** {total} packages with ELF dependencies"
        f" ({len(manylinux_only)} manylinux-only,"
        f" {len(could_bundle)} bundleable,"
        f" {len(accelerator)} accelerator,"
        f" {len(has_unbundleable)} unbundleable,"
        f" {len(undecided)} undecided,"
        f" {len(unknown_external)} unknown)\n"
    )
    return out.getvalue()


def analyze_elf(search_dir: pathlib.Path) -> str | None:
    """Run ELF analysis on a directory tree.

    Returns a combined report with three sections:

    1. External dependencies -- libraries not provided by any wheel and
       not in the manylinux baseline.
    2. Inter-wheel dependencies -- libraries provided by one wheel and
       consumed by another.
    3. Dependency complexity -- packages classified by bundleability
       of their external library dependencies.

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

    complexity = _format_dependency_complexity_report(requires, provided_libs)
    if complexity:
        parts.append(complexity)

    return "\n\n".join(parts) if parts else None


def _load_wheel_counts(index_dir: pathlib.Path) -> dict[str, list[str]] | None:
    """Load cached wheel counts from an index directory."""
    path = index_dir / WHEEL_COUNTS_FILE
    if not path.is_file():
        return None
    return json.loads(path.read_text())


def _find_no_elf_packages(
    wheel_counts: dict[str, list[str]] | None,
    requires: dict[str, set[str]],
) -> tuple[list[str], list[str]]:
    """Return platlib package names that have no ELF requires data.

    Returns ``(manylinux_packages, other_packages)`` -- pre-built
    upstream wheels with manylinux tags are listed separately from
    packages that lack any manylinux tag.
    """
    platlib = set(wheel_counts["platlib_packages"]) if wheel_counts else set()
    manylinux = set(wheel_counts.get("manylinux_packages", [])) if wheel_counts else set()
    has_elf: set[str] = set()
    for projects in requires.values():
        has_elf.update(projects)
    no_elf = platlib - has_elf
    return sorted(no_elf & manylinux), sorted(no_elf - manylinux)


class IndexStats(typing.TypedDict):
    """Wheel and ELF classification statistics for an index."""

    n_pure: int       # pure-Python (purelib) packages
    n_plat: int       # platform-specific (platlib) packages
    n_total: int      # n_pure + n_plat
    n_ml: int         # manylinux-only (no external deps beyond baseline)
    n_bun: int        # could become manylinux by bundling external deps
    n_accel: int      # depend on AI accelerator (CUDA/ROCm) runtime
    n_unbun: int      # at least one unbundleable external dep
    n_undec: int      # external deps not yet classified
    n_unk: int        # external deps not in any classification list
    n_elf: int        # total platlib packages with ELF data
    n_ml_bun: int     # n_ml + n_bun (portable native packages)
    n_platform: int   # n_accel + n_unbun + n_undec + n_unk
    n_no_elf_ml: int  # platlib without ELF data, pre-built manylinux
    n_no_elf_other: int  # platlib without ELF data, other


def _compute_index_stats(
    wheel_counts: dict[str, list[str]] | None,
    provides: dict[str, set[str]],
    requires: dict[str, set[str]],
) -> IndexStats:
    """Compute wheel and ELF classification statistics for an index."""
    purelib = set(wheel_counts["purelib_packages"]) if wheel_counts else set()
    platlib = set(wheel_counts["platlib_packages"]) if wheel_counts else set()
    manylinux = set(wheel_counts.get("manylinux_packages", [])) if wheel_counts else set()
    # packages with both pure and platlib wheels count as platlib
    purelib -= platlib
    n_pure = len(purelib)
    n_plat = len(platlib)
    n_total = n_pure + n_plat

    n_ml = n_bun = n_accel = n_unbun = n_undec = n_unk = 0
    n_elf = n_ml_bun = n_platform = 0

    if requires:
        cl = _classify_projects(requires, set(provides))
        n_ml = len(cl["manylinux_only"])
        n_bun = len(cl["could_bundle"])
        n_accel = len(cl["accelerator"])
        n_unbun = len(cl["has_unbundleable"])
        n_undec = len(cl["undecided"])
        n_unk = len(cl["unknown_external"])
        n_elf = n_ml + n_bun + n_accel + n_unbun + n_undec + n_unk
        n_ml_bun = n_ml + n_bun
        n_platform = n_accel + n_unbun + n_undec + n_unk

    # Platlib packages without ELF data, split by manylinux tag
    has_elf: set[str] = set()
    for projects in requires.values():
        has_elf.update(projects)
    no_elf = platlib - has_elf
    no_elf_ml = no_elf & manylinux
    n_no_elf_ml = len(no_elf_ml)
    n_no_elf_other = len(no_elf) - n_no_elf_ml

    return {
        "n_pure": n_pure,
        "n_plat": n_plat,
        "n_total": n_total,
        "n_ml": n_ml,
        "n_bun": n_bun,
        "n_accel": n_accel,
        "n_unbun": n_unbun,
        "n_undec": n_undec,
        "n_unk": n_unk,
        "n_elf": n_elf,
        "n_ml_bun": n_ml_bun,
        "n_platform": n_platform,
        "n_no_elf_ml": n_no_elf_ml,
        "n_no_elf_other": n_no_elf_other,
    }


def _format_index_summary(
    stats: IndexStats,
) -> str:
    """Format wheel and ELF classification stats as a Markdown table."""
    def _pct(n: int, base: int) -> str:
        return f"{100 * n / base:.1f}%" if base else "-"

    n_total = stats["n_total"]
    n_pure = stats["n_pure"]
    n_plat = stats["n_plat"]

    rows: list[tuple[str, str, str]] = [
        ("**Total packages**", f"**{n_total}**", ""),
        ("&ensp;Purelib (pure Python)", str(n_pure), _pct(n_pure, n_total)),
        ("&ensp;Platlib (native code)", str(n_plat), _pct(n_plat, n_total)),
    ]

    n_elf = stats["n_elf"]
    if n_elf:
        n_ml = stats["n_ml"]
        n_bun = stats["n_bun"]
        n_no_elf_ml = stats["n_no_elf_ml"]
        n_no_elf_other = stats["n_no_elf_other"]
        n_portable_ml = stats["n_ml_bun"] + n_no_elf_ml
        n_platform = stats["n_platform"]
        n_accel = stats["n_accel"]
        n_unbun = stats["n_unbun"]
        n_undec = stats["n_undec"]
        n_unk = stats["n_unk"]
        rows.extend([
            ("&ensp;Manylinux + bundleable", str(n_portable_ml), _pct(n_portable_ml, n_total)),
            ("&ensp;&ensp;Manylinux-only", str(n_ml), _pct(n_ml, n_total)),
            ("&ensp;&ensp;Could be bundled", str(n_bun), _pct(n_bun, n_total)),
        ])
        if n_no_elf_ml:
            rows.append(
                ("&ensp;&ensp;Pre-built (manylinux)", str(n_no_elf_ml), _pct(n_no_elf_ml, n_total)),
            )
        rows.extend([
            ("&ensp;Platform-dependent", str(n_platform), _pct(n_platform, n_total)),
            ("&ensp;&ensp;Accelerator-specific", str(n_accel), _pct(n_accel, n_total)),
            ("&ensp;&ensp;Unbundleable", str(n_unbun), _pct(n_unbun, n_total)),
            ("&ensp;&ensp;Undecided", str(n_undec), _pct(n_undec, n_total)),
            ("&ensp;&ensp;Unknown", str(n_unk), _pct(n_unk, n_total)),
        ])
        if n_no_elf_other:
            rows.append(
                ("&ensp;No ELF data (other)", str(n_no_elf_other), _pct(n_no_elf_other, n_total)),
            )
        n_portable = n_pure + n_portable_ml
        n_other = n_total - n_portable
        rows.extend([
            ("**Purelib + manylinux + bundleable**", f"**{n_portable}**", f"**{_pct(n_portable, n_total)}**"),
            ("**Platform/accel + other**", f"**{n_other}**", f"**{_pct(n_other, n_total)}**"),
        ])

    out = io.StringIO()
    out.write("| Category | Count | % |\n")
    out.write("|:---|---:|---:|\n")
    for cat, count, pct in rows:
        out.write(f"| {cat} | {count} | {pct} |\n")
    return out.getvalue()


def _format_mermaid_charts(
    index_name: str,
    stats: IndexStats,
) -> str | None:
    """Produce a Mermaid bar chart for the index summary.

    Uses xychart-beta with the Wong color-blind safe palette.
    Returns None when there is no ELF data to chart.
    """
    n_total = stats["n_total"]
    n_elf = stats["n_elf"]
    if not n_total or not n_elf:
        return None

    # Wong color-blind safe palette
    # Pre-built manylinux wheels without ELF data count as portable
    n_portable_ml = stats["n_ml_bun"] + stats["n_no_elf_ml"]
    segments = [
        ("purelib", stats["n_pure"], "#0072B2"),
        ("manylinux + bundleable", n_portable_ml, "#009E73"),
        ("platform/accel", stats["n_platform"], "#D55E00"),
        ("no ELF data (other)", stats["n_no_elf_other"], "#999999"),
    ]
    segments = [(l, v, c) for l, v, c in segments if v]
    if not segments:
        return None

    labels, values, colors = zip(*segments)
    palette = ", ".join(colors)
    init = json.dumps({
        "theme": "base",
        "themeVariables": {"xyChart": {"plotColorPalette": palette}},
    })

    out = io.StringIO()
    out.write("```mermaid\n")
    out.write(f"%%{{init: {init}}}%%\n")
    out.write("xychart-beta\n")
    out.write(f'    title "{index_name} -- package overview"\n')
    x_axis = ", ".join(f'"{l}"' for l in labels)
    out.write(f"    x-axis [{x_axis}]\n")
    out.write('    y-axis "Packages"\n')
    bar_vals = ", ".join(str(v) for v in values)
    out.write(f"    bar [{bar_vals}]\n")
    out.write("```\n")

    return out.getvalue()


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Analyze ELF shared library deps from RHOAI wheel metadata",
    )
    ap.add_argument(
        "version",
        nargs="?",
        default="3.6-EA1",
        help="RHOAI index version (default: 3.6-EA1)",
    )
    args = ap.parse_args()

    version: str = args.version
    base_dir = pathlib.Path("data") / f"rhoai-{version}"

    if not base_dir.is_dir():
        tqdm.write(f"No local data found at {base_dir}")
        tqdm.write("Run fetch-wheel-metadata.py first to fetch wheel data.")
        return

    # Run ELF analysis and summary per index
    for index_dir in sorted(base_dir.iterdir()):
        if not index_dir.is_dir():
            continue
        provides, requires = _collect_elf_data(index_dir)
        if not requires:
            tqdm.write(f"[{index_dir.name}] no ELF requires data")
            continue
        provided_libs = set(provides)
        wc = _load_wheel_counts(index_dir)
        stats = _compute_index_stats(wc, provides, requires)
        summary = _format_index_summary(stats)
        charts = _format_mermaid_charts(index_dir.name, stats)

        md = io.StringIO()
        md.write(f"# ELF Analysis: {index_dir.name}\n\n")
        md.write(f"## Summary\n\n{summary}\n")
        if charts:
            md.write(f"## Charts\n\n{charts}\n")
        ext = _format_external_report(requires, provided_libs)
        if ext:
            md.write(f"## External Dependencies\n\n{ext}\n")
        inter = _format_inter_wheel_report(provides, requires)
        if inter:
            md.write(f"## Inter-wheel Dependencies\n\n{inter}\n")
        complexity = _format_dependency_complexity_report(requires, provided_libs)
        if complexity:
            md.write(f"## Dependency Complexity\n\n{complexity}\n")
        no_elf_ml, no_elf_other = _find_no_elf_packages(wc, requires)
        if no_elf_ml or no_elf_other:
            n = len(no_elf_ml) + len(no_elf_other)
            md.write(f"## Packages without ELF Data ({n})\n\n")
            md.write(
                "Platlib packages that ship platform-specific wheels but have no\n"
                "fromager-elf-requires/provides metadata. These are typically\n"
                "pre-built upstream wheels, proprietary binary blobs, packages\n"
                "with optional C extensions, or packages built without fromager\n"
                "instrumentation.\n\n"
            )
            if no_elf_ml:
                md.write(f"**Pre-built manylinux ({len(no_elf_ml)}):** ")
                md.write(", ".join(no_elf_ml) + "\n\n")
            if no_elf_other:
                md.write(f"**Other ({len(no_elf_other)}):** ")
                md.write(", ".join(no_elf_other) + "\n\n")

        dest = index_dir / "elf-analysis.md"
        dest.write_text(md.getvalue())
        tqdm.write(f"[{index_dir.name}] wrote {dest}")

    # Combined analysis across all indexes
    # Aggregate wheel counts across all indexes (union of package names)
    all_purelib: set[str] = set()
    all_platlib: set[str] = set()
    all_manylinux: set[str] = set()
    for index_dir in sorted(base_dir.iterdir()):
        if not index_dir.is_dir():
            continue
        wc = _load_wheel_counts(index_dir)
        if wc:
            all_purelib.update(wc["purelib_packages"])
            all_platlib.update(wc["platlib_packages"])
            all_manylinux.update(wc.get("manylinux_packages", []))
    combined_wc: dict[str, list[str]] | None = None
    if all_purelib or all_platlib:
        combined_wc = {
            "purelib_packages": sorted(all_purelib),
            "platlib_packages": sorted(all_platlib),
            "manylinux_packages": sorted(all_manylinux),
        }

    provides, requires = _collect_elf_data(base_dir)
    provided_libs = set(provides)
    stats = _compute_index_stats(combined_wc, provides, requires)
    summary = _format_index_summary(stats)
    charts = _format_mermaid_charts("combined", stats)

    md = io.StringIO()
    md.write("# ELF Analysis: combined\n\n")
    md.write(f"## Summary\n\n{summary}\n")
    if charts:
        md.write(f"## Charts\n\n{charts}\n")

    if requires:
        ext = _format_external_report(requires, provided_libs)
        if ext:
            md.write(f"## External Dependencies\n\n{ext}\n")
        inter = _format_inter_wheel_report(provides, requires)
        if inter:
            md.write(f"## Inter-wheel Dependencies\n\n{inter}\n")
        complexity = _format_dependency_complexity_report(requires, provided_libs)
        if complexity:
            md.write(f"## Dependency Complexity\n\n{complexity}\n")

    no_elf_ml, no_elf_other = _find_no_elf_packages(combined_wc, requires)
    if no_elf_ml or no_elf_other:
        n = len(no_elf_ml) + len(no_elf_other)
        md.write(f"## Packages without ELF Data ({n})\n\n")
        md.write(
            "Platlib packages that ship platform-specific wheels but have no\n"
            "fromager-elf-requires/provides metadata. These are typically\n"
            "pre-built upstream wheels, proprietary binary blobs, packages\n"
            "with optional C extensions, or packages built without fromager\n"
            "instrumentation.\n\n"
        )
        if no_elf_ml:
            md.write(f"**Pre-built manylinux ({len(no_elf_ml)}):** ")
            md.write(", ".join(no_elf_ml) + "\n\n")
        if no_elf_other:
            md.write(f"**Other ({len(no_elf_other)}):** ")
            md.write(", ".join(no_elf_other) + "\n\n")

    dest = base_dir / "elf-analysis.md"
    dest.write_text(md.getvalue())
    tqdm.write(f"\nWrote combined analysis: {dest}")

    tqdm.write("Done.")


if __name__ == "__main__":
    main()
