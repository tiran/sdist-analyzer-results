# RHOAI sdist-analyzer-results

Analyze Python wheel packaging for Red Hat OpenShift AI (RHOAI):
build systems, ELF shared library deps, manylinux compatibility.

Wheels are built from source with [fromager](https://github.com/python-wheel-build/fromager) on UBI9.

## Scripts

All scripts use `uv run` with PEP 723 inline metadata (no requirements.txt needed).

### Fetch (remote data)

| Script | Purpose |
|:---|:---|
| `fetch-rhoai-metadata.py` | Fetches METADATA, WHEEL, and fromager files from RHOAI Pulp indexes via zipwire (HTTP/2). Writes `wheel-counts.json` per index. |
| `fetch-pypi-sdists.py` | Downloads sdists from PyPI and extracts PKG-INFO, pyproject.toml, setup.py into `data/pypi/`. Writes `no_sdist.yaml`. |

### Analyze (local data)

| Script | Purpose |
|:---|:---|
| `analyze-elf-deps.py` | ELF dependency analysis. Classifies deps (manylinux/bundleable/accelerator/unbundleable), writes `elf-analysis.md` with Mermaid charts. |
| `analyze-attestations.py` | Checks PyPI PEP 740 Sigstore attestations. Writes `data/pypi/attestations.yaml`. |
| `analyze-git-hosting.py` | Finds projects without git hosting URLs in METADATA. |
| `compare-build-deps.py` | Diffs fromager build-system-requirements vs upstream pyproject.toml build-system.requires. |
| `dump-transitive-deps.py` | Runs ldd on local system to dump transitive deps for vendor/bundleable libraries. |

## Data layout

```
data/
  rhoai-3.6-EA1/
    elf-analysis.md                      # combined report
    transitive-deps.yaml                 # ldd transitive dep analysis
    {cpu,cuda12.9,cuda13.0,rocm7.1,rocm7.14,spyre}-ubi9-test/
      elf-analysis.md                    # per-index report
      wheel-counts.json                  # purelib/platlib/manylinux counts
      <package>/<version>/               # METADATA, WHEEL, fromager-*.txt
  pypi/
    <package>/<version>/                 # PKG-INFO, pyproject.toml, setup.py
    no_sdist.yaml                        # packages without sdists on PyPI
```

## Practices

- Fetch RHOAI data: `uv run fetch-rhoai-metadata.py 3.6-EA1 test`
- Fetch PyPI sdists: `uv run fetch-pypi-sdists.py 3.6-EA1`
- Analyze ELF deps: `uv run analyze-elf-deps.py 3.6-EA1`
- AI-assisted: scripts developed with Claude (Anthropic). Review before relying on output.
