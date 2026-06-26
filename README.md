# Data Birth Integrity (DBI)

[![Docs](https://img.shields.io/badge/docs-phindagijimana.github.io%2Fvecta-009688?logo=readthedocs&logoColor=white)](https://phindagijimana.github.io/vecta/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

### Read the docs → **[https://phindagijimana.github.io/vecta/](https://phindagijimana.github.io/vecta/)**

**DBI** is a 0–1 score for raw DICOM MRI series: it checks metadata, protocol structure, diffusion evidence (when relevant), spatial consistency, and naming—**before** heavy processing—so you can see whether data is ready for automated workflows.

- **Python:** 3.9+  
- **License:** [MIT](LICENSE)  
- **Rules / version:** [`dbi/dbi_v1_config.yaml`](dbi/dbi_v1_config.yaml)

## Install

```bash
pip install git+https://github.com/phindagijimana/vecta.git
```

This installs the **`dbi-audit`** and **`dbi-convert`** commands and the `dbi` Python package.

For development (editable install with tests):

```bash
git clone https://github.com/phindagijimana/vecta.git
cd vecta
pip install -e ".[dev]"
pytest dbi/tests
```

## Run (minimal)

```bash
dbi-audit --root /path/to/dicom --out ./results
dbi-convert --root /path/to/dicom --out ./run_logs --nifti-root /path/to/nifti
```

Use `--help` on either command for options (layouts, config file, etc.).

## Documentation

The full documentation hub lives at **[phindagijimana.github.io/vecta](https://phindagijimana.github.io/vecta/)** — getting-started guide, concepts (M / P / G / S / N), CLI reference, configuration, outputs, and the v1 specification.

| | |
|---|---|
| **Docs hub (recommended)** | [phindagijimana.github.io/vecta](https://phindagijimana.github.io/vecta/) |
| **Installation variants, repo CLI, outputs, API, configuration** | [**USER_GUIDE.md**](USER_GUIDE.md) |
| **Formal specification** | [`dbi/DBI_v1_SPECIFICATION.md`](dbi/DBI_v1_SPECIFICATION.md) |
| **Contributing** | [`CONTRIBUTING.md`](CONTRIBUTING.md) |

## Citation

In publications, cite the **`version`** field in `dbi/dbi_v1_config.yaml` (and a hash of that file if you need exact reproducibility).
