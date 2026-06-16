# CLI reference

Two commands ship with the package:

| Command       | Source                       | Purpose                                                      |
|---------------|------------------------------|--------------------------------------------------------------|
| [`dbi-audit`](dbi-audit.md)     | `dbi/run_audit.py`           | Walk a DICOM tree, score every MR series, write CSVs + figures. |
| [`dbi-convert`](dbi-convert.md) | `dbi/run_dcm2niix_batch.py`  | Run `dcm2niix` per scan folder and log convert-pass per series. |

Both expose `main()` so you can also invoke them as modules:

```bash
python -m dbi.run_audit --root /path/to/cohort --out ./outputs
python -m dbi.run_dcm2niix_batch --root /path/to/cohort --out ./outputs_dcm2niix
```

## Common patterns

### Run on an XNAT-style cohort

```bash
dbi-audit   --root /data/CIDUR_data --out ./outputs
dbi-convert --root /data/CIDUR_data --out ./outputs_dcm2niix --nifti-root /data/nifti
```

### Run on a flat DICOM tree

```bash
dbi-audit --layout uid-tree --root /data/loose_dicoms --out ./outputs_uid
```

### Smoke-test before a long run

```bash
dbi-convert --root /data/CIDUR_data --out ./outputs_dcm2niix --dry-run --limit 5
```

`--dry-run` lists the work without invoking dcm2niix; `--limit 5` stops after 5 scan
folders. Useful for confirming the path discovery is correct.
