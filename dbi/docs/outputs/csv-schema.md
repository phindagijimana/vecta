# CSV schema

All columns emitted by `dbi-audit` and `dbi-convert`.

## `per_series.csv`

One row per scan folder (xnat layout) or `(StudyUID, SeriesUID)` pair (uid-tree).

### Identification

| Column          | Type | Notes                                                                |
|-----------------|------|----------------------------------------------------------------------|
| `session_path`  | str  | Absolute path to the `*_MR_*` directory, or `uid://<StudyUID>`.       |
| `session_id`    | str  | `*_MR_*` basename, or StudyInstanceUID for uid-tree.                 |
| `scan_folder`   | str  | `scans/<name>` basename, or synthesised label for uid-tree.          |
| `scan_path`     | str  | Absolute scan path or `uid://<StudyUID>/<SeriesUID>`.                |
| `dicom_path`    | str  | Path to the first DICOM that was read.                               |

### Classification & context

| Column                       | Type | Notes                                                |
|------------------------------|------|------------------------------------------------------|
| `scanner_cluster`            | str  | `Manufacturer | Model | <B0>T`. Same on every row from a session. |
| `series_class`               | str  | Heuristic class (see [Classification](../concepts/classification.md)). |
| `standards_compliant_class`  | str  | Standards-classifier output (or `unclassifiable`).   |
| `naming_compliant`           | bool | `True` iff `series_class == standards_compliant_class != "other"`. |
| `recommended_name_pattern`   | str  | Suggested SeriesDescription template for the heuristic class. |
| `standards_gap`              | str  | Human-readable reason for non-compliance (or `Already compliant`). |
| `read_error`                 | str  | Empty on success; otherwise `read_error:<repr>` or `no_dicom`. |

### Component scores

| Column   | Type  | Notes                                                                  |
|----------|-------|------------------------------------------------------------------------|
| `M`      | float | Metadata completeness ∈ `[0, 1]`.                                       |
| `M_pass` | int   | Number of M checks that passed.                                         |
| `M_total`| int   | Number of M checks evaluated (class-dependent).                         |
| `P`      | float | Protocol naming ∈ `[0, 1]`. `P = 0.5·P_minimal + 0.5·P_ideal`.          |
| `P_minimal` | float | Folder pattern + descriptive text present.                          |
| `P_ideal`   | float | Combined text matches the `protocol_token.pattern` regex.            |
| `G`         | float / "" | Gradient integrity (DWI only). Empty string when N/A.            |
| `G_na`      | bool  | `True` when G is excluded from the composite.                       |
| `derivative_series` | bool | `True` if the series is flagged as a derivative DWI map.          |
| `S`      | float | Spatial consistency.                                                   |
| `N`      | float | Naming compliance.                                                     |
| `N_pass` | int   | Number of N checks passed.                                             |
| `N_total`| int   | Number of N checks evaluated.                                          |
| `DBI`    | float | Composite, renormalised over applicable weights.                       |

### Evidence flags

| Column                    | Type | Notes                                                       |
|---------------------------|------|-------------------------------------------------------------|
| `has_bvalue_evidence`     | bool | Any DWI b-value or diffusion tag detected.                  |
| `has_gradient_direction`  | bool | Gradient direction tags detected.                           |

## `per_session.csv`

One row per imaging visit.

| Column                            | Type  | Notes                                                       |
|-----------------------------------|-------|-------------------------------------------------------------|
| `session_id`                      | str   | `*_MR_*` basename or StudyInstanceUID.                       |
| `scanner_cluster`                 | str   | As above.                                                   |
| `n_series`                        | int   | Total scan folders in the session.                          |
| `n_scored`                        | int   | Series that survived DICOM read (excluded read errors).     |
| `DBI_session_mean`                | float | Mean DBI over scored series (incl. localizers).             |
| `DBI_session_mean_no_localizer`   | float | Mean DBI over non-localizer scored series.                  |
| `DBI_session_min`                 | float | Minimum DBI in the session.                                 |
| `DBI_session_median`              | float | Median DBI in the session.                                  |
| `mean_M` / `mean_P` / `mean_S` / `mean_N` | float | Per-component session means.                       |

## `table1_dbi_by_scanner.csv`

One row per `scanner_cluster`:

| Column          | Notes                                              |
|-----------------|----------------------------------------------------|
| `scanner_cluster` | The cluster string.                              |
| `n_sessions`    | Number of sessions in this cluster.                |
| `DBI_mean`      | Mean of `DBI_session_mean_no_localizer`.           |
| `DBI_std`       | Standard deviation.                                |
| `DBI_min`       | Minimum.                                           |
| `DBI_max`       | Maximum.                                           |

## `conversion_log.csv` (`dbi-convert`)

One row per scan folder attempted.

| Column            | Type  | Notes                                                       |
|-------------------|-------|-------------------------------------------------------------|
| `session_id`      | str   | `*_MR_*` basename.                                          |
| `scan_folder`     | str   | scan-folder basename.                                       |
| `series_class`    | str   | From `classify_series` on the first DICOM.                  |
| `status`          | str   | `run`, `dry_run`, `skip_no_dicom`, or `backfill_from_nifti`. |
| `exit_code`       | int   | dcm2niix exit code (or backfill-inferred).                  |
| `n_nifti`         | int   | Count of `.nii` / `.nii.gz` written.                        |
| `convert_pass`    | bool  | `(exit_code == 0) and (n_nifti >= 1)`.                      |
| `stdout_tail`     | str   | Last ~8 KB of dcm2niix stdout.                              |
| `stderr_tail`     | str   | Last ~8 KB of dcm2niix stderr.                              |

## `table2_conversion_by_scanner_class.csv`

Mean `convert_pass` for each `scanner_cluster × series_class` combination. Rows
with `status == skip_no_dicom` are excluded.
