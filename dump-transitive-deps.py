#!/usr/bin/env python3
"""Dump transitive shared library dependencies for vendor/bundleable libraries.

Finds each library on the local system via ldconfig, runs ldd to collect
transitive dependencies, and flags any that are unbundleable (crypto,
accelerator, system runtime, etc.).  Manylinux baseline libraries are
filtered out.

Usage::

    python3 dump-transitive-deps.py
    python3 dump-transitive-deps.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

# Libraries to check -- vendor + bundleable from policy.toml / analyze-elf-deps.py
_CHECK_LIBS = [
    # vendor: text processing
    "libre2.so.9",
    "libutf8proc.so.2",
    # vendor: data formats
    "libthrift-0.15.0.so",
    # vendor: misc
    "libev.so.4",
    "libloguru.so.2",
    "libyaml-0.so.2",
    # bundleable: math / science
    "libgfortran.so.5",
    "libqhull_r.so.7",
    # bundleable: color management
    "liblcms2.so.2",
    # bundleable: database clients / archive / messaging
    # (transitively depend on security libs, bundled copies use system OpenSSL)
    "libmariadb.so.3",
    "libpq.so.5",
    "libzip.so.5",
    "libzmq.so.5",
    # bundleable: misc
    "libtbb.so.2",
]

# Manylinux baseline + dynamic linkers -- always available, skip these
_MANYLINUX = {
    "ld-linux-aarch64.so.1",
    "ld-linux-x86-64.so.2",
    "ld64.so.1",
    "ld64.so.2",
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
    "linux-vdso.so.1",
}

# Libraries that must never be bundled -- flag these in output
_UNBUNDLEABLE = {
    # crypto / auth
    "libcrypto.so.3",
    "libcrypt.so.2",
    "libssl.so.3",
    "libgssapi_krb5.so.2",
    "libk5crypto.so.3",
    "libkeyutils.so.1",
    "libkrb5.so.3",
    "libkrb5support.so.0",
    "libcom_err.so.2",
    # SASL / LDAP / NSS
    "libsasl2.so.3",
    "libldap.so.2",
    "liblber.so.2",
    "libnss3.so",
    "libnssutil3.so",
    "libnspr4.so",
    # SELinux
    "libselinux.so.1",
    # CUDA
    "libcuda.so.1",
    "libcudart.so.12",
    "libcudart.so.13",
    "libcudnn.so.9",
    # ROCm
    "libamdhip64.so.7",
    "libhsa-runtime64.so.1",
    # MPI
    "libmpi.so.40",
    "libmpi_cxx.so.40",
    # math / science
    "libgmp.so.10",
    "libgomp.so.1",
    "libopenblaso.so.0",
    "libopenblasp.so.0",
    # FFmpeg / multimedia
    "libavcodec.so.60",
    "libavdevice.so.60",
    "libavfilter.so.9",
    "libavformat.so.60",
    "libavutil.so.58",
    "libswresample.so.4",
    "libswscale.so.7",
    # image codecs (system)
    "libjbig.so.2.1",
    "libjpeg.so.62",
    "libpng16.so.16",
    "libopenjp2.so.7",
    "libtiff.so.5",
    "libwebp.so.7",
    "libwebpdemux.so.2",
    "libwebpmux.so.3",
    # XML / XSLT
    "libexslt.so.0",
    "libxml2.so.2",
    "libxslt.so.1",
    # compression
    "libbz2.so.1",
    "liblz4.so.1",
    "liblzma.so.5",
    "libsnappy.so.1",
    "libzstd.so.1",
    # system
    "libffi.so.8",
    "libpython3.12.so.1.0",
    "libsqlite3.so.0",
    "libnuma.so.1",
    "libaio.so.1",
    "libunwind.so.8",
    "libfreetype.so.6",
    "libncurses.so.6",
    "libtinfo.so.6",
    "libtirpc.so.3",
    # GIS
    "libgeos_c.so.1",
    "libproj.so.25",
    # ICU
    "libicui18n.so.67",
    "libicuuc.so.67",
    # data formats
    "libcurl.so.4",
    "libeccodes.so.0.1",
    "libgdal.so.36",
    "libhdf5.so.310",
    "libhdf5_hl.so.310",
    "libnetcdf.so.19",
    "libodbc.so.2",
    # OCR
    "liblept.so.5",
    "libtesseract.so.4",
}

_LDD_LINE_RE = re.compile(r"^\s+(\S+)\s+=>\s+(\S+)")
_LDD_DIRECT_RE = re.compile(r"^\s+(/\S+)\s+\(0x")


def _build_ldconfig_map() -> dict[str, str]:
    """Parse ldconfig -p to build soname -> path mapping."""
    result = subprocess.run(
        ["ldconfig", "-p"], capture_output=True, text=True, check=True
    )
    mapping: dict[str, str] = {}
    for line in result.stdout.splitlines():
        # format: "    libfoo.so.1 (libc6,x86-64) => /lib64/libfoo.so.1"
        m = re.match(r"\s+(\S+)\s+\(.*\)\s+=>\s+(\S+)", line)
        if m:
            soname, path = m.group(1), m.group(2)
            if soname not in mapping:
                mapping[soname] = path
    return mapping


def _run_ldd(path: str) -> list[tuple[str, str]]:
    """Run ldd and return [(soname, path), ...]."""
    env = dict(os.environ)
    env.pop("LD_PRELOAD", None)
    result = subprocess.run(
        ["ldd", path], capture_output=True, text=True, env=env, check=False
    )
    deps: list[tuple[str, str]] = []
    for line in result.stdout.splitlines():
        m = _LDD_LINE_RE.match(line)
        if m:
            deps.append((m.group(1), m.group(2)))
            continue
        m = _LDD_DIRECT_RE.match(line)
        if m:
            path_str = m.group(1)
            name = path_str.rsplit("/", 1)[-1]
            deps.append((name, path_str))
    return deps


def _soname(name: str) -> str:
    """Normalize soname: strip minor version suffixes for matching.

    libgeos.so.3.13.1 -> libgeos.so.3 (but keep full name for display).
    """
    # Match libfoo.so.X.Y.Z and return libfoo.so.X
    m = re.match(r"(.*\.so\.\d+)\.\d+", name)
    return m.group(1) if m else name


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--json", action="store_true", help="output as JSON"
    )
    args = ap.parse_args()

    ldmap = _build_ldconfig_map()

    results: dict[str, dict] = {}
    not_found: list[str] = []

    for lib in _CHECK_LIBS:
        path = ldmap.get(lib)
        if not path:
            not_found.append(lib)
            continue

        deps = _run_ldd(path)
        transitive: list[str] = []
        flagged: list[str] = []
        for dep_name, dep_path in deps:
            if dep_name in _MANYLINUX or dep_name == lib:
                continue
            normalized = _soname(dep_name)
            if normalized in _MANYLINUX:
                continue
            transitive.append(dep_name)
            if dep_name in _UNBUNDLEABLE or normalized in _UNBUNDLEABLE:
                flagged.append(dep_name)

        results[lib] = {
            "path": path,
            "transitive": sorted(transitive),
            "flagged": sorted(flagged),
        }

    if args.json:
        out = {"results": results, "not_found": not_found}
        json.dump(out, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return

    for lib in _CHECK_LIBS:
        if lib in not_found:
            print(f"\n{lib}: NOT FOUND")
            continue
        info = results[lib]
        transitive = info["transitive"]
        flagged = info["flagged"]
        if not transitive:
            print(f"\n{lib}: OK (manylinux-only deps)")
            continue
        marker = " ** UNBUNDLEABLE **" if flagged else ""
        print(f"\n{lib}: {len(transitive)} transitive deps{marker}")
        for dep in transitive:
            flag = " <-- UNBUNDLEABLE" if dep in flagged or _soname(dep) in flagged else ""
            print(f"  {dep}{flag}")

    if not_found:
        print(f"\n--- {len(not_found)} libraries not found on this system ---")
        for lib in not_found:
            print(f"  {lib}")


if __name__ == "__main__":
    main()
