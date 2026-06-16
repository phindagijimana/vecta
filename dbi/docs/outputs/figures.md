# Figures

Both CLIs ship optional matplotlib figures. They are written when matplotlib is
importable; otherwise the audit / convert run still succeeds and the figures are
simply skipped.

## `figure1_dbi_by_scanner.png`

Box plot of **session-mean DBI** (`DBI_session_mean_no_localizer`) per
`scanner_cluster`. One box per cluster; outliers shown. This is the headline
plot for cross-scanner comparisons — by reporting the cluster as covariate,
you separate "the data needs work" from "we're comparing apples and pears".

## `figure_supp_class_means.png`

Horizontal bar chart of **mean DBI per heuristic class** across the cohort.
Useful for triaging which class is dragging the score down before you commit to
a cohort-wide fix.

## `figure2_dcm2niix_pass_rate_heatmap.png`

Heatmap of `convert_pass` rate per `scanner_cluster × series_class`, computed
from `table2_conversion_by_scanner_class.csv`. Combine this with Figure 1 to ask:

- *Does low DBI predict failed conversion?* Look for clusters that score low
  on Figure 1 and also have dark rows on Figure 2.
- *Is one class systematically failing?* A vertical dark stripe in Figure 2
  flags a class that isn't ready for downstream automation cohort-wide.

## Disabling figures

There is no explicit `--no-figures` flag in v1; the figures are simply skipped
when matplotlib is not importable. If you want a guaranteed text-only run, do:

```bash
PYTHONNOUSERSITE=1 python -c "import sys; sys.modules['matplotlib']=None" \
    dbi-audit --root ...
```

or just install without matplotlib (it's listed as a hard dep in `requirements.txt`
today, so you would need to remove it from your env).
