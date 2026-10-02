# Machine Learning for Environmental Event Detection (MLEED)

MLEED measures news reporting about environmental hazards and human responses to environmental stress. This repository contains a national monthly snapshot for **69 countries, January 2012–December 2025**, documentation, aggregate evaluation reports, and code for checking and reusing these files.

The CSV has 11,592 country-month observations and 88 columns. Summing its country-month counts gives 1,643,983 contributions to the screened article pool, 1,839,196 assigned labels, and 58,223,860 locally relevant document contributions in the normalization denominator. The screened pool contains articles that passed the environmental-relevance screen and have a category-classification record; the second model can still assign its non-environmental (`-999`) label. An international report may contribute to more than one country, so cross-country sums are not counts of unique corpus documents. Each row represents a country-month; each category count records assigned article labels. Documents can receive more than one label. These are measures of reporting, not counts of distinct physical events or people affected. See the [data dictionary](docs/data_dictionary.md) for the documented inclusion rules and their provenance limits.

This is a **pre-publication snapshot**, not a certified release of the current live collection. A broader collection roster or newer dashboard does not establish complete coverage in this file. No 2026 national records are included here.

## Files and documentation

| Resource | Contents |
| --- | --- |
| [National data](data/mleed_country_month_2012_2025.csv) | Unchanged CSV: 69 countries × 168 months |
| [Data dictionary](docs/data_dictionary.md) | Observation unit, labels, derived fields, and interpretation |
| [Machine-readable schema](metadata/schema.json) | All 88 fields, types, definitions, and exact country names |
| [Country coverage](outputs/country_coverage.csv) and [year coverage](outputs/year_coverage.csv) | Observed reporting volume in the deposited file |
| [Validation materials](validation/README.md) | Classifier matrices/reports and a human-review summary, with limitations |
| [Reuse guide](docs/reuse.md) | Rates, category pooling, joins, zeros, and examples |
| [Surge reconstruction](docs/surge_reconstruction.md) | Recovered code, full-input comparisons, and unresolved frozen-indicator lineage |
| [Snapshot metadata](metadata/snapshot.json), [manifest](metadata/release_manifest.json), and [checksums](SHA256SUMS) | Explicit inventory and file identity |
| [Release scope](docs/repository_scope.md) and [changelog](CHANGELOG.md) | Available materials and remaining publication requirements |

## What the labels mean

The 16 substantive categories cover environmental hazards; displacement, environmental crime, and violence; civic and corporate responses; and government actions. The stored data separate lethal and nonlethal violence, giving 17 substantive count columns. Pool those two columns for the 16-category taxonomy. Three additional classifier fields are retained for accounting and excluded from substantive summaries.

Each label has a raw count, a normalized value (`Norm`), and two stored surge indicators. A normalized value is a label count divided by all locally relevant documents in that country-month. Multiply it by 10,000 for **labels per 10,000 documents**.

A recovered surge routine is available for comparison, but it does not exactly reproduce this frozen snapshot's indicators; see [surge reconstruction](docs/surge_reconstruction.md). Separately, in 36 cells, the field ending `NormShockCountGt3` differs from `NormShock == 1 and raw_count > 3`; see [diagnostic rows](outputs/indicator_diagnostics.csv). Original data remain unchanged. Use raw counts or normalized values when an independently reproducible measure is needed.

## Run the checks

Tested with Python 3.11 and the pinned dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/build_overview.py --validate-only
python scripts/verify_evaluation.py --check
python scripts/reproduce_surges.py --check
python scripts/test_validation.py
python scripts/build_manifest.py --check
```

To regenerate structural summaries, coverage tables, diagnostics, and the descriptive figure, run `python scripts/build_overview.py`. Rebuild evaluation summaries with `python scripts/verify_evaluation.py`. After reviewing intended changes, refresh the inventory with `python scripts/build_manifest.py`. Structural checks do not certify that every source was collected or every label is correct.

To create a tidy file with the 16 substantive categories and transparent reporting rates:

```bash
python scripts/export_long.py --output analysis/mleed_16_categories.csv
```

The export preserves counts, pools violence, excludes auxiliary labels, and refuses to overwrite existing files. See the [reuse guide](docs/reuse.md) for Python examples.

## Access, rights, and citation

The package contains aggregate country-month measures and numeric validation reports. Full news text, individual predictions, credentials, private databases, and third-party benchmark data are excluded. It does not yet include a verified version of the historical production pipeline, frozen model weights, or a national 71-country update.

**An explicit aggregate-data license, a license for the original package code, and an archival DOI have not yet been recorded.** The recovered surge definitions alone retain their [existing upstream MIT license](licenses/MLP-data-intro-MIT.txt). Public access is not a substitute for reuse permission. The remaining licenses and DOI must be resolved before representing this package as a completed journal deposit. They should be completed during submission preparation; a paper's publication is not a prerequisite for archiving data.

Until a formal dataset citation is available, identify the repository, exact Git commit, snapshot ID `mleed-country-month-2012-2025`, and data SHA-256:

```text
caa171c34fb33ab5df1e10be8e79e9bbb7d9cb82006c2b4e9f77d9416f47e4c7
```

## Related project resources

- [National MLEED dashboard](https://huggingface.co/spaces/zungru/mlp-mleed-dashboard)
- [Subnational environmental dashboard](https://huggingface.co/spaces/zungru/subnational-env-dashboard)
- [Broader MLP pipeline documentation](https://github.com/ML4PDevLab/MLP-data-intro)
- [Machine Learning for Peace project](https://web.sas.upenn.edu/mlp-devlab/)
- [PDRI–DevLab, University of Pennsylvania](https://pdri-devlab.upenn.edu/)

Dashboards are companion resources. Their files, geographic units, updates, and inclusion rules may differ from this national snapshot; cite the exact product used.
