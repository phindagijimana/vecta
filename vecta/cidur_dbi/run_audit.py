#!/usr/bin/env python3
"""
CIDUR DBI v1 audit — Phase 2.
Walks MR DICOM trees, scores each series, writes CSVs and optional figures.

Layouts:
  xnat (default) — EP*/EP*/*_MR_*/scans/<name>/resources/DICOM/files/*.dcm
  uid-tree      — any folder tree: group files by (StudyInstanceUID, SeriesInstanceUID);
                  session = study, series = one row per distinct series UID (MR only).

Usage:
  python run_audit.py --root /path/to/CIDUR_data --out ./outputs
  python run_audit.py --layout uid-tree --root /path/to/dicom_root --out ./outputs_uid
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pydicom

try:
    from .scoring import (
        classify_series,
        composite_dbi,
        elem_value,
        load_yaml_config,
        scanner_cluster_from_ds,
        score_G,
        score_M,
        score_N,
        score_P,
        score_S,
        series_description,
    )
except ImportError:
    from scoring import (
        classify_series,
        composite_dbi,
        elem_value,
        load_yaml_config,
        scanner_cluster_from_ds,
        score_G,
        score_M,
        score_N,
        score_P,
        score_S,
        series_description,
    )


def find_mr_roots(root: Path) -> list[Path]:
    pattern = str(root / "EP*" / "EP*" / "*_MR_*")
    paths = [Path(p) for p in glob.glob(pattern) if os.path.isdir(p)]
    return sorted(paths)


def first_dicom(scan_dir: Path) -> Path | None:
    files = sorted(glob.glob(str(scan_dir / "resources" / "DICOM" / "files" / "*.dcm")))
    return Path(files[0]) if files else None


def session_scanner_cluster(mr_root: Path) -> str:
    scans = sorted(glob.glob(str(mr_root / "scans" / "*")))
    for s in scans:
        dcm = first_dicom(Path(s))
        if not dcm:
            continue
        try:
            ds = pydicom.dcmread(str(dcm), stop_before_pixels=True, force=True)
            return scanner_cluster_from_ds(ds)
        except Exception:
            continue
    return "unknown | unknown | unknownT"


def synthetic_scan_label(ds: pydicom.Dataset) -> str:
    """
    Folder basename substitute for uid-tree layout so P_minimal (^[0-9]+-) and N checks apply.
    Uses SeriesNumber + sanitized SeriesDescription.
    """
    sn_raw = elem_value(ds, (0x0020, 0x0011))
    try:
        num = int(str(sn_raw).strip()) if sn_raw != "" and sn_raw is not None else 0
    except (TypeError, ValueError):
        num = 0
    sd = series_description(ds)
    slug = re.sub(r"[^\w\-]+", "_", sd).strip("_")[:80] if sd else "series"
    if num > 0:
        return f"{num}-{slug}"
    return f"0-{slug}"


def _collect_uid_series_files(root: Path) -> dict[tuple[str, str], list[tuple[Path, int]]]:
    """
    Map (StudyInstanceUID, SeriesInstanceUID) -> list of (path, InstanceNumber for sort).
    Only MR files with both UIDs are grouped; others skipped.
    """
    groups: dict[tuple[str, str], list[tuple[Path, int]]] = {}
    for path in sorted(root.rglob("*.dcm")):
        if not path.is_file():
            continue
        try:
            ds = pydicom.dcmread(str(path), stop_before_pixels=True, force=True)
        except Exception:
            continue
        mod = _s_modality(ds)
        if mod != "MR":
            continue
        study = _s_uid(elem_value(ds, (0x0020, 0x000D)))
        ser = _s_uid(elem_value(ds, (0x0020, 0x000E)))
        if not study or not ser:
            continue
        inn = elem_value(ds, (0x0020, 0x0013))
        try:
            inst = int(str(inn).strip()) if inn != "" and inn is not None else 10**9
        except (TypeError, ValueError):
            inst = 10**9
        key = (study, ser)
        groups.setdefault(key, []).append((path, inst))
    for key in groups:
        groups[key].sort(key=lambda t: (t[1], str(t[0])))
    return groups


def _s_modality(ds: pydicom.Dataset) -> str:
    v = elem_value(ds, (0x0008, 0x0060))
    return str(v).strip().upper() if v not in (None, "") else ""


def _s_uid(v) -> str:
    if v is None or v == "":
        return ""
    return str(v).strip()


def _row_from_dataset(
    ds: pydicom.Dataset,
    dcm_path: Path,
    session_path: str,
    session_id: str,
    scan_name: str,
    scan_path: str,
    cluster: str,
    spatial_cfg: dict,
    folder_rx: str,
    proto_pat: str,
    rules: list,
    deriv_toks: list,
    weights: dict[str, float],
    automation_conventions: list[dict] | None = None,
    class_sd_compliance: dict[str, dict] | None = None,
    derived_scan_naming: dict | None = None,
) -> dict:
    sd = series_description(ds)
    combined = f"{scan_name} {sd}"
    cls = classify_series(combined, rules)

    m, mp, mt = score_M(ds, cls, spatial_cfg)
    p, pmin, pideal = score_P(scan_name, ds, proto_pat)
    s_sc = score_S(ds, cls, spatial_cfg)
    n_sc, n_pass_n, n_total_n = score_N(
        scan_name,
        ds,
        folder_rx,
        automation_conventions,
        series_class=cls,
        class_sd_compliance=class_sd_compliance,
        derived_scan_naming=derived_scan_naming,
    )
    g_val, g_na, deriv, has_b, has_dir = score_G(ds, cls, combined.upper(), deriv_toks)

    scores = {
        "metadata_completeness": m,
        "protocol_naming": p,
        "gradient_integrity": None if g_na else g_val,
        "spatial_consistency": s_sc,
        "naming_compliance": n_sc,
    }
    dbi = composite_dbi(scores, weights)

    return {
        "session_path": session_path,
        "session_id": session_id,
        "scan_folder": scan_name,
        "scan_path": scan_path,
        "dicom_path": str(dcm_path),
        "scanner_cluster": cluster,
        "series_class": cls,
        "read_error": "",
        "M": m,
        "M_pass": mp,
        "M_total": mt,
        "P": p,
        "P_minimal": pmin,
        "P_ideal": pideal,
        "G": "" if g_val is None else g_val,
        "G_na": g_na,
        "derivative_series": deriv,
        "S": s_sc,
        "N": n_sc,
        "N_pass": n_pass_n,
        "N_total": n_total_n,
        "DBI": dbi,
        "has_bvalue_evidence": has_b,
        "has_gradient_direction": has_dir,
    }


def run_audit(
    root: Path,
    out_dir: Path,
    config_path: Path,
    failure_log: Path | None = None,
    layout: str = "xnat",
) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    cfg = load_yaml_config(config_path)
    cfg_version = str(cfg.get("version", "unknown"))
    weights = {k: float(v) for k, v in cfg["weights"].items()}
    spatial_cfg = cfg["spatial"]
    naming_cfg = cfg["naming"]
    proto_pat = cfg["protocol_token"]["pattern"]
    rules = cfg["classification_rules"]
    folder_rx = naming_cfg["scan_folder_pattern"]
    deriv_toks = naming_cfg["derivative_tokens"]
    auto_conv = naming_cfg.get("automation_conventions") or []
    class_sd_comp = naming_cfg.get("class_series_description_compliance") or {}
    derived_naming = naming_cfg.get("derived_scan_naming")

    rows: list[dict] = []

    def log_failure(scan_path: str, dicom_path: str, message: str) -> None:
        if not failure_log:
            return
        line = f"{datetime.now(timezone.utc).isoformat()}\t{scan_path}\t{dicom_path}\t{message}\n"
        with open(failure_log, "a", encoding="utf-8") as lf:
            lf.write(line)

    if layout == "uid-tree":
        groups = _collect_uid_series_files(root)
        for (study_uid, series_uid), file_list in sorted(groups.items(), key=lambda x: (x[0][0], x[0][1])):
            dcm_path = file_list[0][0]
            session_path = f"uid://{study_uid}"
            session_id = study_uid
            scan_path = f"uid://{study_uid}/{series_uid}"
            try:
                ds = pydicom.dcmread(str(dcm_path), stop_before_pixels=True, force=True)
            except Exception as e:
                log_failure(scan_path, str(dcm_path), repr(e))
                cluster = "unknown | unknown | unknownT"
                scan_name = series_uid[:16]
                rows.append(
                    _empty_row(
                        session_path,
                        session_id,
                        scan_name,
                        scan_path,
                        str(dcm_path),
                        cluster,
                        f"read_error:{e}",
                    )
                )
                continue
            scan_name = synthetic_scan_label(ds)
            cluster = scanner_cluster_from_ds(ds)
            rows.append(
                _row_from_dataset(
                    ds,
                    dcm_path,
                    session_path,
                    session_id,
                    scan_name,
                    scan_path,
                    cluster,
                    spatial_cfg,
                    folder_rx,
                    proto_pat,
                    rules,
                    deriv_toks,
                    weights,
                    auto_conv,
                    class_sd_comp,
                    derived_naming,
                )
            )
    elif layout == "xnat":
        for mr_root in find_mr_roots(root):
            cluster = session_scanner_cluster(mr_root)
            session_id = mr_root.name
            scans = sorted(glob.glob(str(mr_root / "scans" / "*")))
            for s in scans:
                scan_path = Path(s)
                if not scan_path.is_dir():
                    continue
                scan_name = scan_path.name
                dcm_path = first_dicom(scan_path)
                err = ""
                if not dcm_path:
                    log_failure(str(scan_path), "", "no_dicom")
                    rows.append(
                        _empty_row(
                            str(mr_root),
                            session_id,
                            scan_name,
                            str(scan_path),
                            "",
                            cluster,
                            "no_dicom",
                        )
                    )
                    continue
                try:
                    ds = pydicom.dcmread(str(dcm_path), stop_before_pixels=True, force=True)
                except Exception as e:
                    log_failure(str(scan_path), str(dcm_path), repr(e))
                    rows.append(
                        _empty_row(
                            str(mr_root),
                            session_id,
                            scan_name,
                            str(scan_path),
                            str(dcm_path),
                            cluster,
                            f"read_error:{e}",
                        )
                    )
                    continue

                rows.append(
                    _row_from_dataset(
                        ds,
                        dcm_path,
                        str(mr_root),
                        session_id,
                        scan_name,
                        str(scan_path),
                        cluster,
                        spatial_cfg,
                        folder_rx,
                        proto_pat,
                        rules,
                        deriv_toks,
                        weights,
                        auto_conv,
                        class_sd_comp,
                        derived_naming,
                    )
                )
    else:
        raise ValueError(f"Unknown layout: {layout!r}; use 'xnat' or 'uid-tree'")

    series_df = pd.DataFrame(rows)
    # Session aggregates
    sess_rows = []
    for sid, g in series_df.groupby("session_id"):
        sub = g[g["read_error"].fillna("") == ""]
        if sub.empty:
            sub = g
        loc_mask = sub["series_class"] == "localizer"
        primary = sub[~loc_mask] if (~loc_mask).any() else sub
        sess_rows.append(
            {
                "session_id": sid,
                "scanner_cluster": g["scanner_cluster"].iloc[0],
                "n_series": len(g),
                "n_scored": len(sub),
                "DBI_session_mean": primary["DBI"].mean(),
                "DBI_session_mean_no_localizer": primary["DBI"].mean() if len(primary) else float("nan"),
                "DBI_session_min": primary["DBI"].min(),
                "DBI_session_median": primary["DBI"].median(),
                "mean_M": primary["M"].mean(),
                "mean_P": primary["P"].mean(),
                "mean_S": primary["S"].mean(),
                "mean_N": primary["N"].mean(),
            }
        )
    session_df = pd.DataFrame(sess_rows)
    return series_df, session_df, cfg_version


def _empty_row(
    session_path: str,
    session_id: str,
    scan_name: str,
    scan_path: str,
    dicom_path: str,
    cluster: str,
    err: str,
) -> dict:
    return {
        "session_path": session_path,
        "session_id": session_id,
        "scan_folder": scan_name,
        "scan_path": scan_path,
        "dicom_path": dicom_path,
        "scanner_cluster": cluster,
        "series_class": "",
        "read_error": err,
        "M": float("nan"),
        "M_pass": 0,
        "M_total": 0,
        "P": float("nan"),
        "P_minimal": float("nan"),
        "P_ideal": float("nan"),
        "G": "",
        "G_na": True,
        "derivative_series": False,
        "S": float("nan"),
        "N": float("nan"),
        "N_pass": 0,
        "N_total": 0,
        "DBI": float("nan"),
        "has_bvalue_evidence": False,
        "has_gradient_direction": False,
    }


def write_figures(series_df: pd.DataFrame, session_df: pd.DataFrame, out_dir: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return

    ok = series_df[series_df["read_error"].fillna("") == ""]
    if ok.empty:
        return

    # Figure 1: DBI by scanner (session mean)
    fig, ax = plt.subplots(figsize=(10, 5))
    clusters = session_df["scanner_cluster"].unique()
    data = [
        session_df[session_df["scanner_cluster"] == c]["DBI_session_mean_no_localizer"].dropna()
        for c in clusters
    ]
    labels = [c[:40] + "…" if len(c) > 40 else c for c in clusters]
    ax.boxplot(data, tick_labels=labels, showfliers=True)
    ax.set_ylabel("DBI (session mean, localizers excluded)")
    ax.set_title("DBI v1 by scanner cluster")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    fig.savefig(out_dir / "figure1_dbi_by_scanner.png", dpi=150)
    plt.close()

    # Supplement: class counts
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ok.groupby("series_class")["DBI"].mean().sort_values().plot(kind="barh", ax=ax2)
    ax2.set_xlabel("Mean DBI")
    ax2.set_title("Mean DBI by heuristic series class")
    plt.tight_layout()
    fig2.savefig(out_dir / "figure_supp_dbi_by_class.png", dpi=150)
    plt.close()


def main() -> None:
    ap = argparse.ArgumentParser(description="CIDUR DBI v1 audit")
    ap.add_argument(
        "--root",
        type=Path,
        default=Path("/mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/Documents/CIDUR_data"),
        help="CIDUR_data root",
    )
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "outputs")
    ap.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).resolve().parent / "dbi_v1_config.yaml",
    )
    ap.add_argument(
        "--layout",
        choices=("xnat", "uid-tree"),
        default="xnat",
        help="xnat: CIDUR/XNAT tree; uid-tree: recurse *.dcm, group by Study/Series UID (MR only)",
    )
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    fail_log = args.out / "read_failures.log"
    if fail_log.exists():
        fail_log.unlink()
    with open(fail_log, "w", encoding="utf-8") as lf:
        lf.write("utc_timestamp\tscan_path\tdicom_path\tmessage\n")

    meta = {
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(args.root.resolve()),
        "layout": args.layout,
        "n_mr_sessions": len(find_mr_roots(args.root)) if args.layout == "xnat" else None,
    }
    series_df, session_df, cfg_version = run_audit(
        args.root, args.out, args.config, failure_log=fail_log, layout=args.layout
    )
    meta["dbi_spec_version"] = cfg_version
    if args.layout == "uid-tree":
        meta["n_mr_sessions"] = int(session_df["session_id"].nunique())

    series_path = args.out / "per_series.csv"
    session_path = args.out / "per_session.csv"
    series_df.to_csv(series_path, index=False)
    session_df.to_csv(session_path, index=False)

    meta["n_series_rows"] = len(series_df)
    meta["n_session_rows"] = len(session_df)
    meta["mean_dbi_series"] = float(series_df["DBI"].mean(skipna=True))
    meta["mean_dbi_session"] = float(session_df["DBI_session_mean_no_localizer"].mean(skipna=True))

    with open(args.out / "run_metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # Table 1 style summary
    tbl = (
        session_df.groupby("scanner_cluster")
        .agg(
            n_sessions=("session_id", "count"),
            DBI_mean=("DBI_session_mean_no_localizer", "mean"),
            DBI_std=("DBI_session_mean_no_localizer", "std"),
            DBI_min=("DBI_session_mean_no_localizer", "min"),
            DBI_max=("DBI_session_mean_no_localizer", "max"),
        )
        .reset_index()
    )
    tbl.to_csv(args.out / "table1_dbi_by_scanner.csv", index=False)

    write_figures(series_df, session_df, args.out)

    print(f"Wrote {series_path} ({len(series_df)} rows)")
    print(f"Wrote {session_path} ({len(session_df)} rows)")
    print(f"Wrote {args.out / 'table1_dbi_by_scanner.csv'}")
    print(f"Wrote {args.out / 'run_metadata.json'}")
    flines = fail_log.read_text(encoding="utf-8").splitlines()
    n_fail_lines = max(0, len(flines) - 1)
    print(f"Wrote {fail_log} ({n_fail_lines} failure row(s))")


if __name__ == "__main__":
    main()
