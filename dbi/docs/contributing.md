# Contributing

Thanks for considering a contribution.

## Quick loop

```bash
# clone & install
git clone https://github.com/phindagijimana/vecta.git
cd vecta
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# tests
make test            # pytest

# docs
make serve           # http://127.0.0.1:8000 with live reload
make docs-strict     # what CI runs
```

## Where to make a change

| Want to …                                       | Edit                                                                |
|-------------------------------------------------|---------------------------------------------------------------------|
| Adjust a weight or threshold                    | `dbi/dbi_v1_config.yaml`                                            |
| Add / change a classification rule              | `classification_rules:` in `dbi_v1_config.yaml`                     |
| Add a naming convention                         | `naming.automation_conventions:` in `dbi_v1_config.yaml` (+ cite)    |
| Change scoring logic                            | `dbi/scoring.py` and `dbi/tests/test_scoring.py`                    |
| Change the audit CLI                            | `dbi/run_audit.py`                                                   |
| Change the dcm2niix runner                      | `dbi/run_dcm2niix_batch.py`                                          |
| Change the spec                                 | `dbi/DBI_v1_SPECIFICATION.md` (bump `version:` in the config too)    |
| Edit docs you are reading                       | `dbi/docs/**.md` and `dbi/mkdocs.yml`                                |

## Guidelines

- **Cite when you add a naming convention.** The point of
  `automation_conventions` is that it is normative and reproducible; every
  convention has a `source:` and a `downstream_benefit:` block (see
  [Naming conventions](configuration/naming-conventions.md)).
- **Add a unit test for any new scoring branch.** `tests/test_scoring.py` has
  scaffolding for synthetic `pydicom.Dataset` fixtures.
- **Bump the config `version:` when scores change.** Downstream consumers rely
  on `run_metadata.json.dbi_spec_version` to detect drift.
- **Keep docs in sync.** If you add a CSV column, update
  [`outputs/csv-schema.md`](outputs/csv-schema.md). If you change a CLI flag,
  update [`cli/`](cli/index.md).

## Style

- Python: ruff defaults are fine; line length 100; prefer the explicit pydicom
  `Tag` form (`(0xGGGG, 0xEEEE)`) over keywords for clarity in the scoring core.
- Docs: short sentences, one idea per paragraph, code blocks fenced with
  language hints (Material's syntax highlighting depends on it).

## Reporting issues

Open an issue at
[github.com/phindagijimana/vecta/issues](https://github.com/phindagijimana/vecta/issues).
Useful information:

- DBI spec version (`run_metadata.json.dbi_spec_version`).
- Layout (`--layout`).
- A minimal cohort that reproduces the problem (one anonymised DICOM is often
  enough — DBI reads only the first file per series).
