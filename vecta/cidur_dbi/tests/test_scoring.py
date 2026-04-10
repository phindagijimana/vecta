"""Unit tests for DBI v1 scoring helpers."""

from pathlib import Path

import pydicom
from pydicom.dataset import Dataset, FileMetaDataset

try:
    from cidur_dbi.scoring import composite_dbi, elem_value, score_N, series_description
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from scoring import composite_dbi, elem_value, score_N, series_description

DEFAULT_DERIVED = {
    "enabled": True,
    "markers": ["ADC", "FA"],
    "series_description_suffix_regex": r"(?i)(reformat|derived)\s*\Z",
}


def _minimal_mr_ds(**kwargs) -> Dataset:
    ds = Dataset()
    ds.file_meta = FileMetaDataset()
    ds.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
    for k, v in kwargs.items():
        setattr(ds, k, v)
    return ds


def test_composite_renormalizes_when_g_na():
    w = {
        "metadata_completeness": 0.28,
        "protocol_naming": 0.18,
        "gradient_integrity": 0.22,
        "spatial_consistency": 0.17,
        "naming_compliance": 0.15,
        "drift_control": 0.0,
    }
    scores = {
        "metadata_completeness": 1.0,
        "protocol_naming": 1.0,
        "gradient_integrity": None,
        "spatial_consistency": 1.0,
        "naming_compliance": 1.0,
    }
    # Only M,P,S,N apply: weights 0.28+0.18+0.17+0.15 = 0.78 → all 1 → 1.0
    assert abs(composite_dbi(scores, w) - 1.0) < 1e-9


def test_series_description_empty():
    ds = Dataset()
    assert series_description(ds) == ""


def test_elem_value_missing():
    ds = Dataset()
    assert elem_value(ds, (0x0010, 0x0010)) == ""


def test_score_N_legacy_only_when_no_automation_config():
    ds = _minimal_mr_ds(SeriesDescription="AX T1")
    s, p, t = score_N("6-test_series", ds, r"^[0-9]+-")
    assert t == 3
    assert 0.0 <= s <= 1.0


def test_score_N_includes_automation_when_text_present():
    ds = _minimal_mr_ds(SeriesDescription="AX FLAIR sequence")
    conv = [{"id": "lex", "regex": r"(?i)FLAIR", "enabled": True}]
    s, p, t = score_N("6-AX_FLAIR", ds, r"^[0-9]+-", conv)
    assert t == 4  # 3 legacy + 1 automation
    assert p >= 3  # folder, sep, length, likely FLAIR match


def test_score_N_class_series_description_dwi():
    ds = _minimal_mr_ds(SeriesDescription="AX_DTI_AP_64_DIRECTIONS")
    comp = {
        "dwi": {
            "all_match": [
                r"(?i)(DTI|DWI|dwi|dti)",
                r"(?i)AP[_\s-]*\d+.*(DIRECTION|DIR|direction)s?",
            ]
        }
    }
    s, p, t = score_N("20-AX_DTI", ds, r"^[0-9]+-", None, "dwi", comp)
    assert t == 4  # 3 legacy + class SD
    assert p == 4

    ds2 = _minimal_mr_ds(SeriesDescription="AX_DTI_only")
    s2, p2, t2 = score_N("20-AX_DTI", ds2, r"^[0-9]+-", None, "dwi", comp)
    assert t2 == 4
    assert p2 == 3  # class SD fails (no AP/directions)


def test_score_N_derived_scan_requires_suffix():
    ds_ok = _minimal_mr_ds(SeriesDescription="MY_ADC_MAP_reformat")
    s, p, t = score_N(
        "20-SCOUT",
        ds_ok,
        r"^[0-9]+-",
        None,
        "other",
        None,
        DEFAULT_DERIVED,
    )
    assert t == 4  # legacy 3 + derived check
    assert p == 4

    ds_bad = _minimal_mr_ds(SeriesDescription="MY_ADC_MAP_final")
    s2, p2, t2 = score_N(
        "20-SCOUT",
        ds_bad,
        r"^[0-9]+-",
        None,
        "other",
        None,
        DEFAULT_DERIVED,
    )
    assert t2 == 4
    assert p2 == 3  # derivative marker hit, suffix missing


def test_score_N_t2_anat_compliance():
    comp = {
        "t2_anat": {
            "all_match": [
                r"(?i)(T2|BLADE)",
                r"(?i)THIN\s*\Z",
            ]
        }
    }
    ds = _minimal_mr_ds(SeriesDescription="COR_T2_THIN")
    s, p, t = score_N("14-COR_T2", ds, r"^[0-9]+-", None, "t2_anat", comp, None)
    assert p == t


if __name__ == "__main__":
    test_composite_renormalizes_when_g_na()
    test_series_description_empty()
    test_elem_value_missing()
    print("test_scoring: ok")
