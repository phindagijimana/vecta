# DBI user guide

This guide covers setup options, the optional **`./vecta`** helper, command-line usage, outputs, the Python API, configuration, and testing. For a short overview, see [README.md](README.md).

## What DBI measures

DBI scores five components per series:

| Component | What it checks |
|-----------|----------------|
| **M** — Metadata completeness | Required DICOM tags present and valid |
| **P** — Protocol conformity | Folder structure + prospective protocol tokens |
| **G** — Gradient integrity | Diffusion encoding evidence (DWI only) |
| **S** — Spatial consistency | Pixel spacing and slice geometry within bounds |
| **N** — Naming compliance | SeriesDescription conventions and per-class rules |

## Installation options

### Editable install (development)

From the repository root (directory that contains `pyproject.toml`):

```bash
pip install -e ".[dev]"
```

`[dev]` adds `pytest` and `seaborn` for tests and some figures.

### Install without dev dependencies

```bash
pip install .
```

### Requirements file only

Core runtime dependencies only (no setuptools entry-point metadata for console scripts):

```bash
pip install -r dbi/requirements.txt
```

### PyPI (when published)

```bash
pip install data-birth-integrity
```

## Optional repo CLI: `scripts/vecta`

For a small wrapper around venv + background jobs:

```bash
chmod +x scripts/vecta
ln -sf scripts/vecta ./vecta    # skip if a file or directory ./vecta already exists
```

| Command | Purpose |
|--------|---------|
| `./vecta install` | Create `.venv` and `pip install -e ".[dev]"` |
| `./vecta start -- --root /path/to/dicom --out ./results` | Run `dbi-audit` in the background; logs under `.vecta/logs/` |
| `./vecta stop` | Stop the last background audit |
| `./vecta logs` | `tail -f` the background log |

Use `VECTA_RUN=dbi-convert` to run **`dbi-convert`** instead of **`dbi-audit`**. See `./vecta --help` for environment variables (`VECTA_VENV`, `VECTA_LOG_FILE`, …).

If you do not use the symlink, run **`./scripts/vecta`** with the same subcommands.

## `dbi-audit` (Phase 2)

Score every series in a DICOM tree and write CSVs, figures, and summary tables:

```bash
# XNAT-style layout (EP*/EP*/*_MR_*/scans/...)
dbi-audit --root /path/to/CIDUR_data --out ./results

# Generic DICOM tree (group by StudyInstanceUID + SeriesInstanceUID)
dbi-audit --layout uid-tree --root /path/to/any_dicom_folder --out ./results_uid
```

## `dbi-convert` (Phase 3)

Batch conversion with dcm2niix and per-series pass/fail logging:

```bash
dbi-convert --root /path/to/CIDUR_data --out ./results_nifti \
  --nifti-root /path/to/large_disk/nifti_output
```

Rebuild conversion tables from existing NIfTI without re-running dcm2niix:

```bash
dbi-convert --backfill-from-nifti \
  --root /path/to/CIDUR_data \
  --out ./results_nifti \
  --nifti-root ./results_nifti/nifti
```

## Python API (minimal example)

```python
from dbi import composite_dbi, load_yaml_config, score_M, score_S
from pathlib import Path
import pydicom

import dbi.scoring as sc

cfg = load_yaml_config(Path(sc.__file__).parent / "dbi_v1_config.yaml")
weights = {k: float(v) for k, v in cfg["weights"].items()}

ds = pydicom.dcmread("example.dcm", stop_before_pixels=True)
m_score, m_pass, m_total = score_M(ds, "t1_anat", cfg["spatial"])
s_score = score_S(ds, "t1_anat", cfg["spatial"])

scores = {
    "metadata_completeness": m_score,
    "protocol_naming": 0.5,
    "gradient_integrity": None,   # NA for non-DWI
    "spatial_consistency": s_score,
    "naming_compliance": 0.7,
}
dbi = composite_dbi(scores, weights)
print(f"DBI = {dbi:.4f}")
```

## Outputs from `dbi-audit`

| File | Content |
|------|---------|
| `per_series.csv` | One row per scan (first DICOM sampled); includes N_pass/N_total |
| `per_session.csv` | Aggregates per MR session |
| `table1_dbi_by_scanner.csv` | Scanner-stratified summary |
| `run_metadata.json` | Run timestamp, N, mean DBI, spec version |
| `read_failures.log` | Tab-separated log of DICOM read errors |
| `figure1_dbi_by_scanner.png` | Boxplot of session-mean DBI by scanner |
| `figure_supp_dbi_by_class.png` | Mean DBI by heuristic series class |

## Outputs from `dbi-convert`

| File | Content |
|------|---------|
| `conversion_log.csv` | Per scan: exit code, n_nifti, pass/fail, scanner, class |
| `dcm2niix_environment.json` | dcm2niix version, CLI pattern |
| `table2_conversion_by_scanner.csv` | Marginal pass rate by scanner |
| `table2_conversion_by_scanner_class.csv` | Pass rate by scanner × class |
| `figure2_dcm2niix_pass_rate_heatmap.png` | Heatmap of pass rates |

## Configuration

Rules, weights, thresholds, and naming conventions live in **`dbi_v1_config.yaml`** (bundled next to the Python package). Override with:

```bash
dbi-audit --config /path/to/my_config.yaml --root /data --out ./results
```

The human-readable specification is [**dbi/DBI_v1_SPECIFICATION.md**](dbi/DBI_v1_SPECIFICATION.md).

## Tests

From the repository root:

```bash
pytest dbi/tests -v
```

## Outputs and Git

Default audit directories under `dbi/` (`outputs/`, `outputs_phase4/`, `outputs_dcm2niix_v1freeze/`, large `nifti/` trees) are listed in `.gitignore`. After cloning, run **`dbi-audit`** and **`dbi-convert`** locally to regenerate tables and figures. Do not commit raw DICOM or identifiers.

## Maintainers (local-only tooling)

Manuscript or internal scripts (`writing/`, `build_*.py`, generated `*.docx`) are **gitignored** in this repository when present on disk; they are not part of the public tree.

## Contributing

See [**CONTRIBUTING.md**](CONTRIBUTING.md).

## Citation (detail)

When publishing, cite the DBI **version** and, if useful, a **hash** of `dbi_v1_config.yaml` in your Methods section.

## License

MIT — see [**LICENSE**](LICENSE).
