# data-birth-integrity — Data Birth Integrity for DICOM series

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**DBI** scores raw DICOM MRI series (0–1) on metadata, protocol, diffusion evidence (DWI), spatial consistency, and naming—before heavy processing.

## Quick install

```bash
pip install data-birth-integrity    # when published to PyPI
# or from a clone of https://github.com/phindagijimana/vecta :
pip install .
```

## Quick commands

```bash
dbi-audit --root /path/to/dicom --out ./results
dbi-convert --root /path/to/dicom --out ./logs --nifti-root /path/to/nifti
```

## Documentation

| | |
|---|---|
| **Full user guide** (install options, `./vecta` helper, outputs, API, config) | [**USER_GUIDE.md**](../USER_GUIDE.md) in the repository root |
| **Repository overview** | [**README.md**](../README.md) |
| **DBI v1 specification** | [**DBI_v1_SPECIFICATION.md**](DBI_v1_SPECIFICATION.md) |

## License

MIT
