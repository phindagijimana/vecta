# QC spot-check

The audit is purely mechanical — it trusts what's in the DICOM. A reviewer-driven
spot-check is the v1 way to validate that the automated scores match what a
human sees at the scanner console.

## The template

`qc_spotcheck_template.csv` has the columns:

| Column                          | Notes                                                      |
|---------------------------------|------------------------------------------------------------|
| `row_index`                     | Row in `per_series.csv` you are reviewing.                  |
| `session_id`                    | From the audit.                                            |
| `scan_folder`                   | From the audit.                                            |
| `dicom_path`                    | From the audit — the file the reviewer should open.        |
| `reviewer`                      | Free text (initials / email).                              |
| `date`                          | ISO-8601 review date.                                      |
| `console_M_P_G_S_N_agrees`      | `Y` / `N` for each component (e.g. `Y/Y/N/Y/Y`).            |
| `notes`                         | Free-text justification when disagreeing with the score.   |

## A recommended procedure

1. **Sample.** Stratified random sample of ~20–50 rows from `per_series.csv`,
   covering each `series_class` and `scanner_cluster`.
2. **Open.** For each row, open `dicom_path` in a viewer that shows raw DICOM
   tags (e.g. dcmdump, OsiriX / Horos tag inspector, or `pydicom` interactively).
3. **Check.** For each component, decide if the score agrees with what you see
   on the console — metadata present? naming sensible? gradients sane (DWI)?
   spacing realistic? naming compliant?
4. **Record.** Fill in `console_M_P_G_S_N_agrees` and add a note when you disagree.
5. **Report.** Aggregate: percentage agreement per component, plus reasons for
   the most common disagreements. Disagreements often point to **config bugs**
   (regex too strict / lax) rather than scoring bugs.

## Why this matters

DBI is an automation-oriented metric, but config decisions (which automation
conventions to enable, which classification rules to allow) are still
**editorial**. A small QC loop keeps them honest, and the diff between two
reviewers is a good way to catch ambiguous SeriesDescription strings before they
go into a downstream training set.
