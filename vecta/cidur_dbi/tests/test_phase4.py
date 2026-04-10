"""Tests for Phase 4 metadata / safety helpers."""

from pathlib import Path

import pandas as pd
import pytest

try:
    from cidur_dbi.phase4_build_sample_manifest import stratified_sample, _scored_rows
    from cidur_dbi.phase4_compare_labels import cohen_kappa_multiclass
    from cidur_dbi.phase4_paths import assert_write_outside_cohort, infer_cohort_root_from_scan_path
except ImportError:
    from phase4_build_sample_manifest import stratified_sample, _scored_rows
    from phase4_compare_labels import cohen_kappa_multiclass
    from phase4_paths import assert_write_outside_cohort, infer_cohort_root_from_scan_path


def test_infer_cohort_root():
    p = "/data/CIDUR_data/EP1/EP1/EP1_MR_1/scans/10-T1/foo"
    assert infer_cohort_root_from_scan_path(p) == Path("/data/CIDUR_data")


def test_refuse_write_inside_cohort(tmp_path: Path):
    cohort = tmp_path / "CIDUR_data"
    cohort.mkdir()
    bad_out = cohort / "metadata_out"
    with pytest.raises(SystemExit):
        assert_write_outside_cohort(bad_out, [cohort])


def test_allow_write_outside(tmp_path: Path):
    cohort = tmp_path / "CIDUR_data"
    cohort.mkdir()
    good = tmp_path / "phase4_meta"
    assert_write_outside_cohort(good, [cohort])


def test_kappa_perfect():
    assert cohen_kappa_multiclass(["a", "b", "c"], ["a", "b", "c"]) == pytest.approx(1.0)


def test_scored_rows_filters_read_error():
    df = pd.DataFrame(
        {
            "read_error": ["", "bad", ""],
            "scan_path": ["a", "b", "c"],
        }
    )
    s = _scored_rows(df)
    assert len(s) == 2


def test_stratified_sample_respects_n():
    df = pd.DataFrame(
        {
            "scanner_cluster": ["A"] * 10 + ["B"] * 10,
            "scan_path": [f"/p/{i}" for i in range(20)],
            "session_id": ["s"] * 20,
            "scan_folder": [f"f{i}" for i in range(20)],
            "read_error": [""] * 20,
        }
    )
    out = stratified_sample(df, n=8, key="scanner_cluster", seed=0)
    assert len(out) == 8
    assert out["scan_path"].nunique() == 8
