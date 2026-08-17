# RHOAI sdist-analyzer-results

Analysis of Python wheel packaging for
[Red Hat OpenShift AI](https://www.redhat.com/en/technologies/cloud-computing/openshift/openshift-ai)
(RHOAI).  Covers build systems, ELF shared library dependencies,
manylinux compatibility, PyPI attestations, and git hosting.

RHOAI wheels are built from source using
[fromager](https://github.com/python-wheel-build/fromager) on UBI 9.
Fromager injects metadata files (`fromager-elf-requires.txt`,
`fromager-build-system-requirements.txt`, etc.) into each wheel's
dist-info directory.  The scripts in this repository fetch that
metadata and analyze it.

## Prerequisites

[uv](https://docs.astral.sh/uv/) is the only prerequisite.  All
scripts use PEP 723 inline metadata -- `uv run` installs dependencies
automatically into a cached per-script virtualenv.

## Workflow

### 1. Fetch RHOAI wheel metadata

```bash
uv run fetch-rhoai-metadata.py 3.6-EA1 test
```

Discovers all RHOAI Pulp indexes for the given version, scrapes the
content listings, and extracts dist-info files (METADATA, WHEEL,
fromager-\*.txt) from each wheel via
[zipwire](https://pypi.org/project/zipwire/) over HTTP/2 -- without
downloading full wheel archives.  METADATA descriptions are stripped
and long fields truncated to reduce storage.

Output per index directory:

| File | Description |
|:---|:---|
| `wheel-counts.json` | Purelib, platlib, and manylinux package counts |
| `<package>/<version>/METADATA` | Wheel metadata (description removed) |
| `<package>/<version>/WHEEL` | Wheel tags |
| `<package>/<version>/fromager-*.txt` | Fromager build/ELF metadata |

### 2. Fetch PyPI sdist metadata

```bash
uv run fetch-pypi-sdists.py 3.6-EA1
```

Scans the local RHOAI data to discover package names and versions,
then downloads source distributions from PyPI and extracts PKG-INFO,
pyproject.toml, and setup.py.  Packages without a sdist on PyPI are
recorded in `data/pypi/no_sdist.yaml`.

### 3. Analyze

```bash
# ELF shared library dependency analysis
uv run analyze-elf-deps.py 3.6-EA1

# PyPI digital attestations (PEP 740)
uv run analyze-attestations.py 3.6-EA1

# Git hosting URL coverage
uv run analyze-git-hosting.py 3.6-EA1

# Fromager vs upstream build-system.requires diff
uv run compare-build-deps.py 3.6-EA1

# Transitive system library deps (run on target platform)
python3 dump-transitive-deps.py
```

## Scripts

### Fetch (remote data)

| Script | Source | Description |
|:---|:---|:---|
| `fetch-rhoai-metadata.py` | RHOAI Pulp | Fetches METADATA, WHEEL, and fromager files from all RHOAI indexes for a version. Writes `wheel-counts.json`. |
| `fetch-pypi-sdists.py` | PyPI | Downloads sdists and extracts PKG-INFO, pyproject.toml, setup.py. Writes `no_sdist.yaml`. |

### Analyze (local data)

| Script | Description |
|:---|:---|
| `analyze-elf-deps.py` | Classifies ELF shared library deps as manylinux-only, bundleable, accelerator-specific, or unbundleable. Writes `elf-analysis.md` per index and combined, with Mermaid bar charts. |
| `analyze-attestations.py` | Checks the latest PyPI version of each package for Sigstore attestations (PEP 740). Extracts publisher, repository, workflow, git ref, and commit hash. Writes `data/pypi/attestations.yaml`. |
| `analyze-git-hosting.py` | Scans METADATA for Home-page and Project-URL fields, checks for known git hosting platforms (GitHub, GitLab, etc.). |
| `compare-build-deps.py` | Compares fromager `build-system-requirements.txt` against upstream `pyproject.toml` `build-system.requires`. Reports extra and missing deps. |
| `dump-transitive-deps.py` | Runs `ldd` on the local system to discover transitive shared library deps for vendor/bundleable libraries. Flags unbundleable transitive deps (OpenSSL, Kerberos, etc.). |

## Configuration

| File | Description |
|:---|:---|
| `policy.toml` | [Wheelmonger](https://github.com/tiran/wheelmonger) shared library policy. Classifies every external soname as `vendor` (bundle into wheel), `system` (consume from platform), or `skip` (provided by another wheel). |

## Analysis results

| File | Description |
|:---|:---|
| `data/rhoai-3.6-EA1/elf-analysis.md` | Combined ELF dependency analysis across all indexes |
| `data/rhoai-3.6-EA1/*/elf-analysis.md` | Per-index ELF dependency analysis |
| `data/rhoai-3.6-EA1/transitive-deps.yaml` | Transitive deps of vendor/bundleable libraries (from `ldd`) |
| `data/pypi/attestations.yaml` | PyPI attestation results |
| `data/pypi/no_sdist.yaml` | Packages/versions without sdists on PyPI |
| `cuda-rocm-without-torch.md` | Packages using CUDA/ROCm without PyTorch runtime |
| `downstream-build-system-analysis.md` | Build system patching analysis |
| `extra-build-backend-analysis.md` | Extra build-backend dependency analysis |
| `OPEN-QUESTIONS.md` | Resolved packaging decisions with rationale |

## Data layout

```
data/
  rhoai-3.6-EA1/
    elf-analysis.md
    transitive-deps.yaml
    {cpu,cuda12.9,cuda13.0,rocm7.1,rocm7.14,spyre}-ubi9-test/
      elf-analysis.md
      wheel-counts.json
      <package>/<version>/
        METADATA
        WHEEL
        fromager-build-system-requirements.txt
        fromager-build-backend-requirements.txt
        fromager-build-sdist-requirements.txt
        fromager-elf-requires.txt
        fromager-elf-provides.txt
  pypi/
    attestations.yaml
    no_sdist.yaml
    <package>/<version>/
      PKG-INFO
      pyproject.toml
      setup.py
```

## Notes

Scripts in this repository were developed with the assistance of
Claude (Anthropic).  Review before relying on output.
