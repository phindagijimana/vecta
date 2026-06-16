# Getting started

A 10-minute path from `git clone` to a CSV of DBI scores for a small MR cohort.

You'll need:

- Python ≥ 3.10
- `pydicom`, `pandas`, `PyYAML`, `matplotlib` (installed for you by `make install`)
- A folder of DICOMs — either CIDUR-style XNAT (`EP*/EP*/*_MR_*/scans/…`) or any tree
  with valid `StudyInstanceUID` / `SeriesInstanceUID` tags

The three steps:

1. [**Install**](install.md) — clone, create a venv, install the package.
2. [**Your first audit**](first-audit.md) — run `dbi-audit` (or `python -m dbi.run_audit`)
   and read the output CSVs.
3. [**Your first conversion**](first-conversion.md) — optionally run `dbi-convert` to
   exercise dcm2niix on the same cohort and join its results back to DBI.

When you're done, you'll have:

- `per_series.csv` — one row per scan folder with all five sub-scores and the
  composite DBI.
- `per_session.csv` — one row per imaging visit with mean / min / median DBI.
- Optional `figure1_dbi_by_scanner.png` and `figure_supp_class_means.png`.
- (If you ran `dbi-convert`) `conversion_log.csv` and a NIfTI tree.

If anything is unclear, the [Concepts](../concepts/index.md) section explains
*what* you are measuring and *why*.
