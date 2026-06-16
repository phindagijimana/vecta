# Configuration

Everything that influences DBI lives in one YAML file:
[`dbi_v1_config.yaml`](https://github.com/phindagijimana/vecta/blob/main/dbi/dbi_v1_config.yaml).

That includes:

- The composite **weights** (`weights:`)
- Physical **spatial bounds** (`spatial:`)
- Series **classification rules** (`classification_rules:`)
- **Naming compliance** — automation conventions, per-class SeriesDescription
  rules, derived-scan suffix rule (`naming:`)
- The optional **prospective protocol token** (`protocol_token:`)

Two pages cover the details:

- [**YAML reference**](yaml-reference.md) — section by section.
- [**Naming conventions**](naming-conventions.md) — the
  `naming.automation_conventions` block, with citations and downstream rationale.

## Overriding the config

Pass `--config` to either CLI:

```bash
dbi-audit   --config /path/to/site_config.yaml ...
dbi-convert --config /path/to/site_config.yaml ...
```

The reader (`scoring.load_yaml_config`) is a thin `yaml.safe_load`, so any
well-formed YAML works. There is no schema validation — copy the bundled file
and edit it.

## Versioning

The top-level `version:` field is echoed into `run_metadata.json` as
`dbi_spec_version`. Bump it when you change weights, regexes, or thresholds so
downstream comparisons can distinguish "score moved because the data changed"
from "score moved because the config changed".

## A pragmatic override pattern

If you want to enforce a stricter naming policy at your site without forking the
package:

1. Copy `dbi/dbi_v1_config.yaml` to your project as `site_dbi_config.yaml`.
2. Edit it (e.g. set `automation_conventions[*].enabled` per your policy).
3. Bump `version:` to something like `1.0.5-mysite-1`.
4. Always pass `--config site_dbi_config.yaml` when running.

Now `run_metadata.json` carries the site version, and any downstream report can
report the exact config that produced it.
