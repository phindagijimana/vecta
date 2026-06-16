# 2. Your first audit

The audit walks a DICOM tree, scores every MR series, and writes two CSVs plus an
optional figure pair.

## XNAT-style cohort (default layout)

If your data looks like this (CIDUR-style export):

```
CIDUR_data/
  EP001/
    EP001/
      EP001_MR_1/
        scans/
          1-Localizer/resources/DICOM/files/*.dcm
          2-AX_3D_T1_MPRAGE/resources/DICOM/files/*.dcm
          3-AX_DTI_AP_64_DIRECTIONS/resources/DICOM/files/*.dcm
          ...
```

Run:

```bash
dbi-audit --root /path/to/CIDUR_data --out ./outputs
# equivalent module form:
python -m dbi.run_audit --root /path/to/CIDUR_data --out ./outputs
```

## Any tree (uid-tree layout)

For data that isn't laid out in XNAT folders — but still has valid
`StudyInstanceUID` / `SeriesInstanceUID` tags — group by UIDs instead:

```bash
dbi-audit --layout uid-tree --root /path/to/dicom_root --out ./outputs_uid
```

## What you get

```
outputs/
├── per_series.csv                  # one row per scan folder / UID-tree series
├── per_session.csv                 # one row per imaging visit (session aggregate)
├── table1_dbi_by_scanner.csv       # session-mean DBI by scanner cluster
├── run_metadata.json               # run timestamp, spec version, row counts
├── compliance_report.{txt,csv}     # readable + machine-readable summary
├── read_failures.log               # unreadable DICOMs / scans without DICOMs
├── figure1_dbi_by_scanner.png      # optional
└── figure_supp_class_means.png     # optional
```

A peek at `per_series.csv`:

| session_id     | scan_folder              | series_class | M    | P    | G    | S | N    | DBI  |
|----------------|--------------------------|--------------|------|------|------|---|------|------|
| EP001_MR_1     | 1-Localizer              | localizer    | 0.86 | 1.00 |      | 1 | 0.92 | 0.94 |
| EP001_MR_1     | 2-AX_3D_T1_MPRAGE        | t1_anat      | 1.00 | 1.00 |      | 1 | 1.00 | 1.00 |
| EP001_MR_1     | 3-AX_DTI_AP_64_DIRECTIONS| dwi          | 1.00 | 1.00 | 0.90 | 1 | 1.00 | 0.97 |

Each column is explained in [Outputs → CSV schema](../outputs/csv-schema.md), and the
five sub-scores in [Concepts → Components](../concepts/components.md).

## Useful flags

- `--config /path/to/dbi_v1_config.yaml` — override the bundled config.
- `--layout {xnat,uid-tree}` — pick the input layout.

Full reference: [CLI → `dbi-audit`](../cli/dbi-audit.md).
