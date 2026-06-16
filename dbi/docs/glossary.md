# Glossary

Terms used throughout the docs.

**Audit**
:   One invocation of `dbi-audit`. Walks a DICOM tree, scores every MR series,
    writes CSVs / figures.

**BIDS**
:   Brain Imaging Data Structure — the community standard for organising
    neuroimaging data on disk. DBI is **upstream** of BIDS: it scores whether
    a raw DICOM series is clean enough to be safely converted.

**Component**
:   One of `M`, `P`, `G`, `S`, `N`, `D`. Each contributes a value in `[0, 1]`
    or is marked N/A and excluded from the composite.

**Composite (DBI)**
:   The weighted mean of applicable component scores, renormalised so that the
    weights of N/A components are dropped from both numerator and denominator.

**Derived series**
:   A scanner-generated map (ADC, FA, TRACE, mIP, …) detected by token match in
    the combined folder / SeriesDescription / ProtocolName text. Derived DWI
    series score `G = 0` and trigger the derived-scan suffix N check.

**dcm2niix**
:   The de-facto DICOM → NIfTI converter. `dbi-convert` invokes it per scan
    folder and records `convert_pass = (exit_code == 0) AND (n_nifti >= 1)`.

**N/A (Not Applicable)**
:   A component returns N/A when its check is meaningless for the series
    (e.g. gradient integrity on a T1w). N/A components are excluded from both
    numerator and denominator in the composite.

**P_minimal / P_ideal**
:   The two halves of the protocol-naming score. P_minimal credits *any*
    reasonable folder + descriptive text; P_ideal credits a match against the
    prospective `protocol_token.pattern` regex.

**Scanner cluster**
:   The covariate `Manufacturer | Model | <B0>T`, reported alongside DBI but
    not part of the composite.

**Series**
:   The unit of DBI scoring. In `xnat` layout, one `scans/<name>` folder; in
    `uid-tree` layout, one `(StudyInstanceUID, SeriesInstanceUID)` pair.

**Series class**
:   The label assigned by the heuristic classifier: `dwi`, `bold`, `asl`,
    `fmap`, `swi`, `flair`, `perf`, `t1_anat`, `t2_anat`, `localizer`, `other`.

**Session**
:   One imaging visit. In `xnat` layout, one `*_MR_*` directory; in `uid-tree`,
    one `StudyInstanceUID`.

**Standards classifier**
:   A second, strict classifier driven by
    `naming.class_series_description_compliance`. Emitted as
    `standards_compliant_class` for cross-checking against the heuristic class.

**XNAT layout**
:   The CIDUR-style export tree
    `EP*/EP*/*_MR_*/scans/<name>/resources/DICOM/files/*.dcm`. The default layout
    expected by `dbi-audit` and `dbi-convert`.
