# Open Questions

## uv / uv-build: libbz2, liblzma dependencies

uv 0.11.x wheels built by fromager on UBI9 depend on `libbz2.so.1` and
`liblzma.so.5`.  Upstream PyPI wheels are fully statically linked.

**Root cause**: The Rust crates `bzip2-sys` and `lzma-sys` (pulled in via
`async-compression` features `bzip2` and `xz`) use `pkg-config` to detect
system libraries.  Upstream builds in a minimal `manylinux2014` (CentOS 7)
container without `-devel` packages, so the crates compile their bundled C
sources statically.  The fromager UBI9 build environment has `bzip2-devel`
and `xz-devel` installed, so `pkg-config` finds the shared libraries and
links dynamically.

**Status**: Fixed upstream in uv 0.12.0 (PR
[#18927](https://github.com/astral-sh/uv/pull/18927)) -- `bzip2` and `xz`
features were removed from `async-compression`.  Neither `bzip2-sys` nor
`lzma-sys` appear in the dependency tree for uv 0.12.0+.

**Workaround for 0.11.x**: Set `BZIP2_NO_PKG_CONFIG=1` and
`LZMA_API_STATIC=1` in the build environment to force static linking, or
remove `bzip2-devel` / `xz-devel` from the build container.

## Bundle libev.so?

`cassandra-driver` depends on `libev.so.4`.  libev is a small, stable event
loop library with no transitive dependencies beyond libc.  Bundling is
technically feasible but needs investigation into whether cassandra-driver
can be built with its pure-Python event loop fallback instead.

## Bundle libffi.so?

`cffi` and `pandoc-rhai` depend on `libffi.so.8`.  libffi is a low-level
foreign function interface library.  It is architecture-specific and
tightly coupled to the platform ABI.  Bundling is likely impractical --
libffi should probably be classified as unbundleable (system runtime).

## Bundle HDF5?

`h5py` depends on `libhdf5.so.310` and `libhdf5_hl.so.310`.  HDF5 is a
large library with optional dependencies (MPI, compression filters, etc.).
Bundling is technically possible but the resulting wheel would be large.
Upstream h5py wheels on PyPI bundle HDF5.  Needs decision on whether to
follow upstream's approach or require system HDF5.

## Bundle libxml2 / libxslt / libexslt?

`lxml` depends on `libxml2.so.2`, `libxslt.so.1`, and `libexslt.so.0`.
Upstream lxml wheels on PyPI bundle these libraries.  libxml2/libxslt have
a history of security vulnerabilities, which argues for using
system-provided versions.  Needs decision on security policy vs.
portability.
