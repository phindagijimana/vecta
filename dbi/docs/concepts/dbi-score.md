# The DBI score

## Definition

For one series, DBI is the **weighted mean of the applicable components**:

$$
\mathrm{DBI} \;=\; \frac{\displaystyle\sum_{c \in \text{applicable}} w_c \cdot s_c}
                       {\displaystyle\sum_{c \in \text{applicable}} w_c}
$$

where each $s_c \in [0, 1]$ and the default weights $w_c$ come from
[`dbi_v1_config.yaml`](../configuration/yaml-reference.md):

| Component                | Symbol | Weight (v1) |
|--------------------------|:------:|:-----------:|
| Metadata completeness    |   M    |    0.28     |
| Protocol naming          |   P    |    0.18     |
| Gradient integrity (DWI) |   G    |    0.22     |
| Spatial consistency      |   S    |    0.17     |
| Naming compliance        |   N    |    0.15     |
| Drift control            |   D    |    0.00     |

`D` (cohort-drift control) is reserved for a future version and contributes 0 in v1.

## Why renormalize?

Not every component applies to every series. The clearest example is `G`:
gradient integrity on a T1w MPRAGE is meaningless, so it returns **N/A**. Forcing
non-DWI series to score 0 on `G` would penalize them for a check that doesn't
apply, so DBI drops both the score *and* the weight from the denominator.

Concretely, for a T1w series with $M{=}1$, $P{=}1$, $G{=}\text{N/A}$, $S{=}1$, $N{=}1$:

$$
\mathrm{DBI} = \frac{0.28(1) + 0.18(1) + 0.17(1) + 0.15(1)}{0.28 + 0.18 + 0.17 + 0.15} = 1.0
$$

The `G` weight (0.22) is excluded from both numerator and denominator.

## What DBI is *not*

- **Not** an SNR / motion / clinical-quality measure. A series with perfect
  metadata and a motion-blurred image will still score DBI = 1.
- **Not** a per-voxel metric. DBI looks at one DICOM per series — the first readable
  file in the folder — and trusts that tag values are series-level.
- **Not** a BIDS-compliance check. DBI is **upstream** of BIDS: it tells you whether
  the data is clean enough for HeuDiConv / dcm2niix to succeed *in the first place*.

## Aggregating across a session / cohort

`dbi-audit` emits a per-session aggregate row alongside the per-series rows. By
default the session-level summary is the **mean DBI over non-localizer series**:

| Field                            | Meaning                                                   |
|----------------------------------|-----------------------------------------------------------|
| `DBI_session_mean`               | Mean over all scored series (incl. localizers).           |
| `DBI_session_mean_no_localizer`  | Mean over scored series excluding `localizer` class.      |
| `DBI_session_min`                | Worst-scoring series in the session.                      |
| `DBI_session_median`             | Median DBI across the session.                            |

For cohort comparisons across scanners, stratify by
[`scanner_cluster`](scanner-cluster.md) — that is the official v1 covariate.
