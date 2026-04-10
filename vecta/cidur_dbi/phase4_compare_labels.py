#!/usr/bin/env python3
"""
Phase 4 — Compare human true_role to predicted_series_class (filled manifest).

Reads only the manifest CSV; writes metrics and confusion table under --out.
Does not touch CIDUR_data.

Usage:
  python phase4_compare_labels.py --manifest ./outputs_phase4/sample_manifest_filled.csv --out ./outputs_phase4
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

try:
    from .phase4_paths import assert_write_outside_cohort
except ImportError:
    from phase4_paths import assert_write_outside_cohort


def cohen_kappa_multiclass(y_true: list[str], y_pred: list[str]) -> float:
    """Unweighted Cohen's κ from aligned label lists (same length)."""
    labels = sorted(set(y_true) | set(y_pred))
    if not labels:
        return 1.0
    k = len(labels)
    idx = {lab: i for i, lab in enumerate(labels)}
    n = len(y_true)
    if n == 0:
        return 0.0
    cm = [[0] * k for _ in range(k)]
    for t, p in zip(y_true, y_pred):
        cm[idx[t]][idx[p]] += 1
    diag = sum(cm[i][i] for i in range(k))
    p_o = diag / n
    row_m = [sum(cm[i][j] for j in range(k)) / n for i in range(k)]
    col_m = [sum(cm[i][j] for i in range(k)) / n for j in range(k)]
    p_e = sum(row_m[i] * col_m[i] for i in range(k))
    if abs(1.0 - p_e) < 1e-12:
        return 0.0
    return (p_o - p_e) / (1.0 - p_e)


def main() -> None:
    ap = argparse.ArgumentParser(description="Phase 4 label vs prediction metrics")
    ap.add_argument("--manifest", type=Path, required=True, help="CSV with true_role filled")
    ap.add_argument("--out", type=Path, default=None, help="Default: manifest parent")
    ap.add_argument(
        "--cohort-root",
        type=Path,
        default=None,
        help="If set, --out must not be inside this tree",
    )
    args = ap.parse_args()

    out = args.out if args.out else args.manifest.parent
    roots = [args.cohort_root] if args.cohort_root is not None else []
    assert_write_outside_cohort(out, [r for r in roots if r is not None])

    df = pd.read_csv(args.manifest)
    for col in ("predicted_series_class", "true_role"):
        if col not in df.columns:
            raise SystemExit(f"Manifest must contain column {col!r}")

    work = df.copy()
    work["true_role"] = work["true_role"].fillna("").astype(str).str.strip()
    work = work[work["true_role"] != ""]
    if work.empty:
        raise SystemExit("No rows with non-empty true_role; fill labels first.")

    y_true = work["true_role"].tolist()
    y_pred = work["predicted_series_class"].fillna("").astype(str).str.strip().tolist()

    labels = sorted(set(y_true) | set(y_pred))
    cm = pd.crosstab(
        pd.Series(y_true, name="true_role"),
        pd.Series(y_pred, name="predicted_series_class"),
    )
    cm = cm.reindex(index=labels, columns=labels, fill_value=0)

    correct = sum(1 for a, b in zip(y_true, y_pred) if a == b)
    acc = correct / len(y_true)
    kappa = cohen_kappa_multiclass(y_true, y_pred)

    out.mkdir(parents=True, exist_ok=True)
    cm.to_csv(out / "phase4_confusion_matrix.csv")

    metrics = {
        "phase": "4_human_labels",
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "n_labeled": len(work),
        "accuracy": round(acc, 4),
        "cohen_kappa_unweighted": round(kappa, 4),
        "labels": labels,
        "manifest": str(args.manifest.resolve()),
    }
    with open(out / "phase4_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    # Plain-text summary for supplement paste
    lines = [
        f"n_labeled={len(work)}",
        f"accuracy={acc:.4f}",
        f"cohen_kappa={kappa:.4f}",
        "",
        str(cm),
    ]
    (out / "phase4_summary.txt").write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {out / 'phase4_confusion_matrix.csv'}")
    print(f"Wrote {out / 'phase4_metrics.json'}")
    print(f"accuracy={acc:.4f} kappa={kappa:.4f}")


if __name__ == "__main__":
    main()
