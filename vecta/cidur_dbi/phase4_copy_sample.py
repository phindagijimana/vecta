#!/usr/bin/env python3
"""
Phase 4 — Optional copy of sampled series to a staging directory (originals unchanged).

Copies **from** paths listed in the manifest; never modifies or deletes source files.
Destination must not be inside --cohort-root.

Modes:
  minimal — first N .dcm files per series into a flat mirror of relative names (small disk).
  full    — full scan folder tree via copytree (large).

Usage:
  python phase4_copy_sample.py --manifest ./outputs_phase4/sample_manifest.csv \\
      --dest /scratch/my_phase4_copies --cohort-root /path/to/CIDUR_data --mode minimal
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

try:
    from .phase4_paths import assert_write_outside_cohort
except ImportError:
    from phase4_paths import assert_write_outside_cohort


def copy_minimal_series(scan_path: Path, dest_series: Path, max_files: int) -> dict:
    dicom_dir = scan_path / "resources" / "DICOM" / "files"
    dest_series.mkdir(parents=True, exist_ok=True)
    if not dicom_dir.is_dir():
        return {"status": "skip_no_dicom_dir", "n_copied": 0}
    dcms = sorted(dicom_dir.glob("*.dcm"))[:max_files]
    n = 0
    for src in dcms:
        shutil.copy2(src, dest_series / src.name)
        n += 1
    return {"status": "ok", "n_copied": n}


def copy_full_series(scan_path: Path, dest_series: Path) -> dict:
    if not scan_path.is_dir():
        return {"status": "skip_missing", "n_copied": 0}
    if dest_series.exists():
        shutil.rmtree(dest_series)
    shutil.copytree(scan_path, dest_series, dirs_exist_ok=False)
    return {"status": "ok", "n_copied": -1}


def main() -> None:
    ap = argparse.ArgumentParser(description="Phase 4 optional copy to staging (read-only source)")
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--dest", type=Path, required=True)
    ap.add_argument("--cohort-root", type=Path, required=True)
    ap.add_argument("--mode", choices=("minimal", "full"), default="minimal")
    ap.add_argument("--max-dicom", type=int, default=5, help="minimal mode: max .dcm per series")
    args = ap.parse_args()

    assert_write_outside_cohort(args.dest, [args.cohort_root])

    df = pd.read_csv(args.manifest)
    if "scan_path" not in df.columns:
        raise SystemExit("manifest missing scan_path")

    args.dest.mkdir(parents=True, exist_ok=True)
    log_rows: list[dict] = []

    for _, row in df.iterrows():
        scan_path = Path(str(row["scan_path"])).resolve()
        sid = str(row.get("sample_id", ""))
        session_id = str(row.get("session_id", "unknown"))
        scan_folder = str(row.get("scan_folder", "scan"))
        dest_series = args.dest / session_id / scan_folder

        if args.mode == "minimal":
            info = copy_minimal_series(scan_path, dest_series, args.max_dicom)
        else:
            info = copy_full_series(scan_path, dest_series)

        log_rows.append(
            {
                "sample_id": sid,
                "source_scan_path": str(scan_path),
                "dest_path": str(dest_series),
                **info,
            }
        )

    log_path = args.dest / "copy_log.json"
    payload = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "cohort_root": str(args.cohort_root.resolve()),
        "dest": str(args.dest.resolve()),
        "note": "Source files were not modified; this is a read+copy operation.",
        "entries": log_rows,
    }
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"Wrote {log_path}")
    print(f"Copied under {args.dest.resolve()}")


if __name__ == "__main__":
    main()
