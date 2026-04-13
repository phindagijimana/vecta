#!/usr/bin/env python3
"""
Phase 3 — dcm2niix batch proof on CIDUR-style XNAT exports.

Runs dcm2niix per scan folder (DICOM in resources/DICOM/files), logs outcomes,
and writes Table 2 / optional Figure 2 (pass rate by scanner × series class).

Usage:
  python run_dcm2niix_batch.py --root /path/to/CIDUR_data --out ./outputs_dcm2niix \\
      --nifti-root /path/to/nifti_output

Rubric (v1 default): convert_pass = (exit_code == 0) and (≥1 NIfTI in output dir).

Use --backfill-from-nifti to rebuild conversion_log.csv and Table 2 / Figure 2 from an existing
NIfTI tree without re-running dcm2niix (e.g. after a long batch where only nifti/ was kept).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pydicom

try:
    from .run_audit import find_mr_roots, first_dicom, session_scanner_cluster
    from .scoring import classify_series, load_yaml_config, scanner_cluster_from_ds, series_description
except ImportError:
    from run_audit import find_mr_roots, first_dicom, session_scanner_cluster
    from scoring import classify_series, load_yaml_config, scanner_cluster_from_ds, series_description

TEXT_CAPTURE_LIMIT = 8000


def get_dcm2niix_version(exe: str) -> str:
    r = subprocess.run(
        [exe, "-v"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    blob = (r.stdout or "") + "\n" + (r.stderr or "")
    m = re.search(r"(v1\.[0-9.]+)", blob, re.I)
    if m:
        return m.group(1).strip()
    line = next((ln.strip() for ln in blob.splitlines() if ln.strip()), "")
    return line or "unknown"


def dicom_dir_for_scan(scan_path: Path) -> Path:
    return scan_path / "resources" / "DICOM" / "files"


def count_niftis(out_dir: Path) -> tuple[int, str]:
    if not out_dir.exists():
        return 0, ""
    paths = [
        p
        for p in out_dir.rglob("*")
        if p.is_file() and (p.name.endswith(".nii.gz") or p.name.endswith(".nii"))
    ]
    paths = sorted(set(paths))
    names = [p.name for p in paths]
    sample = ";".join(names[:50]) + (";..." if len(names) > 50 else "")
    return len(paths), sample


def rubric_pass(exit_code: int, n_nifti: int) -> bool:
    return exit_code == 0 and n_nifti >= 1


def run_dcm2niix_one(
    exe: str,
    dicom_in: Path,
    out_dir: Path,
    timeout: int | None,
) -> tuple[int, str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [exe, "-z", "y", "-f", "%n_%s", "-o", str(out_dir), str(dicom_in)]
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return r.returncode, (r.stdout or "")[-TEXT_CAPTURE_LIMIT:], (r.stderr or "")[-TEXT_CAPTURE_LIMIT:]
    except subprocess.TimeoutExpired:
        return 124, "", "TIMEOUT"
    except Exception as e:
        return 125, "", repr(e)


def series_class_for_scan(scan_path: Path, rules: list) -> str:
    dcm = first_dicom(scan_path)
    if not dcm:
        return ""
    try:
        ds = pydicom.dcmread(str(dcm), stop_before_pixels=True, force=True)
    except Exception:
        return ""
    sd = series_description(ds)
    combined = f"{scan_path.name} {sd}"
    return classify_series(combined, rules)


def scanner_for_series(scan_path: Path, session_fallback: str) -> str:
    dcm = first_dicom(scan_path)
    if not dcm:
        return session_fallback
    try:
        ds = pydicom.dcmread(str(dcm), stop_before_pixels=True, force=True)
        return scanner_cluster_from_ds(ds)
    except Exception:
        return session_fallback


def build_rows(
    root: Path,
    nifti_root: Path,
    config_path: Path,
    exe: str,
    dry_run: bool,
    timeout: int | None,
    limit: int | None,
) -> list[dict]:
    cfg = load_yaml_config(config_path)
    rules = cfg["classification_rules"]
    version = get_dcm2niix_version(exe) if not dry_run else "dry_run"
    run_utc = datetime.now(timezone.utc).isoformat()
    rows: list[dict] = []
    n_done = 0

    for mr_root in find_mr_roots(root):
        session_id = mr_root.name
        sess_cluster = session_scanner_cluster(mr_root)
        scans = sorted(mr_root.glob("scans/*"))
        for s in scans:
            scan_path = Path(s)
            if not scan_path.is_dir():
                continue
            scan_name = scan_path.name
            d_in = dicom_dir_for_scan(scan_path)
            out_sub = nifti_root / session_id / scan_name
            cls = series_class_for_scan(scan_path, rules)
            cluster = scanner_for_series(scan_path, sess_cluster)

            if not d_in.is_dir() or not list(d_in.glob("*.dcm")):
                rows.append(
                    {
                        "run_utc": run_utc,
                        "dcm2niix_version": version,
                        "session_id": session_id,
                        "scan_folder": scan_name,
                        "scan_path": str(scan_path),
                        "dicom_input_dir": str(d_in),
                        "scanner_cluster": cluster,
                        "series_class": cls or "unknown",
                        "status": "skip_no_dicom",
                        "exit_code": "",
                        "duration_sec": "",
                        "stdout_tail": "",
                        "stderr_tail": "",
                        "n_nifti": 0,
                        "nifti_sample": "",
                        "convert_pass": False,
                        "rubric_note": "no DICOM in resources/DICOM/files",
                        "cmd": "",
                    }
                )
                n_done += 1
                if limit is not None and n_done >= limit:
                    return rows
                continue

            cmd = f"{exe} -z y -f '%n_%s' -o {out_sub} {d_in}"
            if dry_run:
                rows.append(
                    {
                        "run_utc": run_utc,
                        "dcm2niix_version": version,
                        "session_id": session_id,
                        "scan_folder": scan_name,
                        "scan_path": str(scan_path),
                        "dicom_input_dir": str(d_in),
                        "scanner_cluster": cluster,
                        "series_class": cls or "other",
                        "status": "dry_run",
                        "exit_code": "",
                        "duration_sec": "",
                        "stdout_tail": "",
                        "stderr_tail": "",
                        "n_nifti": "",
                        "nifti_sample": "",
                        "convert_pass": "",
                        "rubric_note": "",
                        "cmd": cmd,
                    }
                )
                n_done += 1
                if limit is not None and n_done >= limit:
                    return rows
                continue

            t0 = datetime.now(timezone.utc)
            code, out_t, err_t = run_dcm2niix_one(exe, d_in, out_sub, timeout)
            dt = (datetime.now(timezone.utc) - t0).total_seconds()
            n_ni, sample = count_niftis(out_sub)
            passed = rubric_pass(code, n_ni)
            rows.append(
                {
                    "run_utc": run_utc,
                    "dcm2niix_version": version,
                    "session_id": session_id,
                    "scan_folder": scan_name,
                    "scan_path": str(scan_path),
                    "dicom_input_dir": str(d_in),
                    "scanner_cluster": cluster,
                    "series_class": cls or "other",
                    "status": "ran",
                    "exit_code": code,
                    "duration_sec": round(dt, 3),
                    "stdout_tail": out_t,
                    "stderr_tail": err_t,
                    "n_nifti": n_ni,
                    "nifti_sample": sample,
                    "convert_pass": passed,
                    "rubric_note": "exit==0 and n_nifti>=1",
                    "cmd": cmd,
                }
            )
            n_done += 1
            if limit is not None and n_done >= limit:
                return rows

    return rows


def build_rows_backfill(
    root: Path,
    nifti_root: Path,
    config_path: Path,
    exe: str,
) -> list[dict]:
    """
    Rebuild conversion_log-style rows from an existing NIfTI tree (no dcm2niix run).
    Use when conversion already finished but logs/table2/figure2 were lost or never written.
    Per series with DICOM: exit_code=0 and convert_pass=True iff rubric (≥1 NIfTI) holds; else exit_code=1.
    """
    cfg = load_yaml_config(config_path)
    rules = cfg["classification_rules"]
    version = get_dcm2niix_version(exe) if shutil.which(exe) else "unknown"
    run_utc = datetime.now(timezone.utc).isoformat()
    rows: list[dict] = []

    for mr_root in find_mr_roots(root):
        session_id = mr_root.name
        sess_cluster = session_scanner_cluster(mr_root)
        scans = sorted(mr_root.glob("scans/*"))
        for s in scans:
            scan_path = Path(s)
            if not scan_path.is_dir():
                continue
            scan_name = scan_path.name
            d_in = dicom_dir_for_scan(scan_path)
            out_sub = nifti_root / session_id / scan_name
            cls = series_class_for_scan(scan_path, rules)
            cluster = scanner_for_series(scan_path, sess_cluster)

            if not d_in.is_dir() or not list(d_in.glob("*.dcm")):
                rows.append(
                    {
                        "run_utc": run_utc,
                        "dcm2niix_version": version,
                        "session_id": session_id,
                        "scan_folder": scan_name,
                        "scan_path": str(scan_path),
                        "dicom_input_dir": str(d_in),
                        "scanner_cluster": cluster,
                        "series_class": cls or "unknown",
                        "status": "skip_no_dicom",
                        "exit_code": "",
                        "duration_sec": "",
                        "stdout_tail": "",
                        "stderr_tail": "",
                        "n_nifti": 0,
                        "nifti_sample": "",
                        "convert_pass": False,
                        "rubric_note": "no DICOM in resources/DICOM/files",
                        "cmd": "",
                    }
                )
                continue

            n_ni, sample = count_niftis(out_sub)
            code = 0 if rubric_pass(0, n_ni) else 1
            passed = rubric_pass(code, n_ni)
            rows.append(
                {
                    "run_utc": run_utc,
                    "dcm2niix_version": version,
                    "session_id": session_id,
                    "scan_folder": scan_name,
                    "scan_path": str(scan_path),
                    "dicom_input_dir": str(d_in),
                    "scanner_cluster": cluster,
                    "series_class": cls or "other",
                    "status": "backfill_from_nifti",
                    "exit_code": code,
                    "duration_sec": "",
                    "stdout_tail": "",
                    "stderr_tail": "BACKFILL_FROM_NIFTI: pass/fail inferred from files under nifti_root; not a live run",
                    "n_nifti": n_ni,
                    "nifti_sample": sample,
                    "convert_pass": passed,
                    "rubric_note": "backfill_from_nifti: exit inferred; pass = (code==0 and n_nifti>=1)",
                    "cmd": f"[backfill] would be: {exe} -z y -f '%n_%s' -o {out_sub} {d_in}",
                }
            )

    return rows


def _rows_for_table2(df: pd.DataFrame) -> pd.DataFrame:
    """Live runs plus backfill-from-disk rows; exclude dry_run and skip_no_dicom."""
    return df[df["status"].isin(("ran", "backfill_from_nifti"))].copy()


def write_table2_figure2(df: pd.DataFrame, out_dir: Path) -> None:
    ran = _rows_for_table2(df)
    if ran.empty:
        return
    ran["convert_pass"] = ran["convert_pass"].astype(bool)

    # Cell: scanner × class → pass rate & counts
    g = (
        ran.groupby(["scanner_cluster", "series_class"], dropna=False)
        .agg(n=("convert_pass", "size"), n_pass=("convert_pass", "sum"))
        .reset_index()
    )
    g["pass_rate"] = (g["n_pass"] / g["n"]).round(4)
    g.to_csv(out_dir / "table2_conversion_by_scanner_class.csv", index=False)

    # Scanner marginal
    sg = ran.groupby("scanner_cluster", dropna=False).agg(n=("convert_pass", "size"), n_pass=("convert_pass", "sum")).reset_index()
    sg["pass_rate"] = (sg["n_pass"] / sg["n"]).round(4)
    sg.to_csv(out_dir / "table2_conversion_by_scanner.csv", index=False)

    try:
        import matplotlib.pyplot as plt
        import numpy as np

        pivot = ran.pivot_table(
            index="scanner_cluster",
            columns="series_class",
            values="convert_pass",
            aggfunc="mean",
        )
        fig, ax = plt.subplots(figsize=(max(10, pivot.shape[1] * 0.4), max(4, pivot.shape[0] * 0.35)))
        im = ax.imshow(pivot.values.astype(float), aspect="auto", vmin=0, vmax=1, cmap="RdYlGn")
        ax.set_xticks(range(pivot.shape[1]))
        ax.set_xticklabels(pivot.columns, rotation=35, ha="right")
        ax.set_yticks(range(pivot.shape[0]))
        ax.set_yticklabels([c[:48] + "…" if len(str(c)) > 48 else c for c in pivot.index])
        ax.set_title("Figure 2 — dcm2niix pass rate (mean) by scanner × series class")
        fig.colorbar(im, ax=ax, label="pass rate")
        plt.tight_layout()
        fig.savefig(out_dir / "figure2_dcm2niix_pass_rate_heatmap.png", dpi=150)
        plt.close()
    except ImportError:
        pass


def main() -> None:
    ap = argparse.ArgumentParser(description="Phase 3 dcm2niix batch proof")
    ap.add_argument(
        "--root",
        type=Path,
        default=Path("/mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/Documents/CIDUR_data"),
    )
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "outputs_dcm2niix")
    ap.add_argument(
        "--nifti-root",
        type=Path,
        default=None,
        help="Directory for NIfTI outputs (default: <out>/nifti)",
    )
    ap.add_argument("--config", type=Path, default=Path(__file__).resolve().parent / "dbi_v1_config.yaml")
    ap.add_argument("--dcm2niix", type=str, default="dcm2niix", help="dcm2niix executable name or path")
    ap.add_argument("--dry-run", action="store_true", help="List work only; do not invoke dcm2niix")
    ap.add_argument("--timeout", type=int, default=7200, help="Per-series timeout seconds (0 = no limit)")
    ap.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Stop after N scan folders (for testing)",
    )
    ap.add_argument(
        "--backfill-from-nifti",
        action="store_true",
        help="Rebuild conversion_log + Table 2 + Figure 2 from existing NIfTI under --nifti-root (no dcm2niix)",
    )
    args = ap.parse_args()

    exe = args.dcm2niix
    if args.backfill_from_nifti and args.dry_run:
        print("ERROR: --backfill-from-nifti cannot be used with --dry-run", file=sys.stderr)
        sys.exit(1)
    if not args.backfill_from_nifti and not args.dry_run and not shutil.which(exe):
        print(f"ERROR: dcm2niix not found in PATH: {exe!r}", file=sys.stderr)
        sys.exit(1)

    nifti_root = args.nifti_root if args.nifti_root else args.out / "nifti"
    args.out.mkdir(parents=True, exist_ok=True)

    timeout = None if args.timeout == 0 else args.timeout

    if args.backfill_from_nifti:
        rows = build_rows_backfill(
            args.root.resolve(),
            nifti_root.resolve(),
            args.config,
            exe,
        )
    else:
        rows = build_rows(
            args.root.resolve(),
            nifti_root.resolve(),
            args.config,
            exe,
            args.dry_run,
            timeout,
            args.limit,
        )
    df = pd.DataFrame(rows)
    log_path = args.out / "conversion_log.csv"
    df.to_csv(log_path, index=False)

    rubric = (
        "convert_pass = (exit_code == 0) and (n_nifti >= 1); skip_no_dicom excluded from Table 2"
    )
    if args.backfill_from_nifti:
        rubric += (
            ". Rows with status=backfill_from_nifti: outcomes inferred from files under nifti_root "
            "(exit_code 0 if rubric holds else 1); not a live dcm2niix invocation."
        )

    if args.backfill_from_nifti:
        d2_ver = get_dcm2niix_version(exe) if shutil.which(exe) else "unknown"
    elif args.dry_run:
        d2_ver = "dry_run"
    else:
        d2_ver = get_dcm2niix_version(exe)

    env = {
        "phase": "3_dcm2niix_batch_backfill" if args.backfill_from_nifti else "3_dcm2niix_batch",
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "cohort_root": str(args.root.resolve()),
        "nifti_root": str(nifti_root.resolve()),
        "dcm2niix_exe": exe,
        "dcm2niix_version": d2_ver,
        "cli_pattern": "dcm2niix -z y -f '%n_%s' -o <out_dir> <dicom_dir>",
        "rubric": rubric,
        "n_rows": len(df),
        "dry_run": args.dry_run,
        "backfill_from_nifti": args.backfill_from_nifti,
    }
    with open(args.out / "dcm2niix_environment.json", "w", encoding="utf-8") as f:
        json.dump(env, f, indent=2)

    if args.backfill_from_nifti or not args.dry_run:
        write_table2_figure2(df, args.out)

    print(f"Wrote {log_path} ({len(df)} rows)")
    print(f"Wrote {args.out / 'dcm2niix_environment.json'}")
    if not args.dry_run and not args.backfill_from_nifti:
        print(f"NIfTI under {nifti_root.resolve()}")
    if args.backfill_from_nifti:
        print(f"Backfill used NIfTI under {nifti_root.resolve()}")
    if args.backfill_from_nifti or not args.dry_run:
        for name in ("table2_conversion_by_scanner_class.csv", "figure2_dcm2niix_pass_rate_heatmap.png"):
            p = args.out / name
            if p.exists():
                print(f"Wrote {p}")


if __name__ == "__main__":
    main()
