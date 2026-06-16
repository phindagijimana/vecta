# Specification

The frozen v1 specification lives in
[`DBI_v1_SPECIFICATION.md`](https://github.com/phindagijimana/vecta/blob/main/dbi/DBI_v1_SPECIFICATION.md)
at the root of the package. The docs you are reading are intended to *interpret*
the spec for end users; the spec itself is the authoritative reference.

## Quick index

| § | Topic                                                                       |
|---|-----------------------------------------------------------------------------|
| 1 | Purpose, design principles, units of analysis, relation to de-identification |
| 2 | Scanner cluster (covariate, not a DBI component)                            |
| 3 | Series classification — algorithm, classes, known limitations               |
| 4 | DBI components: M, P, G, S, N (and D = 0 in v1)                             |
| 5 | Composite formula and N/A renormalization                                   |
| 6 | Reporting requirements and figures                                          |
| 7 | Reproducibility, versioning, audit trail                                    |

## Status

- **Spec:** v1.0.5 (frozen 2026-04-10)
- **Companion config:** `dbi_v1_config.yaml`
- **Cohort target:** CIDUR-style XNAT exports
  (`EP*/EP*/*_MR_*/scans/<series>/resources/DICOM/files/*.dcm`)

## Compatibility promise

Within v1, the **scoring functions** (`score_M`, `score_P`, `score_G`, `score_S`,
`score_N`, `composite_dbi`) and the **column names** in `per_series.csv` /
`per_session.csv` are stable. Patch releases (1.0.x) may add columns or relax
regexes; they will not remove columns or change the meaning of existing scores.

Breaking changes go into v2.0 and require:

- bumping `version:` in the config,
- amending the spec markdown with a `## Changelog` entry,
- and (for additive changes only) keeping the v1 reader path working.
