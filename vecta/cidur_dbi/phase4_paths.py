"""Phase 4 path safety — never write inside the original cohort tree."""

from __future__ import annotations

from pathlib import Path


def _is_under(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def assert_write_outside_cohort(out_path: Path, cohort_roots: list[Path]) -> None:
    """Raise SystemExit if out_path is inside any cohort root (resolved)."""
    out_r = out_path.resolve()
    for root in cohort_roots:
        r = root.resolve()
        if _is_under(out_r, r):
            raise SystemExit(
                f"Refusing to write under cohort data tree:\n  out={out_r}\n  cohort_root={r}\n"
                "Use a directory outside CIDUR_data (e.g. ./outputs_phase4 or /scratch/...)."
            )


def infer_cohort_root_from_scan_path(scan_path: str | Path) -> Path | None:
    """
    Best-effort for .../<cohort>/EPid/EPid/EPid_MR_n/scans/<series>/...
    Returns <cohort> directory (one level above the outer EPid folder).
    """
    p = Path(scan_path).resolve()
    parts = p.parts
    if "scans" not in parts:
        return None
    si = parts.index("scans")
    if si < 4:
        return None
    return Path(*parts[: si - 3])
