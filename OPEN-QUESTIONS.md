# Open Questions

*No open questions at this time.*

## Resolved

### uv / uv-build: libbz2, liblzma dependencies

Fixed upstream in uv 0.12.0 (PR
[#18927](https://github.com/astral-sh/uv/pull/18927)) -- `bzip2` and `xz`
features removed from `async-compression`.  For 0.11.x, set
`BZIP2_NO_PKG_CONFIG=1` / `LZMA_API_STATIC=1` or remove `-devel` packages.

**Decision**: libbz2, liblzma classified as system (not bundled).

### libev.so

**Decision**: bundleable.  Small, stable, no transitive deps beyond libc.
cassandra-driver would become manylinux by bundling it.

### libffi.so

**Decision**: system (not bundled).  Always present because Python's
ctypes module depends on it.

### HDF5 (libhdf5, libhdf5_hl)

**Decision**: system (not bundled).  Large, may need MPI variant.
libnetcdf and libgdal also depend on it.

### libxml2 / libxslt / libexslt

**Decision**: system (not bundled).  Security-sensitive libraries,
use system-provided versions.

### Image codecs (libjpeg, libpng, libtiff, libwebp, liblcms2, libopenjp2)

**Decision**: system (not bundled).  Used by multiple packages (Pillow,
opencv, torchvision, docling-parse), provide consistent versions
across the index.

### libfreetype

**Decision**: system (not bundled).  Transitively depends on
libharfbuzz, libpng, libbz2, libbrotli.

### libgeos_c / libproj

**Decision**: system (not bundled).  libgeos_c requires libgeos
(large C++ geometry engine).  libproj transitively depends on
libcurl -> libssl / libkrb5.

### libeccodes

**Decision**: system (not bundled).  Transitively depends on libgomp
(OpenMP, unbundleable).

### Compression libraries (libbz2, liblz4, liblzma, libsnappy, libzstd)

**Decision**: system (not bundled).  Typically available on all systems.

### libmariadb, libpq, libzip, libzmq

**Decision**: bundleable.  Transitively depend on security libraries
(libssl, libkrb5) but bundled copies link against system OpenSSL/Kerberos
at runtime.

### libgfortran, libqhull_r

**Decision**: bundleable.

### ICU (libicui18n, libicuuc)

**Decision**: system (not bundled).  Too large to bundle (~30 MB
libicudata).  Typically available on systems where gdb is installed.
