# Scanner cluster

The scanner cluster is the **covariate** that lets you stratify DBI across
multi-vendor cohorts without baking the scanner into the score itself.

## Definition

For each session, the cluster is taken from the **first readable DICOM**:

```
Manufacturer | ManufacturerModelName | MagneticFieldStrength
```

For example:

```
SIEMENS | Skyra | 3T
GE MEDICAL SYSTEMS | DISCOVERY MR750 | 3T
Philips | Ingenia | 1.5T
```

Implementation: `scanner_cluster_from_ds()` in `dbi/scoring.py`.

## Why it is *not* a DBI component

- DBI v1 deliberately reports the cluster **alongside** the score so reviewers can
  compare apples to apples — e.g. boxplots of `DBI_session_mean_no_localizer`
  faceted by `scanner_cluster`.
- It is **not** part of the composite. A future version may add explicit
  cross-scanner calibration; in v1, that calibration would conflate "the data
  needs work" with "the scanner is different".

## Where it shows up in the output

- `series_dbi.csv` — column `scanner_cluster` (same on every row from a session).
- `session_dbi.csv` — column `scanner_cluster` for each session.
- `figure1_dbi_by_scanner.png` — box plot of session-mean DBI per cluster
  (localizers excluded).
- `dbi-convert` Table 2 — pass rate is stratified by `scanner_cluster × series_class`.

## Edge cases

- If no DICOMs are readable in a session, the cluster is
  `unknown | unknown | unknownT`.
- Field-strength values are coerced to a string (e.g. `3`, `1.5`); no rounding.
- Vendor strings are taken raw from the DICOM — minor formatting differences
  (e.g. `SIEMENS` vs `Siemens Healthineers`) will produce different clusters
  until you normalize them in post.
