# Data Birth Integrity (DBI) — Version 1.0 Specification

**Status:** Phase 1 frozen specification; v1.0.5 reframes N conventions as community-standards naming compliance with normative citations and downstream-benefit documentation.  
**Cohort target:** CIDUR-style XNAT exports (`EP*/EP*/*_MR_*/scans/<series>/resources/DICOM/files/*.dcm`)  
**Companion file:** `dbi_v1_config.yaml`  
**Date:** 2026-04-10  

---

## 1. Purpose and scope

### 1.1 Definition

**Data Birth Integrity (DBI)** is a **scalar summary (0–1)** of how well a **series** (operationalized as one XNAT scan folder) satisfies **automation-oriented structural requirements** at the moment of analysis, **before** study-specific image processing (e.g., eddy correction, segmentation). It is **not** a measure of diagnostic image quality, SNR, or clinical acceptability.

### 1.2 Design principles

1. **Reproducible:** Same DICOM inputs + same config version → same scores (deterministic).
2. **Auditable:** Every subscore traceable to explicit tag checks or string rules.
3. **Modality-aware:** Components that do not apply (e.g., gradient integrity on T1w) are **N/A**, not zero.
4. **Legacy-cohort honest:** Retrospective data without prospective `PROTO_*` tokens must not be penalized on that axis beyond a documented **ideal vs minimal** split (§4.2).

### 1.3 Units of analysis

| Unit | Definition | Primary use |
|------|------------|-------------|
| **Series** | One `scans/<name>` directory under `*_MR_*` with ≥1 `.dcm` | **DBI composite per series** |
| **Session** | One `*_MR_*` directory (one imaging visit) | **Aggregation** (mean, min, histogram) |
| **Cohort** | All sessions in release | **Stratification** by scanner cluster |

### 1.4 Relationship to de-identification

**Clarification needed from team (single choice for Methods):**

- **Option A (recommended for audit fidelity):** Compute DBI on **research export DICOM as ingested** (pre–BIDS de-ID), store only **aggregate statistics + de-identified exemplars** in public materials.
- **Option B:** Compute DBI on **de-identified DICOM** (`sub-*`); document any tags blanked by the de-ID tool.

Phase 2 implementation should accept a **root path** and optionally a **manifest** mapping EP IDs → `sub-*` without changing scoring logic.

---

## 2. Scanner cluster (covariate, not a DBI component)

For stratified tables/figures, assign each session a **scanner_cluster** string from the first successfully read DICOM in that session:

`Manufacturer | ManufacturerModelName | MagneticFieldStrength`  
(normalize whitespace; field strength as string, e.g. `3`).

This label is **reported alongside** DBI; it does not enter the composite unless a future version adds explicit cross-scanner calibration.

---

## 3. Series classification

### 3.1 Algorithm

Concatenate **scan folder basename** + space + **SeriesDescription** (empty if missing) from the **first readable DICOM** in the folder. Apply rules in `dbi_v1_config.yaml` → `classification_rules` **in order**; first matching pattern wins. If none match → class `other`.

### 3.2 Classes

`dwi`, `bold`, `asl`, `fmap`, `swi`, `flair`, `perf`, `t1_anat`, `t2_anat`, `localizer`, `other`.

### 3.3 Known limitations

- **Order sensitivity:** e.g. `T2` appears in many strings; `flair` and `dwi` rules are placed earlier where possible.
- **Validation subset (Phase 4 optional):** Human labels on 20–50 series to report precision/recall of class assignment.

---

## 4. DBI components (series-level)

Each component produces:

- `score ∈ [0, 1]` **or**
- `na = true` (excluded from composite denominator; see §5).

Default weights (applicable components only): see `dbi_v1_config.yaml` → `weights` (M, P, G, S, N sum to 1.0; **D drift = 0** in v1).

---

### 4.1 M — Metadata completeness

**Applicable:** All classes except we optionally treat `localizer` with a **reduced** checklist (team choice: same as full or exclude localizers from cohort summaries).

**Method:** Define a set of **required elements** per class. Each present element contributes equally to M.

**Universal (all non-localizer):**

| Element | Satisfied if |
|---------|----------------|
| modality_mr | (0008,0060) Modality present and equals `MR` (case-insensitive) |
| manufacturer | (0008,0070) non-empty |
| model | (0008,1090) non-empty |
| field_strength | (0018,0087) parseable positive number |
| series_uid | (0020,000E) non-empty |
| study_uid | (0020,000D) non-empty |

**Descriptive text (at least one):**

| Element | Satisfied if |
|---------|----------------|
| series_or_protocol_text | (0008,103E) SeriesDescription **or** (0018,1030) ProtocolName non-empty after strip |

**Spatial (all except `localizer` and `other` if no pixel data — use judgment in Phase 2):**

| Element | Satisfied if |
|---------|----------------|
| in_plane_spacing | (0028,0030) PixelSpacing or (0018,1164) ImagerPixelSpacing present with two positive values |
| slice_info | (0018,0050) SliceThickness **or** (0018,0088) SpacingBetweenSlices present and within YAML `spatial` mm bounds |

**Class-specific add-ons:**

| Class | Extra elements |
|-------|----------------|
| `dwi` | At least one diffusion-related signal (§4.3) scores partial credit toward M_diffusion |
| `bold` | (0018,0080) RepetitionTime and (0018,0081) EchoTime present and > 0 |
| `asl` | Same TR/TE **or** documented ASL-specific tags if present in sample (Phase 2 enumerates after tag audit) |
| `fmap` | (0018,0081) EchoTime present (dual-echo: max TE across instances if needed) |

**M formula:**  
`M = (# satisfied required elements) / (# required elements for that class)`  
If class `localizer`: use only universal + descriptive (no spatial) **or** exclude from paper’s primary histogram (document choice).

---

### 4.2 P — Protocol / naming conformity

Split into two **reportable** sub-scores (both 0–1); **composite P** = `0.5 * P_minimal + 0.5 * P_ideal` (document in Methods).

**P_minimal (retrospective fairness):**

| Criterion | Score |
|-----------|-------|
| Scan folder matches `^[0-9]+-` (XNAT-style index + description) | 1 else 0 |
| Not both SeriesDescription and ProtocolName empty | 1 else 0 |

`P_minimal = average of the two.`

**P_ideal (prospective alignment):**

| Criterion | Score |
|-----------|-------|
| `SeriesDescription` or `ProtocolName` matches `PROTO_[A-Z0-9_]+` from config (regex) | 1 else 0 |

For legacy CIDUR, **P_ideal** is expected to be **often 0**; the paper should report **P_minimal** as primary for this cohort and **P_ideal** as forward-looking standard.

---

### 4.3 G — Gradient integrity (diffusion only)

**Applicable:** `class == dwi` only. **Else:** `na = true`.

**Goals:** (1) Detect likely **raw** diffusion encoding vs obvious **derived** scalar maps; (2) Require evidence that **b-values and directions** are discoverable from DICOM for at least one instance.

**Step A — Derivative penalty**  
If folder name **or** SeriesDescription matches any token in `naming.derivative_tokens` (case-insensitive, whole-token or substring per YAML policy in Phase 2), set **G = 0** and flag `derivative_series = true` (pipeline should not treat as raw DWI).

**Step B — Encoding evidence (if not derivative)**  
Award partial credit (implementation detail in Phase 2):

1. **Classic / mosaic single-frame:** presence of per-instance or per-slice tags commonly carrying diffusion info (vendor-dependent enumeration using pydicom + documented private tag ranges **only if** legally/ethically allowed to document).
2. **Enhanced MR / multiframe:** successful read of **Shared Functional Groups** or **Per-Frame Functional Groups** containing **DiffusionBValue** and gradient direction information for more than one frame.

**G formula (conceptual):**  
`G = 0` if derivative; else `G = w1*I_bvalue + w2*I_direction + w3*I_volume_count` with weights summing to 1 (Phase 2 sets `w` after pilot on 5 series per scanner cluster). Minimum floor: if **any** b-value > 0 readable → `I_bvalue = 1`.

**Clarification for Phase 2:** If Siemens **separate series** for ADC/FA are already classified as non-`dwi` by §3, Step A may rarely trigger; keep Step A for GE-style combined naming.

---

### 4.4 S — Spatial consistency

**Applicable:** All classes except `localizer` (optional `na`) and `other` (score 0 if no imaging geometry).

Parse pixel spacing and slice thickness / spacing; verify values fall within `spatial` min/max in YAML.  
**S = 1** if all applicable spatial checks pass; **S = 0.5** if in-plane OK but slice info missing; **S = 0** if in-plane missing or out of range.

---

### 4.5 N — Naming compliance (community-standards naming compliance)

**Applicable:** All.

**Design rationale:** Component N measures compliance with naming conventions derived from **published community standards** — primarily the Brain Imaging Data Structure (BIDS; Gorgolewski et al. 2016), multi-site consortium protocol guides (ENIGMA: Thompson et al. 2020; ADNI: Jack et al. 2008), and DICOM interoperability requirements (Bidgood & Horii 1997; Rorden et al. 2025). Because these standards are external to any single institution, N scores measure distance from community conventions rather than conformity to site-specific patterns.

Each convention is simultaneously grounded in a normative standard **and** designed to make four downstream workflows measurably easier: **(1) automated BIDS conversion** (dcm2niix, HeuDiConv), **(2) AI/ML pipeline ingestion**, **(3) programmatic data cleaning**, and **(4) automated pipeline routing** (fMRIPrep, MRIQC). The YAML configuration documents both the normative source and the downstream benefits for each check (see `dbi_v1_config.yaml` → `naming.automation_conventions`).

**Structural checks (always applied):**

| # | Criterion | Standard | Implementation note |
|---|-----------|----------|----------------------|
| 1 | Folder matches `naming.scan_folder_pattern` | XNAT export convention (Marcus et al. 2007) | `^[0-9]+-` or synthetic label from `SeriesNumber` |
| 2 | No embedded path separators in scan basename | POSIX portable filenames (IEEE 1003.1) | `/` and `\` disallowed |
| 3 | SeriesDescription length ≤ 128 chars | DICOM VR LO limit (PS3.5); JSON sidecar compatibility | > 128 → 0.5 credit |

**Community-standards naming conventions (v1.0.1+, v1.0.5 expanded):**

Additional **binary** checks in `dbi_v1_config.yaml` → `naming.automation_conventions`. Each entry documents `id`, `rationale`, `source` (normative citation), `downstream_benefit` (AI/BIDS/cleaning/automation workflows enabled), `regex`, and `enabled`. They reward naming patterns that satisfy **published standards** while simultaneously enabling downstream automation:

| Convention | Normative source | Downstream workflows enabled |
|-----------|-----------------|------------------------------|
| **Control-character safety** | RFC 8259 (JSON); BIDS sidecar spec | BIDS sidecar emission, CSV/pandas ingest, ML dataset loaders |
| **BIDS entity tokens** (`run-`, `acq-`, `dir-`, `echo-`, …) | BIDS v1.9 entity system (Gorgolewski et al. 2016) | HeuDiConv heuristic auto-detection, deterministic file renaming, ML metadata parsing |
| **Modality / contrast lexicon** (T1w, DWI, BOLD, FLAIR, …) | BIDS suffixes; ENIGMA/ADNI protocol guides | dcm2niix/HeuDiConv suffix assignment, fMRIPrep/MRIQC series routing, ML modality classification |
| **Token separators** (hyphen/underscore delimiters) | BIDS filename convention; POSIX portable filenames | Regex/split-based metadata extraction, safe shell globbing, NLP tokenization |
| **PHI-safe naming** (no MRN-like digit runs, no date patterns) | DICOM PS3.15 Annex E; Aryanto et al. 2015; HIPAA Safe Harbor | Automated PHI detection, safe ML training data curation, clean BIDS sidecars |
| **Sequence parameter encoding** (b-values, direction counts, TE/TR) | ENIGMA-DTI protocol (Thompson et al. 2020); ADNI procedures (Jack et al. 2008) | Name–header cross-verification, filename-based feature extraction, automated QC triage |

**Evaluation text:** `scan_folder_basename + " " + SeriesDescription + " " + ProtocolName` (trimmed). If that string is **empty**, convention checks are **skipped** (only the three structural checks apply) — so missing tags do not invent false failures.

**Per-class SeriesDescription compliance (v1.0.2+):**

After heuristic **series class** is assigned, optional rules in `naming.class_series_description_compliance` add **one** extra binary check: **all** regexes in `all_match` must match **trimmed SeriesDescription alone** (not folder name). Classes omitted from this block incur **no** extra check. **Empty SeriesDescription** → that check **fails** (0) when the class has a rule block.

Patterns align with BIDS modality suffixes (Gorgolewski et al. 2016), dcm2niix heuristic expectations (Li et al. 2016), and consortium naming guides (ENIGMA, ADNI). Compliance enables deterministic BIDS conversion, automated pipeline routing, and ML-based series classification.

| Class | Intent (summary) |
|-------|------------------|
| `dwi` | Contains DTI/DWI/dti/dwi **and** phase/direction count pattern **AP** + digits + directions |
| `fmap` | Field-map–like text **and** **PA** + digits + directions (parallel to DWI AP convention) |
| `bold` | Contains fMRI/fmri, BOLD, RESTING, TASK, EPI, or rsfMRI |
| `asl` | Contains ASL |
| `flair` | **Ends** with FLAIR or flair |
| `perf` | Contains perf, DSC, DCE, or CBF |
| `t1_anat` | **Ends** with MPRAGE, SPGR, FSPGR, BRAVO, or IR_FSPGR |
| `localizer` | Contains localizer, Localizer, LOC, or scout |
| `t2_anat` | Contains **T2** or **BLADE**; **ends** with **THIN** |
| `swi` | Contains **SWI** or **SWAN** |

**Derived / reformatted series (v1.0.3+):** If `naming.derived_scan_naming` is enabled and **any** configured **marker** matches the **combined** folder + SeriesDescription + ProtocolName string, then **SeriesDescription** must match `series_description_suffix_regex` (default: ends with **reformat** or **derived**, case-insensitive). This follows the BIDS derivatives specification and dcm2niix derivative handling (Li et al. 2016) for unambiguous raw-vs-derived series discrimination — critical for AI/ML training set curation (excluding derived maps), automated BIDS derivatives layout, and data cleaning pipelines.

**Score:**  
\[
N = \frac{1}{K}\sum_{k=1}^{K} \mathbb{1}_k
\]
where \(K\) is the count of enabled checks (structural + community-standards conventions when combined text is non-empty + optional per-class SD check when configured).  
`per_series.csv` reports **`N_pass`** and **`N_total`** for transparency.

**Multi-site portability:** Because conventions are grounded in published community standards rather than site-specific patterns, multi-site deployment requires no re-calibration of these components. Sites that intentionally depart from a standard may override individual conventions (`enabled: false`) or replace regexes in the YAML without changing the composite weight on **N**. Low scores on community-standards conventions in clinical DICOM are expected and informative — they quantify the curation effort required to bring raw acquisitions into compliance with community standards.

---

### 4.6 D — Drift control

**v1 retrospective:** **Not scored** (`na = true` for all series, or omit from composite). **Rationale:** PDI requires **protocol version time series** across acquisitions; not identifiable from single static export without external logs.

**Future:** Session-level variance in `SoftwareVersions` (0018,1020) across series, or explicit `protocol_version` in DICOM/custom tag.

---

## 5. Composite DBI (series-level)

Let applicable components be those with `na = false`. Let weights `w_c` come from config for `c ∈ {M, P, G, S, N}` (renormalize if some excluded).

```
DBI_series = Σ_c (w_c * score_c) / Σ_c w_c
```

**Reported alongside:**

- `class`, `scanner_cluster`, `derivative_series` (bool), flags for DICOM read failures.

---

## 6. Session-level aggregation

For each `*_MR_*` session:

- **DBI_session_mean** = mean of `DBI_series` over all series (optionally **exclude `localizer`** — document).
- **DBI_session_min** = min (worst series).
- **DBI_session_p10** = 10th percentile (robust summary).

**Paper recommendation:** Primary figure = **distribution of DBI_session_mean** by **scanner_cluster**; supplement = per-component heatmaps.

---

## 7. Pseudocode

```
function score_session(mr_root):
    clusters = []
    for scan_dir in list_scan_folders(mr_root):
        dcm = first_dicom(scan_dir)
        if dcm is None:
            record FAILURE; continue
        ds = read(dcm, stop_before_pixels=True)
        cls = classify(scan_dir, ds)
        M = score_metadata(ds, cls)
        P = score_protocol(scan_dir, ds)
        G = score_gradient(ds, scan_dir, cls)   # na if cls != dwi
        S = score_spatial(ds, cls)
        N = score_naming(scan_dir, ds)
        D = NA
        DBI = composite([M,P,G,S,N,D], weights)
        append row(scan_dir, cls, M,P,G,S,N,DBI, flags)
    return aggregate_session_stats(rows)
```

---

## 8. Versioning and changelog

| Version | Date | Notes |
|---------|------|--------|
| 1.0.0 | 2026-04-09 | Initial Phase 1 freeze |
| 1.0.1 | 2026-04-09 | N: `automation_conventions` in YAML; audit CSV `N_pass` / `N_total` |
| 1.0.2 | 2026-04-09 | N: `class_series_description_compliance`; classification_rules tightened per site SOP |
| 1.0.3 | 2026-04-09 | N: t2_anat + swi SD rules; `derived_scan_naming`; swi classification tokens only SWI/SWAN |
| 1.0.4 | 2026-04-10 | Bug fix: PixelSpacing isinstance check now handles pydicom MultiValue (S, M spatial check) |
| 1.0.5 | 2026-04-10 | N: reframed as **community-standards naming compliance**; conventions now cite normative sources (BIDS, ENIGMA, ADNI, DICOM PS3.15, POSIX, RFC 8259) and document downstream benefits (AI/ML, BIDS conversion, data cleaning, pipeline routing); added `no_phi_leak_tokens` and `sequence_param_encoding` conventions; multi-site portability argument formalized |

---

## 9. Clarifications requested from the team (minimal)

1. **De-ID path (§1.4):** Option A vs B for **primary** DBI computation.
2. **Localizers:** Include in global DBI histograms or exclude from primary endpoint?
3. **Protocol regex:** Replace `PROTO_[A-Z0-9_]+` with your real token when prospective acquisitions begin (v1 paper can keep regex as **example**).

---

## 10. Phase 2 implementation checklist

- [ ] Load `dbi_v1_config.yaml` (PyYAML).
- [ ] Walk CIDUR tree; emit `per_series.csv` + `per_session.csv`.
- [ ] Unit tests: synthetic minimal DICOM or anonymized snippets (public).
- [ ] Log pydicom read errors without stopping batch.

---

*End of DBI v1 specification.*
