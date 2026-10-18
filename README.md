# Machine Learning for Environmental Event Detection (MLEED)

MLEED measures monthly news reporting about environmental hazards and the responses of communities, governments and firms. The country summaries cover **71 countries from January 2012 through December 2025**. They support questions about which issues attract attention, how long that attention lasts, and which responses accompany environmental disruption.

The file contains **11,928 country-month rows and 88 columns**: category counts, shares of locally relevant news, and surge indicators. Its totals are 1,782,400 screened article contributions, 1,981,939 label assignments and 59,611,079 document contributions to the denominator. An article can receive two labels and can contribute to more than one country, so these sums describe country-level reporting rather than unique global articles.

## Start here

| Resource | Contents |
| --- | --- |
| [Country summaries](data/mleed_country_month_2012_2025.csv) | 71 countries × 168 months, with complete fields |
| [Data dictionary](docs/data_dictionary.md) and [schema](metadata/schema.json) | Fields, category definitions and country names |
| [Country coverage](outputs/country_coverage.csv) and [year coverage](outputs/year_coverage.csv) | Reporting volume and denominators |
| [Reuse guide](docs/reuse.md) | Counts, reporting shares, category pooling and example code |
| [Validation evidence](validation/README.md) | Classifier results and human-review totals |
| [Surge reproduction](docs/surge_reconstruction.md) | Exact reproduction from the pinned complete input |
| [Source and version record](metadata/source_snapshot_71_20261018.json) | Public source, extraction, changes and known processing issue |
| [Snapshot metadata](metadata/snapshot.json), [manifest](metadata/release_manifest.json) and [checksums](SHA256SUMS) | File identity |

The sixteen substantive categories cover hazards and individual, civic, corporate and governmental responses. The file stores lethal and nonlethal violence separately; pool them for the sixteen-category taxonomy. Three auxiliary classifier labels are retained for accounting. A `Norm` value is the category count divided by all locally relevant documents in that country-month; multiply by 10,000 for labels per 10,000 documents. The screened article pool can include the category classifier's non-environmental (`-999`) label. The dictionary explains the inclusion rules.

Both surge-indicator families reproduce exactly from the pinned October 13, 2026 source export: **238,560 comparisons per family, with zero differences**. The count-screened field equals `NormShock == 1 and raw_count > 3` throughout this version. Because the detector uses neighboring months and the full input series, reproduce the indicators from the complete source before selecting the historical release window.

## Run the checks

Use Python 3.11 and the pinned dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/build_overview.py --validate-only
python scripts/verify_evaluation.py --check
python scripts/reproduce_surges.py --download-source --check
python scripts/freeze_snapshot.py --source-csv analysis/full-mleed-source-20261013.csv --check
python scripts/test_validation.py
python scripts/build_manifest.py --check
```

The surge command downloads a checksum-verified aggregate CSV into `analysis/` if absent. The other commands check local files without database access. Run `python scripts/build_overview.py` to rebuild summaries and the category figure. After reviewing intended changes, use `python scripts/build_manifest.py` to refresh file checksums.

To create 190,848 country-month-category rows with the sixteen substantive categories:

```bash
python scripts/export_long.py --output analysis/mleed_16_categories.csv
```

This export pools violence, preserves category counts and refuses to overwrite an existing file.

## Version and access

This version uses the [October 13 public export](https://huggingface.co/datasets/zungru/mlp-counts/tree/cba21755f1293e2c3808e07e542ae00a79e03df7), adds Iraq and Libya, and updates historical values in 53 existing countries. The [earlier 69-country version](https://github.com/ML4PDevLab/MLEED-public/tree/81c30acb56d9d05779c92cb583c04b730b39c680) remains available in Git; its surge diagnostics are [archived separately](validation/history/69_country_20261005/README.md). The 431-case classifier evidence and 1,481-article human review are unchanged historical evaluations.

One known processing issue remains: 25,599 included historical Libya records await translation, classification and geographic processing. They contribute to the denominator; their eventual processing may change category counts and country assignment. The [source record](metadata/source_snapshot_71_20261018.json) documents the current check. Complete monthly aggregate fields do not certify complete source collection.

The package contains aggregate data and numeric validation reports. Full news text, individual predictions and database credentials are excluded. Aggregate-data and original-code licenses and an archival DOI remain to be assigned. The copied surge definitions retain their existing [upstream MIT license](licenses/MLP-data-intro-MIT.txt). See [release scope](docs/repository_scope.md) for the remaining deposit items.

Until the archival citation is assigned, cite the repository, exact Git commit, snapshot ID `mleed-country-month-2012-2025-71-20261018` and data SHA-256:

```text
78c1d7ba8728fb3b83027ee90c6b7abc4958921ed543b2588821a1657867fef3
```

## Related resources

- [National dashboard](https://huggingface.co/spaces/zungru/mlp-mleed-dashboard)
- [Regional and local dashboard](https://huggingface.co/spaces/zungru/subnational-env-dashboard)
- [MLP pipeline documentation](https://github.com/ML4PDevLab/MLP-data-intro)
- [Machine Learning for Peace](https://web.sas.upenn.edu/mlp-devlab/)

Country and administrative-area products answer different geographic questions. Cite the exact data version and geographic unit used in an analysis.
