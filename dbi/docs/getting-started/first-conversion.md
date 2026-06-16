# 3. Your first conversion

`dbi-convert` runs `dcm2niix` per scan folder and records whether each conversion
succeeded. Join the resulting log back to the audit CSV and you get the headline
finding of Phase 3: **does the structural score (DBI) actually predict whether the
data converts cleanly to BIDS?**

## Prerequisites

- `dcm2niix` on `$PATH` (`which dcm2niix` should return a path).
- A successful `dbi-audit` run, so you have `outputs/per_series.csv`.

## Run it

```bash
dbi-convert \
    --root /path/to/CIDUR_data \
    --out ./outputs_dcm2niix \
    --nifti-root /path/to/nifti_output
```

What happens:

1. For each `scans/<name>` folder under `EP*/EP*/*_MR_*`, run
   `dcm2niix -o <nifti-root>/<session>/<scan_folder> <DICOM/files dir>`.
2. Record the exit code and the number of `.nii` / `.nii.gz` written.
3. Apply the rubric **`convert_pass = (exit_code == 0) AND (≥1 NIfTI emitted)`**.

## What you get

```
outputs_dcm2niix/
├── conversion_log.csv                          # session, scan_folder, series_class, exit_code, convert_pass, stdout/stderr tails
├── dcm2niix_environment.json                   # dcm2niix version, CLI pattern, rubric
├── table2_conversion_by_scanner_class.csv      # pass rate by scanner cluster × series class
└── figure2_dcm2niix_pass_rate_heatmap.png      # optional heatmap
```

A peek at `conversion_log.csv`:

| session_id  | scan_folder              | series_class | exit_code | n_nifti | convert_pass |
|-------------|--------------------------|--------------|-----------|---------|--------------|
| EP001_MR_1  | 2-AX_3D_T1_MPRAGE        | t1_anat      | 0         | 1       | True         |
| EP001_MR_1  | 3-AX_DTI_AP_64_DIRECTIONS| dwi          | 0         | 4       | True         |
| EP004_MR_2  | 7-AX_DERIVED_ADC         | dwi          | 0         | 1       | False        |

## Backfilling from an existing NIfTI tree

If you already ran dcm2niix elsewhere and only kept the NIfTI output, you can rebuild
`conversion_log.csv` and Table 2 without re-running:

```bash
dbi-convert \
    --root /path/to/CIDUR_data \
    --out ./outputs_dcm2niix \
    --nifti-root /path/to/existing_nifti \
    --backfill-from-nifti
```

Full reference: [CLI → `dbi-convert`](../cli/dbi-convert.md).
