# Data Birth Integrity (DBI)

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**DBI** is a 0–1 score for raw DICOM MRI series: it checks metadata, protocol structure, diffusion evidence (when relevant), spatial consistency, and naming—**before** heavy processing—so you can see whether data is ready for automated workflows.

- **Python:** 3.9+  
- **License:** [MIT](LICENSE)  
- **Rules / version:** [`dbi/dbi_v1_config.yaml`](dbi/dbi_v1_config.yaml)

## Install

```bash
git clone https://github.com/phindagijimana/vecta.git
cd vecta
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

This installs the **`dbi-audit`** and **`dbi-convert`** commands.

## Run (minimal)

```bash
dbi-audit --root /path/to/dicom --out ./results
dbi-convert --root /path/to/dicom --out ./run_logs --nifti-root /path/to/nifti
```

Use `--help` on either command for options (layouts, config file, etc.).

## Documentation

| | |
|---|---|
| **Installation variants, repo CLI, outputs, API, configuration** | [**USER_GUIDE.md**](USER_GUIDE.md) |
| **Formal specification** | [`dbi/DBI_v1_SPECIFICATION.md`](dbi/DBI_v1_SPECIFICATION.md) |
| **Contributing** | [`CONTRIBUTING.md`](CONTRIBUTING.md) |

## Citation

In publications, cite the **`version`** field in `dbi/dbi_v1_config.yaml` (and a hash of that file if you need exact reproducibility).
