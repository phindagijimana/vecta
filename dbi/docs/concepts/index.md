# Concepts

The four ideas you need to read everything else:

- [**The DBI score**](dbi-score.md) — what the number means, how the weighted
  mean is computed, and how N/A components are dropped from the denominator.
- [**Components (M / P / G / S / N)**](components.md) — what each sub-score
  measures, what counts as a "pass", and when it goes N/A.
- [**Series classification**](classification.md) — how each scan folder is
  labelled (`dwi`, `bold`, `flair`, …) and why that label drives which checks run.
- [**Scanner cluster**](scanner-cluster.md) — the covariate that is *reported
  alongside* DBI but never enters the composite.

DBI is intentionally narrow:

> A series satisfying DBI = 1.0 has metadata, naming, and structural tags clean enough
> for downstream automation (BIDS conversion, pipeline routing, ML loaders).
> It says **nothing** about clinical / diagnostic quality.

If you only have time to read one page, read [**The DBI score**](dbi-score.md).
