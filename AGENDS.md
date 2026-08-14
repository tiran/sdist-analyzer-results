# RHOAI sdist-analyzer-results

Analyze Python wheel packaging for Red Hat OpenShift AI (RHOAI):
build systems, ELF shared library deps, manylinux compatibility.

Wheels are built from source with [fromager](https://github.com/python-wheel-build/fromager) on UBI9.

## Scripts

All scripts use `uv run` with PEP 723 inline metadata (no requirements.txt needed).

| Script | Purpose |
|:---|:---|
| `extract-fromager-elf.py` | ELF dependency analysis. Fetches `fromager-elf-*.txt` from RHOAI Pulp indexes via zipwire (HTTP/2), classifies deps (manylinux/bundleable/accelerator/unbundleable/undecided), writes `elf-analysis.md` with Mermaid charts. Use `--no-fetch` for local-only re-analysis. |
| `fetch_rhoai_wheel_metadata.py` | Extracts METADATA and fromager requirements from RHOAI wheels into `data/rhoai-*/`. |
| `fetch_sdist_metadata.py` | Downloads PKG-INFO, pyproject.toml, setup.py from PyPI sdists into `data/pypi/`. |
| `analyze_attestations.py` | Checks PyPI PEP 740 Sigstore attestations for RHOAI packages. |
| `analyze_git_hosting.py` | Finds projects without git hosting URLs in PKG-INFO metadata. |
| `compare_build_deps.py` | Diffs fromager build-system-requirements vs upstream pyproject.toml build-system.requires. |

## Data layout

```
data/
  rhoai-3.6-EA1/
    elf-analysis.md                      # combined report
    {cpu,cuda12.9,cuda13.0,rocm7.1,rocm7.14,spyre}-ubi9-test/
      elf-analysis.md                    # per-index report
      wheel-counts.json                  # purelib/platlib/manylinux counts
      <package>/<version>/               # fromager-elf-*.txt files
  rhoai-3.5-cpu-ubi9-test/               # older RHOAI 3.5 data
  pypi/<package>/<version>/              # upstream sdist metadata
```

## Practices

- Run scripts: `uv run <script>.py [args]` -- uv manages venvs automatically.
- Add new version: `uv run extract-fromager-elf.py 3.7 prod`
- AI-assisted: scripts developed with Claude (Anthropic). Review before relying on output.
