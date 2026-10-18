# Reproducing the surge indicators

Both indicator families in the current 71-country snapshot reproduce exactly: **238,560 comparisons per family, zero differences**. Every `NormShockCountGt3` field also equals `NormShock == 1 and raw_count > 3`. The [saved results](../outputs/surge_reconstruction_summary.json) record these checks.

## Source and method

The calculation uses the complete [October 13, 2026 aggregate export](https://huggingface.co/datasets/zungru/mlp-counts/resolve/cba21755f1293e2c3808e07e542ae00a79e03df7/full-mleed-data.csv): 12,576 rows for 71 countries, starting in January 2012 and extending as far as October 2026. Country endpoints vary. This file is byte-identical to the combined CSV at [MLP-data-intro commit `03680567`](https://github.com/ML4PDevLab/MLP-data-intro/tree/03680567f283a8613b2516b7217dfe2bf63b1a5e). Its checksum is:

```text
736719f220aff515a75c4fb0be4e117927be6fda51d52bf35d1719ffbcaefcbe
```

[`recovered_surge.py`](../scripts/recovered_surge.py) retains the upstream `PeakDetector` class and `convert_to_training_data_2` function. Their definition hashes are checked before execution. Only these definitions are imported; no production entrypoint, model job or database operation runs. The definitions retain the [upstream MIT notice](../licenses/MLP-data-intro-MIT.txt).

The verified run uses TensorFlow disabled (`loaded_model=None`), twelve months on either side, a threshold multiplier of 0.88, winsorization mode 1, left-weight decay 0.2 and right-weight decrement 0.05. It preserves the top-three magnitude rule and sequential neighboring-month adjustment. The second indicator additionally requires a raw count greater than three. Full settings and source hashes appear in [surge_provenance.json](../validation/surge_provenance.json).

The comparison first supplies all source months, then selects January 2012–December 2025. Those historical rows contain no missing values. The full input has 1,780 missing normalized cells in later 2026 months; they are retained to reproduce the published calculation. With the source's default handling, a missing value in a series propagates through its z-scores and disables winsorization for that series. For an all-finite series containing an absolute z-score above two, the ceiling-based rule selects 10% winsorization in each tail.

This explains why using only the historical extract can change results: preprocessing uses the whole series, and neighboring months and the top-three rule also depend on the supplied window. These are retrospective measures of elevated reporting. Record the complete input window, missing-value pattern, code and settings when creating a new version.

## Run the verification

With the pinned requirements installed:

```bash
python scripts/reproduce_surges.py --download-source --check
```

This downloads the pinned aggregate CSV into `analysis/full-mleed-source-20261013.csv` if absent, checks its SHA-256, verifies the historical extraction and compares every stored indicator. It never overwrites the release CSV. Later runs can use `--check` alone. To supply an existing copy:

```bash
python scripts/reproduce_surges.py --source-csv path/to/full-mleed-data.csv --check
```

The supplied CSV must match the pinned source checksum. To rebuild only the verification summary after an intended code change, replace `--check` with `--write-summary`.

The historical extraction is independently reproducible:

```bash
python scripts/freeze_snapshot.py --source-csv analysis/full-mleed-source-20261013.csv --check
```

It reads fields as text, retains the 2012–2025 rows, sorts by country and date, and preserves numeric tokens and field order. An explicit `--write` mode is available for recreating the recorded snapshot; it refuses to replace an unrecognized existing data file.

## Earlier version

The previous 69-country file had 36 count-screen discrepancies and did not match the recovered routine on its historical input window. Those findings belong to [commit `81c30ac`](https://github.com/ML4PDevLab/MLEED-public/tree/81c30acb56d9d05779c92cb583c04b730b39c680). Its [audit records](../validation/history/69_country_20261005/README.md) remain available. They do not describe the current 71-country export, which uses a newer source snapshot and verified indicators.
