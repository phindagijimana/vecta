"""
DBI v1 scoring — implements DBI_v1_SPECIFICATION.md with dbi_v1_config.yaml.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pydicom
from pydicom.dataset import Dataset
from pydicom.multival import MultiValue


def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, bytes):
        return v.decode(errors="replace").strip()
    return str(v).strip()


def elem_value(ds: Dataset, tag: tuple[int, int]) -> Any:
    """Raw .value for a tag, or empty string if missing."""
    e = ds.get(tag)
    if e is None:
        return ""
    return e.value if hasattr(e, "value") else e


def series_description(ds: Dataset) -> str:
    return _s(elem_value(ds, (0x0008, 0x103E)))


def _f(v: Any) -> float | None:
    try:
        if v is None or v == "":
            return None
        return float(v)
    except (TypeError, ValueError):
        return None


def load_yaml_config(path: Path) -> dict:
    import yaml

    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def standards_classify(
    sd: str, class_sd_compliance: dict[str, dict]
) -> str:
    """
    Strict classification using only the class_sd_compliance rules.
    ALL regexes for a class must match the SeriesDescription for it to be
    assigned.  Returns the class name or 'unclassifiable'.
    Order: iterate classes alphabetically; first full match wins.
    """
    text = sd.strip()
    if not text:
        return "unclassifiable"
    for cls in sorted(class_sd_compliance.keys()):
        rule = class_sd_compliance[cls]
        all_match = rule.get("all_match") or []
        if not all_match:
            continue
        ok = True
        for pat in all_match:
            try:
                if not re.search(pat, text, re.DOTALL):
                    ok = False
                    break
            except re.error:
                ok = False
                break
        if ok:
            return cls
    return "unclassifiable"


_RULE_DESCRIPTIONS: dict[str, list[str]] = {
    "dwi": ["contains DTI/DWI keyword", "has AP + direction count (e.g. AP_64_DIRECTIONS)"],
    "bold": ["contains fMRI/BOLD/RESTING/TASK/EPI keyword"],
    "asl": ["contains ASL keyword"],
    "fmap": ["contains field_map/fmap/gre_field keyword", "has PA + direction count"],
    "swi": ["contains SWI/SWAN keyword"],
    "flair": ["ends with FLAIR"],
    "perf": ["contains perf/DSC/DCE/CBF keyword"],
    "t1_anat": ["ends with MPRAGE/SPGR/FSPGR/BRAVO"],
    "t2_anat": ["contains T2/BLADE keyword", "ends with THIN"],
    "localizer": ["contains localizer/LOC/scout keyword"],
}


def standards_gap_reason(
    sd: str,
    heuristic_class: str,
    class_sd_compliance: dict[str, dict],
) -> str:
    """
    Explain why standards_classify did not match heuristic_class.
    Returns a human-readable reason string.
    """
    text = sd.strip()
    if not text:
        return "SeriesDescription is empty"
    if heuristic_class == "other":
        return "Classified as 'other' (no modality keyword found)"
    if heuristic_class not in class_sd_compliance:
        return f"No standards rule defined for class '{heuristic_class}'"

    rule = class_sd_compliance[heuristic_class]
    all_match = rule.get("all_match") or []
    descriptions = _RULE_DESCRIPTIONS.get(heuristic_class, [])

    failed = []
    for i, pat in enumerate(all_match):
        try:
            if not re.search(pat, text, re.DOTALL):
                desc = descriptions[i] if i < len(descriptions) else f"pattern {pat}"
                failed.append(desc)
        except re.error:
            failed.append(f"invalid pattern: {pat}")

    if not failed:
        return "Already compliant"
    return "Missing: " + "; ".join(failed)


_RECOMMENDED_PATTERNS: dict[str, str] = {
    "dwi": "<PLANE>_DTI_AP_<N>_DIRECTIONS",
    "bold": "<PLANE>_fMRI_<TASK>",
    "asl": "<PLANE>_3D_ASL",
    "fmap": "<PLANE>_field_map_PA_<N>_DIRECTIONS",
    "swi": "<PLANE>_SWI",
    "flair": "<PLANE>_3D_T2_FLAIR",
    "perf": "<PLANE>_Perfusion",
    "t1_anat": "<PLANE>_3D_MPRAGE",
    "t2_anat": "<PLANE>_T2_THIN",
    "localizer": "3_Plane_Localizer",
}


def recommended_name_for_class(series_class: str) -> str:
    """Return a recommended naming pattern for the given class."""
    return _RECOMMENDED_PATTERNS.get(series_class, "")


def classify_series(text: str, rules: list[dict]) -> str:
    t = text
    for rule in rules:
        cls = rule["class"]
        patterns = rule.get("patterns") or []
        if cls == "other" and not patterns:
            return "other"
        for pat in patterns:
            if not pat:
                continue
            if any(c in pat for c in r".*+?[]()|^$\\") and not pat.isalnum():
                if re.search(pat, t, re.IGNORECASE):
                    return cls
            else:
                if pat.lower() in t.lower():
                    return cls
    return "other"


def scanner_cluster_from_ds(ds: Dataset) -> str:
    man = _s(elem_value(ds, (0x0008, 0x0070)))
    model = _s(elem_value(ds, (0x0008, 0x1090)))
    b0 = _s(elem_value(ds, (0x0018, 0x0087)))
    return f"{man} | {model} | {b0}T".strip()


def is_derivative_dwi_name(combined: str, tokens: list[str]) -> bool:
    u = combined.upper()
    # Longer tokens first to avoid partial matches
    for tok in sorted(tokens, key=len, reverse=True):
        if not tok:
            continue
        # Token as path segment or delimiter-wrapped
        rx = re.compile(r"(^|[_\s\-])" + re.escape(tok.upper()) + r"($|[_\s\-])")
        if rx.search(u):
            return True
    return False


def has_diffusion_evidence(ds: Dataset) -> tuple[bool, str]:
    """Return (found, reason_code) for b-value / diffusion-related tags."""
    # Standard DiffusionBValue in MR Diffusion macro
    if (0x0018, 0x9087) in ds and _f(ds[0x0018, 0x9087].value) is not None:
        return True, "00189087"
    v = ds.get("DiffusionBValue")
    if v is not None and _f(getattr(v, "value", v)) is not None:
        return True, "DiffusionBValue"
    # ImageType
    it = ds.get((0x0008, 0x0008))
    if it is not None:
        parts = [str(x).upper() for x in getattr(it, "value", it)]
        if any("DIFFUSION" in p or "DIFF" == p for p in parts):
            return True, "ImageType"
    # SequenceName
    sn = _s(elem_value(ds, (0x0018, 0x0024))).upper()
    if "DW" in sn or "DIFF" in sn or "DTI" in sn:
        return True, "SequenceName"
    # Enhanced / multiframe
    if "PerFrameFunctionalGroupsSequence" in ds:
        try:
            pffg = ds.PerFrameFunctionalGroupsSequence
            if pffg and len(pffg) > 0:
                return True, "PerFrameFunctionalGroupsSequence"
        except Exception:
            pass
    if "SharedFunctionalGroupsSequence" in ds:
        return True, "SharedFunctionalGroupsSequence"
    # MRDiffusionSequence in some objects
    if "MRDiffusionSequence" in ds:
        return True, "MRDiffusionSequence"
    return False, ""


def has_gradient_direction_info(ds: Dataset) -> bool:
    if (0x0018, 0x9089) in ds:  # DiffusionGradientOrientation
        return True
    if (0x0018, 0x9075) in ds:  # DiffusionDirectionality etc.
        return True
    if "PerFrameFunctionalGroupsSequence" in ds:
        return True
    return False


def score_M(ds: Dataset, cls: str, spatial_cfg: dict) -> tuple[float, int, int]:
    """Return (score, n_pass, n_total)."""
    checks: list[bool] = []

    def add(cond: bool) -> None:
        checks.append(cond)

    mod = _s(elem_value(ds, (0x0008, 0x0060))).upper()
    add(mod == "MR")
    add(bool(_s(elem_value(ds, (0x0008, 0x0070)))))
    add(bool(_s(elem_value(ds, (0x0008, 0x1090)))))
    b0v = elem_value(ds, (0x0018, 0x0087))
    add(_f(b0v) is not None and _f(b0v) > 0)
    add(bool(_s(elem_value(ds, (0x0020, 0x000E)))))
    add(bool(_s(elem_value(ds, (0x0020, 0x000D)))))

    sd = series_description(ds)
    pn = _s(elem_value(ds, (0x0018, 0x1030)))
    add(bool(sd) or bool(pn))

    if cls == "localizer":
        n_pass = sum(checks)
        n_total = len(checks)
        return (n_pass / n_total if n_total else 0.0, n_pass, n_total)

    # Spatial
    ps = elem_value(ds, (0x0028, 0x0030))
    ips = elem_value(ds, (0x0018, 0x1164))
    in_plane_ok = False
    for val in (ps, ips):
        if val is None or val == "":
            continue
        if isinstance(val, (list, tuple, MultiValue)) and len(val) >= 2:
            a, b = _f(val[0]), _f(val[1])
            if a and b and a > 0 and b > 0:
                lo, hi = spatial_cfg["min_pixel_spacing_mm"], spatial_cfg["max_pixel_spacing_mm"]
                if lo <= a <= hi and lo <= b <= hi:
                    in_plane_ok = True
                    break
    add(in_plane_ok)

    st = _f(elem_value(ds, (0x0018, 0x0050)))
    sbs = _f(elem_value(ds, (0x0018, 0x0088)))
    slo, shi = spatial_cfg["min_slice_thickness_mm"], spatial_cfg["max_slice_thickness_mm"]
    slice_ok = False
    if st is not None and slo <= st <= shi:
        slice_ok = True
    if sbs is not None and slo <= sbs <= shi:
        slice_ok = True
    add(slice_ok)

    if cls == "dwi":
        ok, _ = has_diffusion_evidence(ds)
        add(ok)

    tr = _f(elem_value(ds, (0x0018, 0x0080)))
    te = _f(elem_value(ds, (0x0018, 0x0081)))
    if cls in ("bold", "asl"):
        add(tr is not None and tr > 0)
        add(te is not None and te > 0)

    if cls == "fmap":
        add(te is not None and te > 0)

    n_pass = sum(checks)
    n_total = len(checks)
    return (n_pass / n_total if n_total else 0.0, n_pass, n_total)


def score_P(scan_basename: str, ds: Dataset, protocol_pattern: str) -> tuple[float, float, float]:
    """Return (P_composite, P_minimal, P_ideal)."""
    folder_ok = bool(re.match(r"^[0-9]+-", scan_basename))
    sd = series_description(ds)
    pn = _s(elem_value(ds, (0x0018, 0x1030)))
    text_ok = bool(sd) or bool(pn)
    p_min = (float(folder_ok) + float(text_ok)) / 2.0
    combined = f"{sd} {pn}"
    p_ideal = 1.0 if re.search(protocol_pattern, combined) else 0.0
    p = 0.5 * p_min + 0.5 * p_ideal
    return p, p_min, p_ideal


def score_S(ds: Dataset, cls: str, spatial_cfg: dict) -> float:
    if cls == "localizer":
        return 1.0  # N/A treated as full credit for S per spec option (exclude from strict spatial)

    ps = elem_value(ds, (0x0028, 0x0030))
    ips = elem_value(ds, (0x0018, 0x1164))
    in_plane_ok = False
    for val in (ps, ips):
        if val is None or val == "":
            continue
        if isinstance(val, (list, tuple, MultiValue)) and len(val) >= 2:
            a, b = _f(val[0]), _f(val[1])
            if a and b and a > 0 and b > 0:
                lo, hi = spatial_cfg["min_pixel_spacing_mm"], spatial_cfg["max_pixel_spacing_mm"]
                if lo <= a <= hi and lo <= b <= hi:
                    in_plane_ok = True
                    break

    st = _f(elem_value(ds, (0x0018, 0x0050)))
    sbs = _f(elem_value(ds, (0x0018, 0x0088)))
    slo, shi = spatial_cfg["min_slice_thickness_mm"], spatial_cfg["max_slice_thickness_mm"]
    slice_ok = False
    if st is not None and slo <= st <= shi:
        slice_ok = True
    if sbs is not None and slo <= sbs <= shi:
        slice_ok = True

    if in_plane_ok and slice_ok:
        return 1.0
    if in_plane_ok:
        return 0.5
    return 0.0


def score_N(
    scan_basename: str,
    ds: Dataset,
    folder_regex: str,
    automation_conventions: list[dict] | None = None,
    series_class: str = "other",
    class_sd_compliance: dict[str, dict] | None = None,
    derived_scan_naming: dict | None = None,
) -> tuple[float, int, int]:
    """
    Naming compliance N: legacy folder/safety/length checks plus optional
    AI/automation-oriented conventions (regex on folder + SeriesDescription + ProtocolName
    when that combined text is non-empty), plus optional per-class SeriesDescription rules
    (all regexes in all_match must match trimmed SeriesDescription alone), plus optional
    derived-scan suffix rule when combined text matches configured markers.
    Returns (score, n_pass, n_total).
    """
    parts: list[float] = []
    parts.append(1.0 if re.match(folder_regex, scan_basename) else 0.0)
    parts.append(0.0 if ("/" in scan_basename or "\\" in scan_basename) else 1.0)
    sd = series_description(ds)
    pn = _s(elem_value(ds, (0x0018, 0x1030)))
    parts.append(1.0 if len(sd) <= 128 else 0.5)

    combined = f"{scan_basename} {sd} {pn}".strip()
    if automation_conventions and combined:
        for conv in automation_conventions:
            if not conv.get("enabled", True):
                continue
            pat = conv.get("regex") or conv.get("pattern")
            if not pat:
                continue
            try:
                parts.append(1.0 if re.search(pat, combined, re.DOTALL) else 0.0)
            except re.error:
                parts.append(0.0)

    sd_stripped = sd.strip()
    if class_sd_compliance and series_class in class_sd_compliance:
        rule = class_sd_compliance[series_class]
        all_match = rule.get("all_match") or []
        if all_match:
            if not sd_stripped:
                parts.append(0.0)
            else:
                ok = True
                for pat in all_match:
                    try:
                        if not re.search(pat, sd_stripped, re.DOTALL):
                            ok = False
                            break
                    except re.error:
                        ok = False
                        break
                parts.append(1.0 if ok else 0.0)

    if derived_scan_naming and derived_scan_naming.get("enabled", True) and combined:
        markers = derived_scan_naming.get("markers") or []
        suf_pat = (
            derived_scan_naming.get("series_description_suffix_regex")
            or r"(?i)(reformat|derived)\s*\Z"
        )
        if markers and is_derivative_dwi_name(combined, markers):
            if not sd_stripped:
                parts.append(0.0)
            else:
                try:
                    parts.append(1.0 if re.search(suf_pat, sd_stripped) else 0.0)
                except re.error:
                    parts.append(0.0)

    n_total = len(parts)
    n_pass = int(sum(parts))
    return (sum(parts) / n_total if n_total else 0.0, n_pass, n_total)


def score_G(
    ds: Dataset, cls: str, combined_text: str, derivative_tokens: list[str]
) -> tuple[float | None, bool, bool, bool, bool]:
    """
    Returns (G score or None if NA, na_flag as True means use NA, derivative_series, has_b, has_dir).
    na_flag True means exclude G from composite.
    """
    if cls != "dwi":
        return None, True, False, False, False

    if is_derivative_dwi_name(combined_text.upper(), derivative_tokens):
        return 0.0, False, True, False, False

    has_b, _ = has_diffusion_evidence(ds)
    has_dir = has_gradient_direction_info(ds)
    nf = elem_value(ds, (0x0028, 0x0008))
    n_frames_ok = False
    if nf is not None and nf != "":
        try:
            n = int(nf)
            n_frames_ok = n > 1
        except (TypeError, ValueError):
            pass
    # single-slice 2D still valid DWI if b present
    vol_ok = n_frames_ok or True  # spec: credit if multiframe; do not penalize single-frame

    w1, w2, w3 = 0.45, 0.45, 0.10
    ib = 1.0 if has_b else 0.0
    idir = 1.0 if has_dir else 0.0
    iv = 1.0 if vol_ok else 0.0
    g = w1 * ib + w2 * idir + w3 * iv
    return g, False, False, has_b, has_dir


def composite_dbi(
    scores: dict[str, float | None],
    weights: dict[str, float],
) -> float:
    """Renormalize over non-None scores; drift weight 0 skipped."""
    num = 0.0
    den = 0.0
    for k, w in weights.items():
        if w <= 0:
            continue
        s = scores.get(k)
        if s is None:
            continue
        num += w * s
        den += w
    return num / den if den > 0 else 0.0


@dataclass
class SeriesRow:
    session_path: str
    session_id: str
    scan_folder: str
    scan_path: str
    dicom_path: str
    scanner_cluster: str
    series_class: str
    read_error: str
    M: float
    M_pass: int
    M_total: int
    P: float
    P_minimal: float
    P_ideal: float
    G: str
    G_na: bool
    derivative_series: bool
    S: float
    N: float
    N_pass: int
    N_total: int
    DBI: float
    has_bvalue_evidence: bool
    has_gradient_direction: bool
    standards_compliant_class: str
    naming_compliant: bool
    recommended_name_pattern: str
    standards_gap: str