#!/usr/bin/env python3
"""
Phase 4 -- Compare human true_role to predicted_series_class (filled manifest).

Reads only the manifest CSV; writes metrics, confusion matrix, and per-class
precision/recall/F1 under --out.  Does not touch CIDUR_data.

Usage:
  python phase4_compare_labels.py \
      --manifest ./outputs_phase4/phase4_labeling_manifest_filled.csv \
      --out ./outputs_phase4
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
    """Unweighted Cohen kappa from aligned label lists (same length)."""
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


def per_class_metrics(
    y_true: list[str], y_pred: list[str], labels: list[str]
) -> list[dict]:
    """Compute precision, recall, F1 per class from aligned label lists."""
    results = []
    for lab in labels:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == lab and p == lab)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != lab and p == lab)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == lab and p != lab)
        support = tp + fn
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )
        results.append(
            {
                "class": lab,
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1": round(f1, 4),
                "support": support,
                "tp": tp,
                "fp": fp,
                "fn": fn,
            }
        )
    return results


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
    pc = per_class_metrics(y_true, y_pred, labels)

    macro_precision = sum(r["precision"] for r in pc) / len(pc) if pc else 0
    macro_recall = sum(r["recall"] for r in pc) / len(pc) if pc else 0
    macro_f1 = sum(r["f1"] for r in pc) / len(pc) if pc else 0

    out.mkdir(parents=True, exist_ok=True)

    cm.to_csv(out / "phase4_confusion_matrix.csv")

    pc_df = pd.DataFrame(pc)
    pc_df.to_csv(out / "phase4_per_class_metrics.csv", index=False)

    mismatches = work[work["true_role"] != work["predicted_series_class"]]
    if not mismatches.empty:
        mis_cols = [
            "sample_id", "scan_folder", "series_description",
            "predicted_series_class", "true_role", "notes",
        ]
        mis_cols = [c for c in mis_cols if c in mismatches.columns]
        mismatches[mis_cols].to_csv(out / "phase4_misclassifications.csv", index=False)

    metrics = {
        "phase": "4_human_label_validation",
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "n_labeled": len(work),
        "n_correct": correct,
        "n_misclassified": len(work) - correct,
        "accuracy": round(acc, 4),
        "cohen_kappa_unweighted": round(kappa, 4),
        "macro_precision": round(macro_precision, 4),
        "macro_recall": round(macro_recall, 4),
        "macro_f1": round(macro_f1, 4),
        "per_class": pc,
        "labels": labels,
        "manifest": str(args.manifest.resolve()),
    }
    with open(out / "phase4_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    lines = [
        "=" * 60,
        "Phase 4 -- Heuristic Classification Validation",
        "=" * 60,
        "",
        f"  n_labeled           = {len(work)}",
        f"  accuracy            = {acc:.4f}  ({correct}/{len(work)})",
        f"  Cohen's kappa       = {kappa:.4f}",
        f"  macro precision     = {macro_precision:.4f}",
        f"  macro recall        = {macro_recall:.4f}",
        f"  macro F1            = {macro_f1:.4f}",
        "",
        "-" * 60,
        "Per-class metrics:",
        "-" * 60,
        f"  {'Class':<15} {'Prec':>6} {'Recall':>7} {'F1':>6} {'Support':>8}",
    ]
    for r in pc:
        lines.append(
            f"  {r['class']:<15} {r['precision']:>6.3f} "
            f"{r['recall']:>7.3f} {r['f1']:>6.3f} {r['support']:>8d}"
        )
    lines.extend([
        "",
        "-" * 60,
        "Confusion matrix (rows=true, cols=predicted):",
        "-" * 60,
        str(cm),
    ])
    if not mismatches.empty:
        lines.extend([
            "",
            "-" * 60,
            f"Misclassifications ({len(mismatches)}):",
            "-" * 60,
        ])
        for _, row in mismatches.iterrows():
            sid = row.get("sample_id", "?")
            sf = row.get("scan_folder", "?")
            pred = row.get("predicted_series_class", "?")
            true = row.get("true_role", "?")
            lines.append(f"  {sid}: {sf}  predicted={pred}  true={true}")

    summary_text = "\n".join(lines)
    (out / "phase4_summary.txt").write_text(summary_text, encoding="utf-8")

    print(summary_text)
    print()
    print(f"Wrote {out / 'phase4_confusion_matrix.csv'}")
    print(f"Wrote {out / 'phase4_per_class_metrics.csv'}")
    print(f"Wrote {out / 'phase4_metrics.json'}")
    print(f"Wrote {out / 'phase4_summary.txt'}")
    if not mismatches.empty:
        print(f"Wrote {out / 'phase4_misclassifications.csv'}")


if __name__ == "__main__":
    main()
