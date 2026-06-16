# `dbi-audit`

Walks an MR DICOM tree, scores each series with the DBI v1 formula, and writes
CSVs, an optional figure pair, and a compliance report.

## Synopsis

```bash
dbi-audit [--root PATH] [--out PATH] [--config PATH] [--layout {xnat,uid-tree}]
```

Or equivalently:

```bash
python -m dbi.run_audit ...
```

## Flags

| Flag        | Default                                        | Meaning                                                                 |
|-------------|------------------------------------------------|-------------------------------------------------------------------------|
| `--root`    | `…/CIDUR_data` (set in source)                 | Root of the DICOM tree.                                                 |
| `--out`     | `dbi/outputs/`                                 | Directory for CSVs, JSON, figures, failure log.                         |
| `--config`  | `dbi/dbi_v1_config.yaml`                       | Override the default config (weights, regex rules, spatial bounds).     |
| `--layout`  | `xnat`                                         | `xnat` for CIDUR-style `EP*/EP*/*_MR_*/scans/…`; `uid-tree` for any tree grouped by `(StudyInstanceUID, SeriesInstanceUID)`. |

## What it writes

| File                            | Description                                                                |
|---------------------------------|----------------------------------------------------------------------------|
| `per_series.csv`                | One row per scan folder / UID-tree series — all five sub-scores + DBI.      |
| `per_session.csv`               | One row per imaging visit — session-mean DBI + per-component means.         |
| `table1_dbi_by_scanner.csv`     | Session-mean DBI stratified by `scanner_cluster`.                          |
| `run_metadata.json`             | Run timestamp, config version, layout, row counts, cohort mean DBI.        |
| `compliance_report.txt`         | Human-readable summary (counts, top failure reasons).                      |
| `compliance_report.csv`         | Machine-readable version of the same summary.                              |
| `read_failures.log`             | Tab-separated log of unreadable DICOMs / no-DICOM scan folders.            |
| `figure1_dbi_by_scanner.png`    | Box plot of `DBI_session_mean_no_localizer` per scanner cluster (optional). |
| `figure_supp_class_means.png`   | Bar chart of mean DBI per series class (optional).                         |

Schema details live in [Outputs → CSV schema](../outputs/csv-schema.md).

## Layouts in detail

=== "xnat (default)"

    Expects:

    ```
    <root>/EP*/EP*/*_MR_*/scans/<name>/resources/DICOM/files/*.dcm
    ```

    The session is one `*_MR_*` directory; a series is one `scans/<name>` folder.
    The first readable `*.dcm` is used to read all tags.

=== "uid-tree"

    Recursively walks `<root>` for `*.dcm`, keeps only `Modality == MR`, groups
    by `(StudyInstanceUID, SeriesInstanceUID)`, and synthesises a scan-folder
    label from `SeriesNumber + sanitized SeriesDescription`. Use this when your
    cohort isn't laid out as an XNAT export.

## Exit codes

`0` on success. The audit does not raise on individual unreadable DICOMs — they
are logged in `read_failures.log` and the corresponding row carries
`read_error != ""`.
