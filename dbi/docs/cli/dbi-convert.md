# `dbi-convert`

Runs `dcm2niix` per scan folder and records whether each conversion succeeded.

## Synopsis

```bash
dbi-convert \
    [--root PATH] [--out PATH] [--nifti-root PATH] [--config PATH] \
    [--dcm2niix EXEC] [--dry-run] [--timeout SECONDS] [--limit N] \
    [--backfill-from-nifti]
```

Or:

```bash
python -m dbi.run_dcm2niix_batch ...
```

## Flags

| Flag                    | Default                                   | Meaning                                                                |
|-------------------------|-------------------------------------------|------------------------------------------------------------------------|
| `--root`                | `…/CIDUR_data` (set in source)            | Root of the DICOM tree (XNAT layout only for this command).            |
| `--out`                 | `dbi/outputs_dcm2niix/`                   | Directory for log + table + figure.                                    |
| `--nifti-root`          | `<out>/nifti`                             | Where dcm2niix writes NIfTI; per-session and per-scan sub-folders.     |
| `--config`              | `dbi/dbi_v1_config.yaml`                  | Used to classify series for stratifying Table 2.                       |
| `--dcm2niix`            | `dcm2niix`                                | Executable name or full path.                                          |
| `--dry-run`             | _false_                                   | List the work without invoking dcm2niix.                               |
| `--timeout`             | `7200`                                    | Per-series timeout in seconds; `0` = no limit.                         |
| `--limit`               | _all_                                     | Stop after N scan folders (for smoke tests).                           |
| `--backfill-from-nifti` | _false_                                   | Rebuild `conversion_log.csv` and Table 2 from an existing NIfTI tree. |

## Rubric

```
convert_pass = (exit_code == 0) AND (n_nifti >= 1)
```

Rows tagged `status == skip_no_dicom` are written but excluded from Table 2.

## What it writes

| File                                          | Description                                                          |
|-----------------------------------------------|----------------------------------------------------------------------|
| `conversion_log.csv`                          | Per-series row: status, exit code, n_nifti, stdout/stderr tails.     |
| `dcm2niix_environment.json`                   | dcm2niix version, CLI pattern, rubric, run timestamp, flags echoed.  |
| `table2_conversion_by_scanner_class.csv`      | Mean `convert_pass` per `scanner_cluster × series_class`.            |
| `figure2_dcm2niix_pass_rate_heatmap.png`      | Optional heatmap of Table 2.                                         |

## Backfill mode

If you already ran dcm2niix elsewhere and only kept the NIfTI tree:

```bash
dbi-convert --root /data/CIDUR_data \
            --out ./outputs_dcm2niix \
            --nifti-root /existing/nifti \
            --backfill-from-nifti
```

The tool walks `--nifti-root`, recovers session and scan-folder labels from the
directory layout, and emits a `conversion_log.csv` whose
`status = backfill_from_nifti` rows are flagged in
`dcm2niix_environment.json`. Cannot be combined with `--dry-run`.

## Exit codes

| Code | When                                                                        |
|:----:|-----------------------------------------------------------------------------|
| 0    | Normal completion.                                                          |
| 1    | dcm2niix missing on `$PATH` (and not `--dry-run` / `--backfill-from-nifti`). |
| 1    | `--backfill-from-nifti` combined with `--dry-run`.                          |
