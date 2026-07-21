# Downstream Build-System Patches Analysis

Comparison of `fromager-build-system-requirements.txt` (from RHOAI 3.5
cpu-ubi9-test wheels) with `build-system.requires` from upstream PyPI
sdists. Out of 2,326 comparable package-versions, 98 have differences.

These are **not** PEP 517 dynamic build requirements. They are
intentional build-system modifications made by fromager / Red Hat
downstream patches.

## Extra deps added downstream

Dependencies present in `fromager-build-system-requirements.txt` but
absent from upstream `pyproject.toml` `build-system.requires`.

### setuptools (unversioned)

Added as a generic build compatibility shim. Downstream policy to
ensure setuptools is always available regardless of what the upstream
build backend expects.

Packages (25): daft, jupyter_bokeh, ninja, onnx, pandas, pyarrow,
pydantic-core, and others.

```
# pandas 2.2.3
# upstream: meson-python==0.13.1, meson==1.2.1, wheel, Cython~=3.0.5, numpy>=2.0, versioneer[toml]
# downstream adds: setuptools
```

### filelock

Added for build-time locking in parallel build environments.
vllm-specific downstream requirement.

Packages (9): vllm (all rhaiv variants).

```
# vllm 0.24.0+rhaiv.2
# upstream: cmake>=3.26.1, ninja, packaging>=24.2, setuptools>=77.0.3,<81.0.0,
#           setuptools-scm>=8.0, setuptools-rust>=1.9.0, torch==2.11.0, wheel, jinja2
# downstream adds: filelock, setuptools (unversioned)
# downstream removes: cmake>=3.26.1
# downstream changes: torch==2.11.0 -> torch (unpinned)
```

### build

Build bootstrapper module added downstream.

Packages (4): pyarrow.

```
# pyarrow 24.0.0
# upstream: scikit-build-core, cython>=3.1, libcst>=1.8.6, numpy>=1.25, setuptools_scm[toml]>=8
# downstream adds: build, setuptools
```

### flit-scm (replaces flit-core)

Complete build backend swap from plain `flit-core` to `flit-scm` for
SCM-based versioning.

Packages (4): garak (rhaiv variants).

```
# garak 0.15.0+rhaiv.5
# upstream: flit_core>=3.11,<4
# downstream: flit-scm<2,>=1.7.0
```

### nanobind, pybind11

C++ binding tools added for downstream native rebuilds.

Packages (4): onnx.

```
# onnx 1.19.1
# upstream: setuptools>=64, protobuf>=4.25.1
# downstream adds: pybind11[global], nanobind, setuptools (unversioned)
```

### typing-extensions

Added for maturin-based Rust builds on older Python.

Packages (3): pydantic-core.

### setuptools-scm (replaces scikit-build-core)

Complete build backend swap from `scikit-build-core` to setuptools.

Packages (2): ninja.

```
# ninja 1.11.1.4
# upstream: scikit-build-core>=0.10
# downstream: setuptools>60, setuptools_scm>8
```

### scikit-build-core (replaces setuptools)

Build system upgrade from plain setuptools to scikit-build-core.

Packages (1): faiss-cpu.

```
# faiss-cpu 1.12.0
# upstream: setuptools, wheel, numpy>=2.0,<3
# downstream: scikit-build-core>=0.10, numpy<3.0,>=2.0, setuptools
# downstream removes: wheel
```

### cython

Added to build Cython extensions not required upstream.

Packages (1): yarl.

### meson (version constraint change)

Not a new dependency. Version constraint loosened from pinned to range.

Packages (1): pandas.

```
# pandas 2.2.3
# upstream: meson==1.2.1
# downstream: meson<1.11.0,>=1.2.1
```

## Deps removed downstream

Dependencies present in upstream `pyproject.toml` `build-system.requires`
but absent from `fromager-build-system-requirements.txt`.

### tomli

Python < 3.11 backport of `tomllib`. Correctly stripped because
downstream builds target Python 3.11+ where `tomllib` is in the
standard library. These are typically declared with a marker like
`tomli; python_version < "3.11"` and fromager resolves markers for the
target platform.

Packages (36): setuptools-scm, meson-python, maturin, numpy, mypy,
apache-airflow, and others.

### typing-extensions

Similarly a conditional dependency for older Python versions, stripped
for the same reason as tomli.

Packages (13): setuptools-scm, vcs-versioning, soxr, and others.

### cmake

System-provided cmake used instead of the Python package. Downstream
builds rely on the system cmake binary rather than pulling it as a
Python build dependency.

Packages (9): vllm (all rhaiv variants).

### jupyterlab

Build dependency omitted for Jupyter extension packages. Downstream
likely uses pre-built frontend assets rather than rebuilding JavaScript
at wheel build time.

Packages (7): bqplot, ipyevents, ipytree, jupyter-leaflet,
jupyter_bokeh, jupyterlab_pygments.

### ctypesgen

Dropped downstream, likely replaced by pre-generated bindings.

Packages (5): pypdfium2.

### flit-core

Replaced by flit-scm in garak (see above).

Packages (4): garak (rhaiv variants).

### scikit-build-core

Replaced by setuptools in ninja (see above).

Packages (2): ninja.

### Other single removals

- **colorama** -- numpy 1.26.2 (Windows-only dependency)
- **oldest-supported-numpy** -- pyarrow 20.0.0 (deprecated meta-package)
- **cffi** -- pyzmq 27.1.0 (conditional on implementation)
- **importlib-metadata** -- setuptools-scm 8.3.0 (Python < 3.8 backport)
- **wheel** -- faiss-cpu 1.12.0 (replaced by scikit-build-core)

## Categories of downstream changes

### 1. Marker-conditional dep stripping (tomli, typing-extensions, colorama, importlib-metadata)

Fromager resolves environment markers for the target Python version
and platform. Dependencies guarded by `python_version < "3.11"` or
`sys_platform == "win32"` are correctly omitted. This is expected
behavior, not a gap.

### 2. Complete backend swaps (ninja, garak, faiss-cpu)

The upstream build backend is replaced entirely with a different one.
These are deliberate downstream engineering decisions that cannot be
predicted from upstream source analysis.

- ninja: scikit-build-core -> setuptools + setuptools-scm
- garak: flit-core -> flit-scm
- faiss-cpu: setuptools + wheel -> scikit-build-core + setuptools

### 3. System tool substitution (cmake in vllm)

Python-packaged build tools (cmake, ninja) are replaced by
system-installed binaries. The Python packages are removed from
build-system.requires because the system provides them.

### 4. Extra native build tools (onnx, vllm)

Additional C/C++/Rust binding tools or build utilities are added
for downstream native rebuilds that differ from upstream's build
process.

- onnx: adds pybind11, nanobind
- vllm: adds filelock

### 5. Policy additions (setuptools, build)

Unversioned `setuptools` or `build` added as a safety net. Downstream
policy to ensure core build tools are always explicitly declared.

### 6. Version constraint changes (pandas/meson, vllm/torch)

Existing dependencies have their version constraints modified:
- Loosened: `meson==1.2.1` -> `meson>=1.2.1,<1.11.0`
- Unpinned: `torch==2.11.0` -> `torch`

## Relationship to sdist-analyzer

These downstream patches are a **different category** from the PEP 517
dynamic build requirements that sdist-analyzer is designed to detect.
sdist-analyzer analyzes upstream source to identify what
`get_requires_for_build_wheel()` would return at build time (patchelf
for mesonpy, hatch-jupyter-builder for hatchling hooks, cffi for
maturin, etc.).

Downstream patches are intentional build-system modifications that
cannot be discovered from upstream source alone. They represent
engineering decisions about how to rebuild packages in a controlled
environment with specific system-level tooling.

The marker-conditional stripping (tomli, typing-extensions) is correct
behavior and validates that fromager properly resolves markers rather
than blindly copying requirements.
