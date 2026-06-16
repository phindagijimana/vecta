# Outputs

Every `dbi-audit` and `dbi-convert` artefact, in one place.

- [**CSV schema**](csv-schema.md) — every column in `per_series.csv`,
  `per_session.csv`, `table1_dbi_by_scanner.csv`, `conversion_log.csv`, and
  `table2_conversion_by_scanner_class.csv`.
- [**Figures**](figures.md) — what `figure1_dbi_by_scanner.png`,
  `figure_supp_class_means.png`, and `figure2_dcm2niix_pass_rate_heatmap.png`
  show, and when they are skipped.
- [**QC spot-check**](qc-spotcheck.md) — how to use
  `qc_spotcheck_template.csv` to manually validate a small subset.

## Filename map

| Tool        | File                                          |
|-------------|-----------------------------------------------|
| `dbi-audit` | `per_series.csv`                              |
| `dbi-audit` | `per_session.csv`                             |
| `dbi-audit` | `table1_dbi_by_scanner.csv`                   |
| `dbi-audit` | `run_metadata.json`                           |
| `dbi-audit` | `compliance_report.txt` + `compliance_report.csv` |
| `dbi-audit` | `read_failures.log`                           |
| `dbi-audit` | `figure1_dbi_by_scanner.png`                  |
| `dbi-audit` | `figure_supp_class_means.png`                 |
| `dbi-convert` | `conversion_log.csv`                        |
| `dbi-convert` | `dcm2niix_environment.json`                 |
| `dbi-convert` | `table2_conversion_by_scanner_class.csv`    |
| `dbi-convert` | `figure2_dcm2niix_pass_rate_heatmap.png`    |
