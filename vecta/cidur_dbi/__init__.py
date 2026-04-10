"""
cidur_dbi — Data Birth Integrity scoring for DICOM series.

Install:  pip install .          (from the vecta/ root)
Audit:    dbi-audit --root /path/to/data --out ./results
Convert:  dbi-convert --root /path/to/data --out ./results_nifti --nifti-root ./nifti
"""

from importlib.metadata import version as _version, PackageNotFoundError

try:
    __version__ = _version("cidur-dbi")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

from .scoring import (
    classify_series,
    composite_dbi,
    load_yaml_config,
    score_G,
    score_M,
    score_N,
    score_P,
    score_S,
    scanner_cluster_from_ds,
    series_description,
    SeriesRow,
)

__all__ = [
    "classify_series",
    "composite_dbi",
    "load_yaml_config",
    "score_G",
    "score_M",
    "score_N",
    "score_P",
    "score_S",
    "scanner_cluster_from_ds",
    "series_description",
    "SeriesRow",
]
