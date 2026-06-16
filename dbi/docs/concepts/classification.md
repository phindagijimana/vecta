# Series classification

DBI is **modality-aware**: which sub-scores apply, and what counts as a "pass",
depend on the inferred class of a series. Two classifiers are evaluated and
**both columns are emitted**.

## 1. Heuristic class (`series_class`)

Defined in `dbi_v1_config.yaml` under `classification_rules`. The classifier takes

```
"<scan_folder_basename> <SeriesDescription>"
```

(from the first readable DICOM) and applies the rules **in order**; the first
matching pattern wins.

### Classes

`dwi`, `bold`, `asl`, `fmap`, `swi`, `flair`, `perf`, `t1_anat`, `t2_anat`,
`localizer`, `other`.

### Code

`classify_series(text, rules)` in `dbi/scoring.py` — substring or regex match,
case-insensitive.

### Known limitations

- **Order sensitivity** — `T2` substrings appear in many strings, so the `flair`
  and `dwi` rules are placed earlier where possible.
- **Folder-text driven** — relies on the SeriesDescription / folder name being
  informative; for de-identified exports that strip these, fall back to the strict
  classifier below or augment the rules.

## 2. Standards classifier (`standards_compliant_class`)

A second, **strict** classifier — `standards_classify` — uses
`naming.class_series_description_compliance` from the config. Every regex listed
under `all_match` for a class must match the trimmed SeriesDescription alone.
Iteration is alphabetical; first full match wins; otherwise the row is labelled
`unclassifiable`.

The audit row also carries:

- `naming_compliant` — `True` only when heuristic class equals standards class
  *and* both are non-trivial (not `other`).
- `recommended_name_pattern` — a suggested SeriesDescription template for the
  inferred class (e.g. `<PLANE>_3D_MPRAGE` for `t1_anat`).
- `standards_gap` — a human-readable reason a series failed the standards check
  (e.g. *"Missing: has AP + direction count (e.g. AP_64_DIRECTIONS)"*).

## Why both?

| Classifier | When it's useful                                                              |
|------------|-------------------------------------------------------------------------------|
| Heuristic  | Routing pipelines, computing DBI components correctly, capturing legacy data. |
| Standards  | Reporting whether the SeriesDescription itself is structured well enough for prospective automation. |

The standards classifier is intentionally stricter so that downstream consumers
(HeuDiConv, dcm2niix sidecar emitters, ML manifests) can rely on a small grammar.
