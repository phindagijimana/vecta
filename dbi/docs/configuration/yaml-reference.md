# YAML reference

Section-by-section walk-through of `dbi_v1_config.yaml`. All defaults shown are
v1.0.5.

## `weights`

```yaml
weights:
  metadata_completeness: 0.28
  protocol_naming:       0.18
  gradient_integrity:    0.22
  spatial_consistency:   0.17
  naming_compliance:     0.15
  drift_control:         0.00   # v1: not scored
```

Composite weights for [the DBI score](../concepts/dbi-score.md). The applicable
weights must sum to 1.0; when a component is N/A its weight is excluded from the
denominator (renormalization).

`drift_control` is reserved for v2.

## `spatial`

```yaml
spatial:
  min_pixel_spacing_mm:   0.05
  max_pixel_spacing_mm:  15.0
  min_slice_thickness_mm: 0.05
  max_slice_thickness_mm: 20.0
```

Physical-plausibility bounds for the S and (part of) M components. Values outside
the range fail the check; values exactly equal to the bound pass.

## `tags_universal` and `tags_spatial`

```yaml
tags_universal:
  - ["Modality", "00080060"]
  ...
tags_spatial:
  - ["PixelSpacing", "00280030"]
  ...
```

**Informative only** — the reader uses `pydicom` tags directly. These blocks
document which DICOM elements DBI inspects, for spec readers.

## `naming`

```yaml
naming:
  scan_folder_pattern: '^[0-9]+-'
  derivative_tokens: ["ADC", "FA", "TRACE", "TRACEW", "ColFA", "MD", "RGB", "mIP", "MIP", "ORIG"]
  automation_conventions: [...]            # see Naming conventions page
  class_series_description_compliance: ... # per-class SeriesDescription regexes
  derived_scan_naming: ...                 # suffix rule for derived series
```

- `scan_folder_pattern` — the regex behind the first N-check (scan folder must
  start with `<number>-`).
- `derivative_tokens` — case-insensitive delimited tokens; if any appear in the
  combined text, the series is flagged as derived (G = 0, derived-scan-suffix
  check active).
- `automation_conventions` — toggleable, citation-backed conventions. Each is a
  separate binary check inside N. See [Naming conventions](naming-conventions.md).
- `class_series_description_compliance` — per-class `all_match` regex lists used
  by both `score_N` and the standards classifier.
- `derived_scan_naming` — if combined text matches a derivative marker, the
  SeriesDescription must end with `(reformat|derived)` (configurable).

## `protocol_token`

```yaml
protocol_token:
  required_for_full_credit: false
  pattern: 'PROTO_[A-Z0-9_]+'
```

Used by `score_P` to compute the **P_ideal** half. Sites that want to enforce a
prospective scanner-console token can change `pattern`; legacy cohorts without
the token still earn the **P_minimal** half.

## `classification_rules`

```yaml
classification_rules:
  - class: fmap
    patterns: ["field_map", "field map", "(?i)\\bPA[_\\s-]*\\d+.*(DIRECTION|DIR)", ...]
  - class: dwi
    patterns: ["DTI", "DWI", "DIFFUSION", ...]
  - class: bold
    patterns: ["fMRI", "BOLD", "RESTING", ...]
  ...
  - class: other
```

Heuristic classifier — rules apply **in order**, first match wins. A pattern is
treated as a regex if it contains regex metacharacters, otherwise as a substring.
Order matters: `fmap` is placed before `dwi` because some fmap descriptions
contain `DIR`; `flair` is before `t2_anat` because `T2 FLAIR` would otherwise hit
`T2` first.

The final `class: other` with no patterns is the default sink.
