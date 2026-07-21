# Extra Build-Backend Dependencies Analysis

Analysis of packages in `rhoai/3.5/cpu-ubi9-test` where
`fromager-build-backend-requirements.txt` contains additional packages
not listed in `fromager-build-system-requirements.txt`.

These are **PEP 517 dynamic build requirements** -- dependencies returned
by `get_requires_for_build_wheel()` or `get_requires_for_build_sdist()`
that are not statically declared in `build-system.requires`.

## patchelf

**Trigger:** `build-backend = "mesonpy"` in pyproject.toml.

Meson-python's `get_requires_for_build_wheel()` dynamically adds
`patchelf` on Linux to fix ELF RPATH entries in compiled extensions.

Packages: array-api-compat, contourpy, cysignals, matplotlib,
meson-python, numpy, pandas, PyWavelets, scikit-image, scikit-learn,
scipy.

```toml
# numpy 2.1.0 pyproject.toml
[build-system]
build-backend = "mesonpy"
requires = ["meson-python>=0.15.0", "Cython>=3.0.6"]
```

## hatch-jupyter-builder

**Trigger:** `build-backend = "hatchling.build"` with a
`[tool.hatch.build.hooks.jupyter-builder]` section in pyproject.toml.

The hatch hook compiles JavaScript/TypeScript frontend assets into the
Python package. The `dependencies` key inside the hook section declares
`hatch-jupyter-builder` as a build-time requirement.

Packages: anywidget, bqscales, ipyevents, jupyter-collaboration-ui,
jupyter-docprovider, jupyter-leaflet, jupyter-resource-usage,
jupyter_ai_acp_client, jupyter_ai_chat_commands,
jupyter_ai_persona_manager, jupyter_ai_router, jupyter_bokeh,
jupyter_server, jupyter_server_documents, jupyterlab, jupyterlab_chat,
jupyterlab_commands_toolkit, jupyterlab_eventlistener, jupyterlab_git,
jupyterlab_notebook_awareness, jupyterlab_pygments, jupyterlab_widgets,
nbdime, odh_jupyter_trash_cleanup.

```toml
# jupyterlab 4.5.7 pyproject.toml
[tool.hatch.build.hooks.jupyter-builder]
dependencies = ["hatch-jupyter-builder>=0.3.2"]
build-function = "buildapi.builder"
```

## setuptools_scm / setuptools-scm

**Trigger:** `use_scm_version=True` with `setup_requires=["setuptools_scm"]`
in setup.py, or `setuptools-scm` listed in `build-system.requires` in
pyproject.toml.

setuptools_scm extracts the package version from git tags at build time.
When used as a setuptools plugin via `use_scm_version`, it must be
available before `setup()` runs.

Packages: black, ConfigArgParse, duckdb, html5tagger, kafka-python-ng,
libcst, nglview, patchelf, pyarrow, PyBindGen, pytest-cpp, soxr, ujson.

```python
# ConfigArgParse 1.7.5 setup.py
setup(
    use_scm_version={"version_scheme": "no-guess-dev"},
    setup_requires=["setuptools_scm"],
    ...
)
```

```toml
# black 21.4b2 pyproject.toml
[build-system]
requires = ["setuptools>=41.0", "setuptools-scm", "wheel"]
build-backend = "setuptools.build_meta"
```

## setuptools_rust

**Trigger:** `from setuptools_rust import RustExtension` with
`rust_extensions=[...]` and `setup_requires=["setuptools_rust"]`
in setup.py.

setuptools_rust is a setuptools plugin that compiles Rust code to Python
extension modules using PyO3 bindings.

Packages: dulwich.

```python
# dulwich 1.2.10 setup.py
from setuptools_rust import Binding, RustExtension

setup(
    setup_requires=["setuptools_rust"],
    rust_extensions=[
        RustExtension("dulwich._objects", "crates/objects/Cargo.toml", binding=Binding.PyO3),
        RustExtension("dulwich._diff_tree", "crates/diff-tree/Cargo.toml", binding=Binding.PyO3),
        RustExtension("dulwich._pack", "crates/pack/Cargo.toml", binding=Binding.PyO3),
    ],
    ...
)
```

## cython

**Trigger:** `.pyx` source files configured via a custom build backend
with `[tool.local.cythonize]` in pyproject.toml, or
`setup_requires=["Cython"]` in setup.py.

Cython must be available to compile `.pyx` files to C extension modules
at build time.

Packages: frozenlist, propcache, ray, tesserocr.

```toml
# frozenlist 1.8.0 pyproject.toml
[build-system]
build-backend = "pep517_backend.hooks"
requires = ["expandvars", "setuptools >= 47"]

[tool.local.cythonize]
src = ["frozenlist/*.pyx"]
```

```python
# tesserocr 2.10.0 setup.py
setup(
    setup_requires=["Cython>=3.0.0,<3.2.0", "cysignals"],
    ...
)
```

## numpy

**Trigger:** `setup_requires` includes numpy, needed at build time to
access C API headers (`numpy/arrayobject.h`) when compiling extension
modules that use NumPy arrays.

Packages: numba, onnxruntime.

```python
# numba 0.60.0 setup.py
min_numpy_build_version = "2.0.0rc1"
build_requires = ['numpy >={},<{}'.format(min_numpy_build_version, max_numpy_run_version)]
setup(
    setup_requires=build_requires,
    ...
)
```

## cmake

**Trigger:** `build-backend = "scikit_build_core.build"` (or a wrapper)
with `[tool.scikit-build] cmake.version` in pyproject.toml.

scikit-build-core's `get_requires_for_build_wheel()` dynamically adds
cmake when a minimum version is configured.

Packages: duckdb.

```toml
# duckdb 1.5.3 pyproject.toml
[build-system]
build-backend = "duckdb_packaging.build_backend"
requires = ["scikit-build-core>=0.11.4", "pybind11[global]>=2.6.0", "setuptools_scm>=8.0"]

[tool.scikit-build]
cmake.version = ">=3.29.0"
ninja.version = ">=1.10"
```

## pbr

**Trigger:** `setup(setup_requires=['pbr'], pbr=True)` in setup.py.

pbr (Python Build Reasonableness) is a legacy setuptools wrapper that
handles version extraction from git tags and automatic metadata
generation. When `pbr=True` is set, pbr must be installed before
`setup()` executes.

Packages: lockfile, munch.

```python
# lockfile 0.12.2 setup.py
setup(
    setup_requires=['pbr>=1.8'],
    pbr=True,
)
```

## cffi

**Trigger:** `setup_requires=["cffi>=1.0"]` with
`cffi_modules=["...:ffibuilder"]` in setup.py.

CFFI generates C extension wrappers from Python API definitions at
build time.

Packages: soundfile.

```python
# soundfile 0.13.1 setup.py
setup(
    setup_requires=["cffi>=1.0"],
    cffi_modules=["soundfile_build.py:ffibuilder"],
    ...
)
```

## pytest-runner

**Trigger:** `setup_requires=['pytest-runner']` in setup.py.

Deprecated setuptools plugin that enables `python setup.py test`.
Listed in `setup_requires`, it gets pulled in during any `setup()`
execution.

Packages: lomond, rfc3986_validator.

```python
# lomond 0.3.3 setup.py
setup(
    setup_requires=['pytest-runner'],
    ...
)
```

## nose

**Trigger:** `setup_requires=['nose>=1.0']` in setup.py.

Legacy test runner pulled in via `setup_requires`.

Packages: annoy.

```python
# annoy 1.17.3 setup.py
setup(
    setup_requires=['nose>=1.0'],
    ...
)
```

## Other

**pydeck** -- `setup_requires=["Jinja2>=2.10.1", "jupyter>=1.0.0"]` in
setup.py. Custom build logic imports these to generate frontend code.

**setuptools-git-versioning** -- `setup_requires` reads from
`requirements.txt` which includes `packaging`. The build plugin uses
`packaging` for version validation.

**ray** -- Backend deps include `pip`, `cython`, and `wheel`. Ray's
build process uses pip internally and requires Cython for compiled
components.

**cysignals** (in tesserocr) -- `setup_requires=["cysignals"]` provides
signal handling support needed during Cython compilation.

## Summary

| Extra dependency | Source pattern | Mechanism | Packages |
|---|---|---|---|
| patchelf | `build-backend = "mesonpy"` | `get_requires_for_build_wheel()` | 11 |
| hatch-jupyter-builder | `[tool.hatch.build.hooks.jupyter-builder]` | `get_requires_for_build_wheel()` | 24 |
| setuptools_scm | `use_scm_version` / `build-system.requires` | `setup_requires` or static | 13 |
| setuptools_rust | `rust_extensions=[...]` | `setup_requires` | 1 |
| cython | `.pyx` files / `[tool.local.cythonize]` | `get_requires_for_build_wheel()` or `setup_requires` | 4 |
| numpy | C API headers for extensions | `setup_requires` | 2 |
| cmake | `[tool.scikit-build] cmake.version` | `get_requires_for_build_wheel()` | 1 |
| pbr | `setup(pbr=True)` | `setup_requires` | 2 |
| cffi | `cffi_modules=[...]` | `setup_requires` | 1 |
| pytest-runner | legacy test setup | `setup_requires` | 2 |
| nose | legacy test setup | `setup_requires` | 1 |
| other | various custom build logic | `setup_requires` | 3+ |
