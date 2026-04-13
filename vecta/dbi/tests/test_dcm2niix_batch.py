"""Unit tests for Phase 3 dcm2niix batch helpers."""

from pathlib import Path

import pandas as pd

try:
    from dbi.run_dcm2niix_batch import _rows_for_table2, count_niftis, rubric_pass
except ImportError:
    from run_dcm2niix_batch import _rows_for_table2, count_niftis, rubric_pass


def test_rubric_pass():
    assert rubric_pass(0, 1) is True
    assert rubric_pass(0, 0) is False
    assert rubric_pass(1, 1) is False


def test_count_niftis_empty(tmp_path: Path):
    assert count_niftis(tmp_path / "missing") == (0, "")


def test_rows_for_table2_includes_backfill():
    df = pd.DataFrame(
        {
            "status": ["ran", "skip_no_dicom", "backfill_from_nifti", "dry_run"],
            "convert_pass": [True, False, True, True],
        }
    )
    r = _rows_for_table2(df)
    assert len(r) == 2
    assert set(r["status"].tolist()) == {"ran", "backfill_from_nifti"}


def test_count_niftis_files(tmp_path: Path):
    d = tmp_path / "o"
    d.mkdir()
    (d / "a.nii.gz").write_bytes(b"")
    sub = d / "sub"
    sub.mkdir()
    (sub / "b.nii").write_bytes(b"")
    n, s = count_niftis(d)
    assert n == 2
    assert "a.nii.gz" in s and "b.nii" in s
