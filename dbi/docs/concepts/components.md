# Components (M / P / G / S / N)

All five sub-scores live in `dbi/scoring.py`. Each returns a value in `[0, 1]` or a
boolean N/A flag.

---

## M — Metadata completeness

**Weight:** 0.28 · **Applicable:** all classes (reduced checklist for `localizer`)

A pass/fail tally of required DICOM elements, where M = `n_pass / n_total`. The
universal checks are:

| Element                  | DICOM tag      | Pass condition                       |
|--------------------------|----------------|--------------------------------------|
| Modality = MR            | (0008,0060)    | present, equals `MR` case-insensitive |
| Manufacturer             | (0008,0070)    | non-empty                            |
| Model                    | (0008,1090)    | non-empty                            |
| Field strength           | (0018,0087)    | parseable, > 0                       |
| SeriesInstanceUID        | (0020,000E)    | non-empty                            |
| StudyInstanceUID         | (0020,000D)    | non-empty                            |
| Some descriptive text    | (0008,103E) or (0018,1030) | at least one non-empty |

Plus class-conditional spatial / sequence checks:

| Added when class is …  | Extra check                                              |
|------------------------|----------------------------------------------------------|
| not `localizer`        | in-plane pixel spacing within spatial bounds             |
| not `localizer`        | slice thickness OR spacing-between-slices within bounds  |
| `dwi`                  | diffusion evidence present (see `score_G`)               |
| `bold`, `asl`          | TR > 0 and TE > 0                                        |
| `fmap`                 | TE > 0                                                   |

---

## P — Protocol naming

**Weight:** 0.18 · **Applicable:** all classes

P is the average of two halves:

- **P_minimal** — the scan folder matches `^[0-9]+-` AND some descriptive text exists
  (SeriesDescription or ProtocolName non-empty). Worth 0.5 of P.
- **P_ideal** — `SeriesDescription + " " + ProtocolName` matches the
  `protocol_token.pattern` regex from the config (e.g., the prospective `PROTO_*`
  marker). Worth the other 0.5.

P = 0.5 × P_minimal + 0.5 × P_ideal.

Legacy cohorts without prospective `PROTO_*` tokens can still earn P = 0.5 (the
minimal half) — they are not double-penalized for a convention that did not exist
when the data was acquired.

---

## G — Gradient integrity (DWI)

**Weight:** 0.22 · **Applicable:** `dwi` only — N/A for every other class.

For `dwi` series, G is a weighted indicator over three checks:

| Check                                          | Weight |
|------------------------------------------------|:------:|
| b-value evidence (`DiffusionBValue`, ImageType, enhanced/multiframe…) | 0.45 |
| Gradient direction info (DiffusionGradientOrientation, multiframe…)  | 0.45 |
| Volume / multiframe sanity                     |  0.10  |

A **derived-DWI** series (folder/SeriesDescription contains `ADC`, `FA`, `TRACE`,
`ColFA`, `MD`, `RGB`, `mIP`, …) automatically scores `G = 0` and gets flagged
`derivative_series = True` — derived maps don't need gradient tables, but they're
not raw DWI either.

---

## S — Spatial consistency

**Weight:** 0.17 · **Applicable:** all classes (`localizer` returns 1.0 by spec)

| Condition                                                            | S    |
|----------------------------------------------------------------------|:----:|
| In-plane pixel spacing within bounds AND slice thickness within bounds | 1.0 |
| In-plane only                                                        | 0.5  |
| Neither                                                              | 0.0  |

Bounds default to `0.05 mm ≤ pixel ≤ 15 mm` and `0.05 mm ≤ slice ≤ 20 mm` — see
[Configuration → `spatial`](../configuration/yaml-reference.md).

---

## N — Naming compliance

**Weight:** 0.15 · **Applicable:** all classes

N is the mean of a set of binary checks; the exact count varies with the config:

1. Scan folder matches `naming.scan_folder_pattern` (default `^[0-9]+-`).
2. Folder name does not contain path separators (`/`, `\`).
3. SeriesDescription length ≤ 128.
4. **Automation conventions** (toggleable in the config) — e.g. no ASCII control
   chars, ASCII-printable, no whitespace at edges, BIDS entity tokens detectable.
   See [Configuration → Naming conventions](../configuration/naming-conventions.md).
5. **Per-class SeriesDescription compliance** — every regex in
   `class_series_description_compliance[<class>].all_match` must match.
6. **Derived-scan suffix rule** — if the combined text matches a derivative marker,
   the SeriesDescription must end with `(reformat|derived)`.

Each binary check contributes equally, so a series that passes 6 of 7 conventions
scores N ≈ 0.857.

---

## How components combine

The composite uses the weights above and the renormalization rule in
[The DBI score](dbi-score.md). For a clean DWI series with all checks passing,
DBI = 1.0; for a derived DWI series (G = 0, everything else perfect),
DBI ≈ 0.78 — the headline weight loss comes from the 0.22 on G.
