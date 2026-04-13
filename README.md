# data-birth-integrity (DBI)

Python package and CLIs for **Data Birth Integrity** — scoring DICOM series for automation-readiness before image processing.

## Quick start

```bash
git clone git@github.com:phindagijimana/vecta.git
cd vecta
chmod +x scripts/vecta
ln -sf scripts/vecta ./vecta    # adds ./vecta at repo root (skip if a ./vecta path already exists)
./vecta install
./vecta --help
dbi-audit --help
pytest dbi/tests -v
```

**Repo CLI** (after `ln -sf scripts/vecta ./vecta` or run `./scripts/vecta` directly):

| Command | Purpose |
|--------|---------|
| `./vecta install` | Create `.venv` and `pip install -e ".[dev]"` |
| `./vecta start -- --root /path/to/dicom --out ./results` | Run `dbi-audit` in the background; logs under `.vecta/logs/` |
| `./vecta stop` | Stop the last background audit |
| `./vecta logs` | `tail -f` the background log |

Use `VECTA_RUN=dbi-convert` for batch conversion instead of audit.

## Documentation

- **Package overview and CLI:** [`dbi/README.md`](dbi/README.md)
- **Formal spec:** [`dbi/DBI_v1_SPECIFICATION.md`](dbi/DBI_v1_SPECIFICATION.md)
- **Contributing:** [`CONTRIBUTING.md`](CONTRIBUTING.md)
- **License:** [`LICENSE`](LICENSE)

Audit outputs under `dbi/outputs*` are gitignored; run `dbi-audit` / `dbi-convert` locally after clone.

**Maintainers:** manuscript tooling (`writing/`, `build_*.py`, generated `*.docx`) is listed in `.gitignore` so it stays on your machine but is not pushed to GitHub.

## Citation

When using DBI in publications, cite the version in `dbi/dbi_v1_config.yaml` and the accompanying paper when available.
