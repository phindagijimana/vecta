# Naming conventions

The `naming.automation_conventions` block in
[`dbi_v1_config.yaml`](https://github.com/phindagijimana/vecta/blob/main/dbi/dbi_v1_config.yaml)
is the heart of the N component. Each convention is a **single regex** applied
to the combined string

```
"<scan_folder_basename> <SeriesDescription> <ProtocolName>"
```

(or, equivalently, declared *not applicable* when that string is empty). Each
convention is one binary check inside N — they contribute equally to the
component.

Conventions cite published normative sources; the rationale for each
explicitly lists the downstream workflow it enables.

## v1.0.5 conventions

| ID                          | Source                                                                                       | What it enforces                                                                  |
|-----------------------------|----------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| `no_control_chars`          | RFC 8259 (JSON); BIDS sidecar spec                                                            | No ASCII control characters in the combined text.                                  |
| `bids_entity_tokens`        | BIDS v1.9; HeuDiConv                                                                          | BIDS entity tokens (`run-`, `acq-`, `ses-`, …) detectable in the text.            |
| `modality_contrast_lexicon` | BIDS suffixes; ENIGMA; ADNI                                                                   | At least one canonical modality / contrast token (`T1w`, `FLAIR`, `DWI`, …).      |
| `token_separators`          | BIDS filename spec; POSIX IEEE 1003.1                                                          | Alphanumeric segments separated by `-` or `_` (no ambiguous whitespace).          |
| `no_phi_leak_tokens`        | DICOM PS3.15 Annex E; HIPAA Safe Harbor; Aryanto et al. 2015                                  | No date-like patterns or 7+ digit runs that resemble PHI.                         |
| `sequence_param_encoding`   | ENIGMA-DTI (Thompson 2020); ADNI MRI procedures (Jack 2008)                                   | Sequence parameters encoded in the name (`b1000`, `64dir`, `TE30`, `TR2000`, …). |

Each has fields:

```yaml
- id: bids_entity_tokens
  rationale: >-
    BIDS entity keys (run-, acq-, dir-, echo-, flip-, inv-, ses-, sub-) are
    the community standard for encoding acquisition parameters in filenames.
    Their presence in raw SeriesDescription or ProtocolName signals
    prospective BIDS alignment at the scanner console, reducing HeuDiConv
    heuristic complexity.
  source: "BIDS v1.9 (Gorgolewski et al. 2016); HeuDiConv (Halchenko et al. 2024)"
  downstream_benefit:
    - "BIDS conversion: HeuDiConv heuristic auto-detection"
    - "Automation: deterministic file renaming without manual mapping tables"
    - "AI/ML: structured metadata parsing for experiment-level feature extraction"
  regex: '(?i)(?<![A-Za-z0-9])(?:run|acq|dir|echo|flip|inv|ses|sub)[_-][A-Za-z0-9]'
  enabled: true
```

## Per-class SeriesDescription compliance

`naming.class_series_description_compliance` defines **`all_match`** regex lists
per class. The trimmed SeriesDescription alone is tested — empty descriptions
fail. Omitted classes do not get an extra N check.

For example:

```yaml
class_series_description_compliance:
  dwi:
    all_match:
      - '(?i)(DTI|DWI|dwi|dti)'
      - '(?i)AP[_\s-]*\d+.*(DIRECTION|DIR|direction)s?'
  t1_anat:
    all_match:
      - '(?i)(MPRAGE|MP[\s_-]RAGE|SPGR|FSPGR|BRAVO|IR[\s_]FSPGR)\s*\Z'
```

A DWI series passes this only if both **(a)** it contains a DTI/DWI token AND
**(b)** it carries an `AP_<N>_DIRECTIONS`-style direction count.

This block is also what the standards classifier (`standards_classify`) uses to
produce `standards_compliant_class` and the `standards_gap` reason string.

## Derived-scan suffix rule

```yaml
derived_scan_naming:
  enabled: true
  markers: ["ADC", "FA", "TRACE", "TRACEW", "ColFA", "MD", "RGB", "mIP", "MIP", "ORIG"]
  series_description_suffix_regex: '(?i)(reformat|derived)\s*\Z'
```

If the combined text matches one of the markers (as a delimiter-bounded token),
SeriesDescription must end with `reformat` or `derived`. This separates raw
volumes from scanner-generated maps in a way that downstream tools (BIDS
derivatives layout, ML training-set curation) can rely on.

## Disabling a convention per-site

Copy the config, flip `enabled: false`, and pass `--config` to either CLI. The
convention's binary check is then **removed** from N — it doesn't contribute to
either numerator or denominator.
