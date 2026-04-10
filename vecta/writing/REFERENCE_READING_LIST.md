# DBI v1 Manuscript — Structured Reference & Reading List

**For:** NeuroImage methods paper on Data Birth Integrity (DBI)  
**Companion file:** `references.bib` (BibTeX)  
**Generated:** 2026-04-10  

---

## How to use this document

Each **Cluster** maps to a section or argument in the manuscript. Papers are ranked
**Tier 1** (must cite — foundational or direct prior art), **Tier 2** (strongly recommended —
context/contrast), or **Tier 3** (cite if space allows or if reviewer asks). The manuscript
column shows where each reference naturally appears.

---

## Cluster A — The gap: DICOM variability across vendors

**Manuscript section:** Introduction §1–2, Methods background

| Tier | Reference | Why it matters |
|------|-----------|----------------|
| **1** | Bidgood & Horii (1997) JAMIA | Canonical DICOM standard overview; establishes that interoperability was a design goal but vendor-specific private tags undermine it |
| **1** | Rorden et al. (2025) Sci Data | Most recent: cross-manufacturer DICOM benchmark datasets; directly validates DBI's premise that vendor encoding differs |
| **2** | Larobina & Murino (2014) J Digital Imaging | Medical image file format review; DICOM vs NIfTI vs Analyze strengths/limitations |
| **2** | "Thirty Years of DICOM" (2023) J Digital Imaging | Historical evolution + remaining gaps; positions DBI as addressing what DICOM alone cannot enforce |

**Key argument they support:** *DICOM is necessary but not sufficient for automation-ready neuroimaging; vendor-specific metadata encoding creates a structural readiness gap that DBI quantifies.*

---

## Cluster B — Standards and data organization: BIDS, FAIR

**Manuscript section:** Introduction §3, Related Work

| Tier | Reference | Why it matters |
|------|-----------|----------------|
| **1** | Gorgolewski et al. (2016) Sci Data | BIDS — the standard DBI is "pre-" to; DBI scores whether raw DICOM is ready for BIDS-adjacent pipelines |
| **1** | Wilkinson et al. (2016) Sci Data | FAIR principles — DBI operationalizes "Interoperable" and "Reusable" at the DICOM-series level |
| **2** | Norgaard et al. (2022) Sci Data | PET-BIDS extension — shows BIDS keeps expanding; upstream data quality matters more as modalities grow |
| **2** | Markiewicz et al. (2021) eLife | OpenNeuro — largest BIDS repository; illustrates the endpoint DBI prepares data for |

**Key argument:** *BIDS solves the curated-dataset problem; DBI scores whether raw clinical DICOM is structurally ready to enter that pipeline, before curation begins.*

---

## Cluster C — Conversion tools: dcm2niix, HeuDiConv, bids-validator

**Manuscript section:** Methods (Phase 3), Related Work

| Tier | Reference | Why it matters |
|------|-----------|----------------|
| **1** | Li et al. (2016) J Neurosci Methods | dcm2niix — the converter used in Phase 3; must cite with pinned version |
| **2** | Halchenko et al. (2024) JOSS | HeuDiConv — DICOM→BIDS layer; DBI scoring happens before this step |
| **2** | bids-validator (GitHub) | Automated BIDS compliance; contrast: bids-validator checks *curated* output, DBI checks *raw input* |

**Key argument:** *DBI is upstream of conversion: series that score low on DBI are more likely to fail or produce incomplete NIfTI/BIDS outputs.*

---

## Cluster D — Research PACS / archive infrastructure

**Manuscript section:** Methods (cohort description)

| Tier | Reference | Why it matters |
|------|-----------|----------------|
| **1** | Marcus et al. (2007) Neuroinformatics | XNAT — your CIDUR data uses XNAT-style exports |

**Key argument:** *The audit operates on institutional XNAT exports; XNAT provides the folder/session structure but does not enforce the metadata completeness DBI measures.*

---

## Cluster E — Image quality control (contrast with DBI)

**Manuscript section:** Discussion (scope / limitations), Related Work

| Tier | Reference | Why it matters |
|------|-----------|----------------|
| **1** | Esteban et al. (2017) PLoS ONE | MRIQC — canonical image-QC tool; **DBI is not image QC** — cite to explicitly delineate scope |

**Key argument:** *DBI measures structural/metadata readiness for automation, not radiological image quality. MRIQC operates downstream on converted NIfTI; DBI operates upstream on raw DICOM.*

---

## Cluster F — Multi-site harmonization / scanner variability

**Manuscript section:** Discussion, Results interpretation (Table 1 scanner clusters)

| Tier | Reference | Why it matters |
|------|-----------|----------------|
| **1** | Fortin et al. (2017) NeuroImage | ComBat DTI harmonization — establishes that scanner effects are real and measurable |
| **2** | Fortin et al. (2018) NeuroImage | ComBat cortical thickness — extends to structural MRI |
| **2** | Thompson et al. (2020) Transl Psychiatry | ENIGMA — largest multi-site consortium; shows that protocol standardization at acquisition is critical |

**Key argument:** *DBI's scanner-cluster stratification (Table 1, Figure 1) reveals structural readiness variation attributable to acquisition site/scanner, complementing downstream harmonization (ComBat) with an upstream diagnostic.*

---

## Cluster G — Diffusion MRI quality / gradient integrity

**Manuscript section:** Methods §4.3 (component G), Results (DWI subgroup)

| Tier | Reference | Why it matters |
|------|-----------|----------------|
| **1** | Bastiani et al. (2019) NeuroImage | QUAD/SQUAD — automated diffusion QC via FSL EDDY; contrast: operates on processed volumes, DBI G checks DICOM-level b-value/direction evidence |

**Key argument:** *DBI component G detects whether diffusion encoding metadata is discoverable from DICOM before any processing begins — a prerequisite for tools like EDDY/QUAD.*

---

## Cluster H — Pipelines requiring structured input

**Manuscript section:** Introduction (motivation), Discussion (downstream impact)

| Tier | Reference | Why it matters |
|------|-----------|----------------|
| **1** | Esteban et al. (2019) Nature Methods | fMRIPrep — requires BIDS input with correct metadata; illustrates what breaks when upstream DICOM is malformed |
| **2** | Gorgolewski et al. (2011) Front Neuroinform | Nipype — pipeline framework; depends on correct metadata propagation |
| **3** | Fischl (2012) NeuroImage | FreeSurfer — widely used downstream; requires correct spatial geometry from conversion |

**Key argument:** *Modern neuroimaging pipelines assume well-formed input. DBI quantifies whether that assumption holds at the source — before a single pipeline is invoked.*

---

## Cluster I — Reproducibility / open science

**Manuscript section:** Introduction (framing), Discussion

| Tier | Reference | Why it matters |
|------|-----------|----------------|
| **1** | Poldrack et al. (2017) Nat Rev Neurosci | Reproducibility crisis in neuroimaging — the broadest framing for why DBI matters |
| **3** | Halchenko & Wagner (2021) JOSS | DataLad — version control for data; reproducibility infrastructure |

**Key argument:** *Poldrack et al. identify analytical flexibility and insufficient methods reporting as threats to reproducibility. DBI contributes by making metadata readiness auditable, versioned, and transparent at the point of data creation.*

---

## Cluster J — Metadata quality scoring (closest prior art)

**Manuscript section:** Related Work (differentiation)

| Tier | Reference | Why it matters |
|------|-----------|----------------|
| **2** | MIDRC CRP 12 (2024) | DICOM quality/provenance objects for radiology (CT/XR focus); closest conceptual cousin to DBI but different domain and granularity |
| **3** | METRICS (2024) Insights Imaging | Quality scoring framework for radiomics; analogy for composite-score methodology |

**Key argument:** *No published tool scores DICOM-level structural readiness for neuroimaging automation across modality-specific components (M/P/G/S/N). MIDRC addresses radiology broadly; METRICS addresses radiomics methodology. DBI fills the neuroimaging-specific gap.*

---

## Cluster K — Software tools used in DBI implementation

**Manuscript section:** Methods (software and reproducibility)

| Tier | Reference | Why it matters |
|------|-----------|----------------|
| **1** | pydicom (GitHub) | DICOM reader used in `scoring.py`; cite with version |
| **1** | Li et al. (2016) — see Cluster C | dcm2niix version pinned in Phase 3 |

---

## Cluster L — Clinical / domain context (if CIDUR is TBI-related)

**Manuscript section:** Introduction (cohort context), Methods (cohort description)

| Tier | Reference | Why it matters |
|------|-----------|----------------|
| **2** | TRACK-TBI Network | Multisite TBI imaging protocols with standardized 3T MRI; cite only if CIDUR is a TBI-related cohort |

**Note:** Add 1–3 domain-specific papers from your clinical collaborators that describe the CIDUR cohort's disease context. These are team-specific and cannot be web-searched generically.

---

## Quick-reference: minimum viable citation set (Tier 1 only)

For a lean first draft, cite at minimum these **10 papers**:

1. Bidgood & Horii (1997) — DICOM standard
2. Gorgolewski et al. (2016) — BIDS
3. Wilkinson et al. (2016) — FAIR
4. Li et al. (2016) — dcm2niix
5. Marcus et al. (2007) — XNAT
6. Esteban et al. (2017) — MRIQC (contrast)
7. Fortin et al. (2017) — ComBat harmonization
8. Bastiani et al. (2019) — Diffusion QC
9. Esteban et al. (2019) — fMRIPrep
10. Poldrack et al. (2017) — Reproducibility

Plus **Rorden et al. (2025)** if you emphasize vendor-specific DICOM encoding differences.

---

## Next steps

- [ ] Add 1–3 **domain papers** from collaborators describing the CIDUR cohort
- [ ] Verify DOIs by running `checkcites references.bib` or similar
- [ ] Cross-reference with NeuroImage Guide for Authors for citation style
- [ ] Import into Zotero / Mendeley / EndNote for the writing team
