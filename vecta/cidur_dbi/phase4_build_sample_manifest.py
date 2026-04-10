#!/usr/bin/env python3
"""
Phase 4 — Build a stratified human-label sample manifest from per_series.csv.

Reads audit output only; writes CSV/JSON metadata under --out (must be outside cohort).
Does not read or modify DICOM bytes in CIDUR_data beyond what pandas does to the CSV.

Usage:
  cd cidur_dbi
  python phase4_build_sample_manifest.py --per-series-csv ./outputs/per_series.csv \\
      --cohort-root /path/to/CIDUR_data --out ./outputs_phase4 --n 40
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

try:
    from .phase4_paths import assert_write_outside_cohort, infer_cohort_root_from_scan_path
except ImportError:
    from phase4_paths import assert_write_outside_cohort, infer_cohort_root_from_scan_path


def _scored_rows(df: pd.DataFrame) -> pd.DataFrame:
    re = df["read_error"].fillna("")
    return df.loc[re == ""].copy()


def stratified_sample(df: pd.DataFrame, n: int, key: str, seed: int) -> pd.DataFrame:
    groups = [g for _, g in df.groupby(key, sort=False)]
    if not groups:
        return df.iloc[:0]
    n_groups = len(groups)
    base = max(1, n // n_groups)
    chunks: list[pd.DataFrame] = []
    for i, g in enumerate(groups):
        take = min(len(g), base)
        chunks.append(g.sample(n=take, random_state=seed + 1000 * i))
    cat = pd.concat(chunks)
    cat = cat.drop_duplicates(subset=["scan_path"])
    if len(cat) < n:
        rest = df.loc[~df.index.isin(cat.index)]
        need = n - len(cat)
        if len(rest) > 0:
            extra = rest.sample(n=min(need, len(rest)), random_state=seed + 9999)
            cat = pd.concat([cat, extra]).drop_duplicates(subset=["scan_path"])
    if len(cat) > n:
        cat = cat.sample(n=n, random_state=seed)
    return cat.sort_values([key, "session_id", "scan_folder"])


def main() -> None:
    ap = argparse.ArgumentParser(description="Phase 4 stratified label sample manifest")
    ap.add_argument("--per-series-csv", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=Path("outputs_phase4"))
    ap.add_argument("--n", type=int, default=40, help="Target sample size (after filtering)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument(
        "--cohort-root",
        type=Path,
        default=None,
        help="Cohort root (e.g. CIDUR_data). Output must not lie inside this path.",
    )
    ap.add_argument(
        "--stratify-key",
        type=str,
        default="scanner_cluster",
        help="Column for stratification (default scanner_cluster)",
    )
    args = ap.parse_args()

    df = pd.read_csv(args.per_series_csv)
    if args.stratify_key not in df.columns:
        raise SystemExit(f"Missing column {args.stratify_key!r} in {args.per_series_csv}")

    cohort_root = args.cohort_root
    if cohort_root is None and len(df) > 0 and "scan_path" in df.columns:
        cohort_root = infer_cohort_root_from_scan_path(df["scan_path"].iloc[0])

    roots: list[Path] = []
    if cohort_root is not None:
        roots.append(cohort_root)
    else:
        print(
            "WARNING: --cohort-root not set; output location is not checked against the cohort tree. "
            "Use --cohort-root /path/to/CIDUR_data so we refuse writes inside originals.",
            file=sys.stderr,
        )
    assert_write_outside_cohort(args.out, roots)

    sub = _scored_rows(df)
    if sub.empty:
        raise SystemExit("No rows with empty read_error after load; check per_series.csv")

    sample = stratified_sample(sub, min(args.n, len(sub)), args.stratify_key, args.seed)

    args.out.mkdir(parents=True, exist_ok=True)
    manifest_path = args.out / "sample_manifest.csv"

    out_rows = []
    for i, (_, row) in enumerate(sample.iterrows(), start=1):
        out_rows.append(
            {
                "sample_id": f"P4-{i:03d}",
                "session_id": row.get("session_id", ""),
                "scan_folder": row.get("scan_folder", ""),
                "scan_path": row.get("scan_path", ""),
                "dicom_path": row.get("dicom_path", ""),
                "scanner_cluster": row.get("scanner_cluster", ""),
                "predicted_series_class": row.get("series_class", ""),
                "true_role": "",
                "reviewer": "",
                "review_date": "",
                "notes": "",
            }
        )
    manifest_df = pd.DataFrame(out_rows)
    manifest_df.to_csv(manifest_path, index=False)

    meta = {
        "phase": "4_human_labels",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_per_series_csv": str(args.per_series_csv.resolve()),
        "cohort_root_for_policy": str(cohort_root.resolve()) if cohort_root else None,
        "n_requested": args.n,
        "n_eligible": int(len(sub)),
        "n_selected": int(len(manifest_df)),
        "stratify_key": args.stratify_key,
        "seed": args.seed,
        "data_policy": "Original cohort tree is read-only for this workflow; only metadata CSV/JSON and optional copies to a user-chosen directory are produced.",
        "manifest_csv": str(manifest_path.resolve()),
    }
    with open(args.out / "sample_manifest_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"Wrote {manifest_path} ({len(manifest_df)} rows)")
    print(f"Wrote {args.out / 'sample_manifest_meta.json'}")


if __name__ == "__main__":
    main()
