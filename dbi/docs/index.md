# Vecta — Data Birth Integrity

> A reproducible, auditable **0–1 score** for the structural quality of a DICOM MR series — measured *before* any image processing.

[![Site](https://img.shields.io/badge/site-vecta-009688?logo=readthedocs&logoColor=white)](https://phindagijimana.github.io/vecta/)
[![GitHub](https://img.shields.io/badge/github-phindagijimana%2Fvecta-181717?logo=github)](https://github.com/phindagijimana/vecta)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/phindagijimana/vecta/blob/main/LICENSE)

---

## What is DBI?

**Data Birth Integrity (DBI)** is a scalar summary of how well a *series* — one XNAT scan
folder, or one `(StudyInstanceUID, SeriesInstanceUID)` — satisfies the structural
requirements that downstream automation needs to succeed:

- ✅ Required DICOM metadata is present and parseable.
- ✅ Folder and protocol naming match a stable, automatable convention.
- ✅ Diffusion series carry b-value and gradient-direction evidence.
- ✅ Pixel spacing and slice thickness are within physically plausible bounds.
- ✅ Strings are clean enough for BIDS sidecars, dcm2niix, and ML loaders.

DBI is **not** a clinical / diagnostic quality measure. It does not capture SNR,
motion, or radiologic acceptability. It answers a different question:

> *Will my pipeline survive this series at the file-system and metadata layer?*

## How it works in one paragraph

For each series, Vecta reads the first DICOM and computes five sub-scores —
**M**etadata completeness, **P**rotocol naming, **G**radient integrity, **S**patial
consistency, **N**aming compliance. Each is in `[0, 1]` or marked **N/A** when the
component does not apply (e.g. `G` on a T1w). The composite DBI is the weighted mean
over the **applicable** components, with the N/A weights dropped from the denominator.
Weights, regex rules, and spatial bounds live in [`dbi_v1_config.yaml`](configuration/yaml-reference.md),
so the score is reproducible from the config version alone.

## Where to go next

<div class="grid cards" markdown>

- :material-rocket-launch: **[Getting started](getting-started/index.md)**

    Install the package, run your first audit on a CIDUR-style export, and inspect
    the CSV / figures it produces.

- :material-school: **[Concepts](concepts/index.md)**

    The DBI formula, the five components, series classification, and the
    scanner-cluster covariate.

- :material-console-line: **[CLI reference](cli/index.md)**

    `dbi-audit` and `dbi-convert` — every flag, every layout (`xnat`, `uid-tree`).

- :material-cog: **[Configuration](configuration/index.md)**

    The YAML config: weights, classification rules, naming conventions, spatial
    bounds — and how to override them per-site.

- :material-file-document-multiple: **[Outputs](outputs/index.md)**

    Series-level CSV, session aggregates, optional figures, and the QC
    spot-check template.

- :material-book-open-variant: **[Specification](spec.md)**

    The frozen v1 spec — `DBI_v1_SPECIFICATION.md` rendered alongside the docs.

</div>

## Quick reference — what `dbi-audit` writes

```
outputs/
├── per_series.csv                  # one row per scan folder / UID-tree series
├── per_session.csv                 # one row per imaging visit
├── table1_dbi_by_scanner.csv       # session-mean DBI stratified by scanner cluster
├── run_metadata.json               # run timestamp, spec version, row counts
├── compliance_report.{txt,csv}     # human + machine-readable summary
├── read_failures.log               # unreadable DICOMs / no-DICOM scan folders
├── figure1_dbi_by_scanner.png      # optional (matplotlib)
└── figure_supp_class_means.png     # optional (matplotlib)
```

## Status

- **Spec:** v1.0.5 (frozen)
- **Reference cohort:** CIDUR-style XNAT exports
  (`EP*/EP*/*_MR_*/scans/<series>/resources/DICOM/files/*.dcm`)
- **Layouts supported:** `xnat` (default) and `uid-tree` (any folder grouped by
  `(StudyInstanceUID, SeriesInstanceUID)`)
- **License:** MIT
