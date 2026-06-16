# 1. Install

The repository is the `vecta` GitHub project; the Python package is `dbi`.

## From source (recommended)

```bash
git clone https://github.com/phindagijimana/vecta.git
cd vecta

# create a venv
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate

# install package + dev tools
pip install -e ".[dev]"
```

This exposes two console scripts:

| Command       | What it does                                                        |
|---------------|---------------------------------------------------------------------|
| `dbi-audit`   | Walks an MR DICOM tree, scores every series, writes CSVs / figures. |
| `dbi-convert` | Runs `dcm2niix` per scan folder and logs success / failure.         |

## Just the package

If you only want the scoring functions (no CLIs / dcm2niix):

```bash
pip install pydicom PyYAML pandas matplotlib
```

Then import:

```python
from dbi import (
    classify_series,
    composite_dbi,
    load_yaml_config,
    score_M, score_P, score_G, score_S, score_N,
    scanner_cluster_from_ds,
    series_description,
)
```

## External tools

| Tool      | Required by      | Install                                             |
|-----------|------------------|-----------------------------------------------------|
| dcm2niix  | `dbi-convert`    | `conda install -c conda-forge dcm2niix` (or build)  |
| Pages CI  | Hosting the site | Provided by the included `.github/workflows/docs.yml` |

## Verify the install

```bash
# unit tests
make test

# build the docs locally
make serve            # opens http://127.0.0.1:8000
```

The next page runs your first audit.
