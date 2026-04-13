# Contributing

## Repository layout

The installable Python package **`data-birth-integrity`** (import name **`dbi`**) lives at the **repository root**: **`pyproject.toml`** and **`dbi/`**. End-user documentation is **[`USER_GUIDE.md`](USER_GUIDE.md)**; the landing page is **[`README.md`](README.md)**.

If you maintain the NeuroImage manuscript locally, keep `writing/` and `build_*.py` on disk; they are **gitignored** so clones and GitHub show only the runnable DBI package. Update those scripts if you move `dbi/` or output paths.

| Path | Purpose |
|------|---------|
| `dbi/scoring.py` | Core DBI component scores and classification |
| `dbi/run_audit.py` | CLI `dbi-audit` — walk DICOM trees, emit CSVs |
| `dbi/run_dcm2niix_batch.py` | CLI `dbi-convert` — batch dcm2niix with logging |
| `dbi/dbi_v1_config.yaml` | Rules, weights, naming conventions |
| `dbi/DBI_v1_SPECIFICATION.md` | Human-readable DBI v1 spec |
| `dbi/tests/` | Pytest suite |

Generated audit outputs are gitignored under `dbi/outputs*`.

## Development setup

```bash
# repository root (directory containing pyproject.toml)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest dbi/tests -v
```

## Style and scope

- Keep changes focused: one logical fix or feature per PR.
- Match existing naming and typing style in `scoring.py` / `run_audit.py`.
- If you change scoring behavior, update `DBI_v1_SPECIFICATION.md` and bump `dbi_v1_config.yaml` `version` with a short changelog note.

## Pull requests

1. Run `pytest dbi/tests` from the repository root (all green).
2. Describe what changed and why (Methods-level clarity helps reproducibility).
3. Do not commit raw DICOM, patient identifiers, or large NIfTI trees.

If `outputs/` or similar paths were committed before `.gitignore` was updated, stop tracking them (files stay on disk):

```bash
git rm -r --cached dbi/outputs dbi/outputs_phase4 dbi/outputs_dcm2niix_v1freeze 2>/dev/null || true
```

Before publishing to PyPI, set real URLs in **`pyproject.toml`** under `[project.urls]` if they change.

## Reporting issues

Include: Python version, `dbi_v1_config.yaml` version string, layout (`xnat` vs `uid-tree`), and a **de-identified** example of `SeriesDescription` / folder naming if the issue is classification- or naming-related.
