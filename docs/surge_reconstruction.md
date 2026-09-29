# Recovered surge routine and historical comparisons

The repository now includes a safe, isolated copy of the project's surge definitions and a script for comparing their outputs with stored indicators. The comparison **does not replace the original national CSV**. Recovering code is distinct from establishing the exact input state that generated a historical export.

## Code and scope

[`scripts/recovered_surge.py`](../scripts/recovered_surge.py) retains the `PeakDetector` class and `convert_to_training_data_2` function from [MLP-data-intro commit `fea13989b8ee6803d1ed82f091097730ae04f727`](https://github.com/ML4PDevLab/MLP-data-intro/tree/fea13989b8ee6803d1ed82f091097730ae04f727/build_data/shock_detection). These definitions are unchanged. The original run-on-import entrypoint, filesystem writes, unrelated pipelines, model loading, and plotting have been excluded. The copied definitions retain their existing [MIT notice](../licenses/MLP-data-intro-MIT.txt), copyright 2025 Machine Learning for Peace. That notice does not license the aggregate data or other original code in this repository.

[`scripts/reproduce_surges.py`](../scripts/reproduce_surges.py) runs the definitions with TensorFlow disabled (`loaded_model=None`): a 12-month window on either side, threshold multiplier 0.88, winsorization mode 1, left-weight decay 0.2, and right-weight decrement 0.05. It preserves the source's top-three magnitude rule and sequential neighboring-month adjustment, including its handling of missing values. The screened candidate is the resulting indicator AND raw count greater than three. No neural-network weights are used or claimed to be reproduced.

Input hashes, definition hashes, parameters, and immutable source URLs are recorded in [surge_provenance.json](../validation/surge_provenance.json). The script verifies the copied definitions and input hashes before comparing values. It uses all months supplied for each country, then compares the 69-country, 2012–2025 overlap with the frozen release: 231,840 cells per indicator family (11,592 observations × 20 label series).

## What reproduces

| Input supplied to recovered routine | Differences from that input's stored indicators, raw / screened | Differences from frozen release, raw / screened |
| --- | --- | --- |
| Frozen public file, January 2012–December 2025 | 10,131 / 6,053 | 10,131 / 6,053 |
| Full source file at 23 August 2026 commit `622e8253` | 0 / 0 | 105 / 52 |
| Full source file at 4 August 2026 commit `cbfc9d5f` | 0 / 0 | 468 / 290 |

All comparisons in the table concern the same historical 69-country overlap, even when the routine receives later months. The full August source files can reproduce their own stored indicators exactly on those cells. Neither reproduces the frozen CSV exactly. Counts and normalized values in the frozen file match the 4 August input on the shared historical cells; their indicator differences remain. Results, including raw/normalized input comparisons, are in [surge_reconstruction_summary.json](../outputs/surge_reconstruction_summary.json).

The 36 stored `NormShockCountGt3` discrepancies documented in [indicator_diagnostics.csv](../outputs/indicator_diagnostics.csv) are a separate test: they compare each frozen screened field with its *stored* raw indicator and count greater than three. They should not be confused with the reconstructed-candidate differences in the table.

## Why input windows matter

The detector uses both earlier and later months, and its preprocessing examines the entire supplied country-label series. The source computes z-scores with the default handling of missing values. If a series contains a missing value, the propagated missing z-scores yield no detected outliers and disable winsorization for that series. For an all-finite series with at least one z-score above two in absolute value, the source's ceiling-based expression selects 10% winsorization in each tail. This behavior is preserved for forensic comparison, not recommended as a new missing-data policy.

Truncating a full series to the complete 2012–2025 window can therefore change flags well before the cutoff. Appending later observations can also change neighboring-month comparisons and the forced top-three selection. These indicators are retrospective descriptors, not fixed real-time alerts or automatically valid out-of-sample signals. Record the entire input window, missing-value pattern, code version, and settings when constructing new indicators.

## Reproduce the comparisons

Use the pinned dependencies in `requirements.txt` (Python 3.11; NumPy 1.26.4, pandas 2.1.4, SciPy 1.15.3 for these checks). These are the tested public-package dependencies, not a claim about the original historical execution environment.

```bash
python scripts/reproduce_surges.py --check
```

This verifies the frozen-input comparison only. It does not download or silently substitute later source files. To repeat both full-window comparisons, obtain the two pinned **aggregate CSVs** and supply them explicitly:

```bash
mkdir -p analysis
curl --fail --location https://raw.githubusercontent.com/ML4PDevLab/MLP-data-intro/622e82535612476e7952a141623c3c48ecbee85a/data/final-counts/full-mleed-data.csv --output analysis/surge-source-20260823.csv
curl --fail --location https://raw.githubusercontent.com/ML4PDevLab/MLP-data-intro/cbfc9d5fa7355c997f5efccdfb2047a1ca550551/data/final-counts/full-mleed-data.csv --output analysis/surge-source-20260804.csv
python scripts/reproduce_surges.py --source-csv analysis/surge-source-20260823.csv --source-csv analysis/surge-source-20260804.csv --check
```

Each external file must match its recorded SHA-256; only the two named source snapshots are accepted. To regenerate the summary after reviewing intended code changes, use the same two input arguments with `--write-summary` instead of `--check`. No command above changes the canonical CSV. The exact creation lineage of its stored indicators remains unresolved, and users should not treat the reconstructed candidates as silently corrected historical data.
