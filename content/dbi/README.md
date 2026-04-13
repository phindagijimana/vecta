# data-birth-integrity — Data Birth Integrity for DICOM Series

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**Data Birth Integrity (DBI)** is a modular 0–1 scoring framework that quantifies
how well a raw DICOM series meets the structural requirements for automated
neuroimaging research workflows — before any image processing.

DBI scores five components per series:

| Component | What it checks |
|-----------|---------------|
| **M** — Metadata completeness | Required DICOM tags present and valid |
| **P** — Protocol conformity | Folder structure + prospective protocol tokens |
| **G** — Gradient integrity | Diffusion encoding evidence (DWI only) |
| **S** — Spatial consistency | Pixel spacing and slice geometry within bounds |
| **N** — Naming compliance | SeriesDescription conventions and per-class rules |

## Installation

Clone the repository and install from its root:

```bash
git clone git@github.com:phindagijimana/vecta.git vecta
cd vecta/content
```

Then install in editable mode for development (includes `pytest`):

```bash
pip install -e ".[dev]"
```

Or install without dev tools:

```bash
pip install .
```

To install from `requirements.txt` only (core runtime deps, no console scripts metadata):

```bash
pip install -r dbi/requirements.txt
```

Once published to PyPI (future):

```bash
pip install data-birth-integrity
```

## Quick start — CLI

### DBI Audit (Phase 2)

Score every series in a DICOM tree and produce CSVs, figures, and summary tables:

```bash
# XNAT-style layout (EP*/EP*/*_MR_*/scans/...)
dbi-audit --root /path/to/CIDUR_data --out ./results

# Generic DICOM tree (group by StudyInstanceUID + SeriesInstanceUID)
dbi-audit --layout uid-tree --root /path/to/any_dicom_folder --out ./results_uid
```

### DICOM-to-NIfTI Conversion (Phase 3)

Batch convert with dcm2niix and log pass/fail per series:

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

## Quick start — Python API

```python
from dbi import composite_dbi, load_yaml_config, score_M, score_S
from pathlib import Path
import pydicom

# Load bundled configuration
import dbi.scoring as sc
cfg = load_yaml_config(Path(sc.__file__).parent / "dbi_v1_config.yaml")
weights = {k: float(v) for k, v in cfg["weights"].items()}

# Score a single DICOM file
ds = pydicom.dcmread("example.dcm", stop_before_pixels=True)
m_score, m_pass, m_total = score_M(ds, "t1_anat", cfg["spatial"])
s_score = score_S(ds, "t1_anat", cfg["spatial"])

# Compute composite
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

## Outputs

### `dbi-audit`

| File | Content |
|------|---------|
| `per_series.csv` | One row per scan (first DICOM sampled); includes N_pass/N_total |
| `per_session.csv` | Aggregates per MR session |
| `table1_dbi_by_scanner.csv` | Scanner-stratified summary |
| `run_metadata.json` | Run timestamp, N, mean DBI, spec version |
| `read_failures.log` | Tab-separated log of DICOM read errors |
| `figure1_dbi_by_scanner.png` | Boxplot of session-mean DBI by scanner |
| `figure_supp_dbi_by_class.png` | Mean DBI by heuristic series class |

### `dbi-convert`

| File | Content |
|------|---------|
| `conversion_log.csv` | Per scan: exit code, n_nifti, pass/fail, scanner, class |
| `dcm2niix_environment.json` | dcm2niix version, CLI pattern |
| `table2_conversion_by_scanner.csv` | Marginal pass rate by scanner |
| `table2_conversion_by_scanner_class.csv` | Pass rate by scanner × class |
| `figure2_dcm2niix_pass_rate_heatmap.png` | Heatmap of pass rates |

## Configuration

All DBI rules, weights, thresholds, and naming conventions are specified in
`dbi_v1_config.yaml` (bundled with the package). Override by passing `--config`:

```bash
dbi-audit --config /path/to/my_config.yaml --root /data --out ./results
```

## Tests

From **`content/`** (directory that contains `pyproject.toml`):

```bash
pytest dbi/tests -v
```

## Contributing

See [`CONTRIBUTING.md`](../CONTRIBUTING.md) next to this package (`content/`).

## Outputs and Git

Default audit directories (`outputs/`, `outputs_phase4/`, `outputs_dcm2niix_v1freeze/`, large `nifti/` trees) are listed in `.gitignore`. After cloning, run `dbi-audit` and `dbi-convert` locally to regenerate tables and figures. Do not commit raw DICOM or identifiers.

## Specification

The full DBI v1 specification (formulas, pseudocode, aggregation rules, and
limitations) is in `DBI_v1_SPECIFICATION.md`, bundled with the package.

## Citation

When publishing results obtained with this tool, cite the DBI version and
config hash (e.g., SHA256 of `dbi_v1_config.yaml`) in your Methods section.

## License

MIT
