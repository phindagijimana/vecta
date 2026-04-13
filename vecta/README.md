# data-birth-integrity (DBI)

Python package and CLIs for **Data Birth Integrity** — scoring DICOM series for automation-readiness before image processing.

## Quick start

```bash
git clone <repo-url> vecta
cd vecta
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
dbi-audit --help
pytest dbi/tests -v
```

## Documentation

- **Package overview and CLI:** [`dbi/README.md`](dbi/README.md)
- **Formal spec:** [`dbi/DBI_v1_SPECIFICATION.md`](dbi/DBI_v1_SPECIFICATION.md)
- **Contributing:** [`CONTRIBUTING.md`](CONTRIBUTING.md)
- **License:** [`LICENSE`](LICENSE)

Audit outputs under `dbi/outputs*` are gitignored; run `dbi-audit` / `dbi-convert` locally after clone.

**Maintainers:** manuscript tooling (`writing/`, root `build_*.py`, generated `*.docx`) is listed in `.gitignore` so it stays on your checkout but is not pushed to GitHub. Public users only need `dbi/`, `pyproject.toml`, and the repo metadata above.

## Citation

When using DBI in publications, cite the version in `dbi/dbi_v1_config.yaml` and the accompanying paper when available.
