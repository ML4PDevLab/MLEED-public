# Reusing the national monthly data

## Reading and joining

Read the UTF-8 CSV with `country` as text and `date` as a month-start date. The primary key is `(country, date)`. The file is balanced across 71 countries and 168 months, but this structural property does not establish completeness of underlying news collection.

The exact country strings are listed in [the schema](../metadata/schema.json). Retain the original strings and add an explicit crosswalk for external joins. In particular, the snapshot uses `DR Congo`, `Macedonia`, `Timor Leste`, and `Turkey`. Do not silently change these strings or assume they are ISO identifiers. Names are release identifiers and do not express a position on territorial status.

```python
import pandas as pd

data = pd.read_csv("data/mleed_country_month_2012_2025.csv", parse_dates=["date"])
assert not data.duplicated(["country", "date"]).any()
data["displacement_labels_per_10000_documents"] = data["displacementNorm"] * 10_000
data["environmental_violence_labels"] = (
    data["lethal environmental violence"]
    + data["nonlethal environmental violence"]
)
```

## Counts, reporting rates, and zeros

Raw counts describe assigned labels in reporting. Multiple articles may describe the same event; a document may contribute primary and secondary labels. Pooling violence adds the two stored label counts. It does not establish a count of unique articles about violence.

An international report may contribute to more than one country. Summed country-month article counts therefore represent document contributions, not a deduplicated global corpus. Grouped reporting rates are ratios of those contributions. Cross-country pooling does not remove duplication of shared international reports.

Stored `Norm` fields are proportions, not percentages or values already scaled per 10,000. For a combined period or group, divide the sum of label counts by the sum of matching `total_local_docs` values. An unweighted average of monthly rates answers a different question.

```python
annual = data.groupby(["country", "year"], as_index=False).agg(
    displacement_labels=("displacement", "sum"),
    local_documents=("total_local_docs", "sum"),
)
annual["labels_per_10000_documents"] = (
    annual["displacement_labels"] / annual["local_documents"] * 10_000
)
```

The denominator controls for observed reporting volume, not population at risk, total event occurrence, or all selection differences among news sources. Comparisons should consider changing source availability, language coverage, editorial attention, retrieval failures, and classification error.

A zero label count means no such labels occur in the included records for that month. It is not proof that no event occurred. This snapshot has no missing cells and a positive denominator in every row; some denominators are as small as two documents. Inspect [country coverage](../outputs/country_coverage.csv) and the original denominators when deciding whether a reporting rate is informative.

## Surge indicators

The stored indicators identify elevated reporting within each country-label series. Both families reproduce exactly from the complete pinned source; [surge reproduction](surge_reconstruction.md) provides the verification command. `NormShockCountGt3` additionally requires more than three assigned labels in the month, and every stored field agrees with that rule.

Use the complete source window when reproducing these retrospective indicators, then select the months needed for analysis. The detector uses earlier and later observations and whole-series preprocessing, so shortening the window or adding new months can change flags. A new analytical rule should have a distinct name and documented baseline, window, threshold and missing-value treatment.

## Supplied code

`build_overview.py` validates the panel and recreates neutral descriptive outputs. `export_long.py` creates 190,848 country-month-category rows with six fields: `country`, `date`, `total_local_docs`, `category`, `label_count`, and `labels_per_10000_documents`. The denominator repeats for each category and must not be summed across categories.

`verify_evaluation.py` recalculates aggregate classifier metrics and human-audit fractions. It does not retrain a model or rerun news collection. [Validation documentation](../validation/README.md) explains what the evaluation samples support.

These scripts run without database credentials. Collection, translation, inference, and geographic extraction are not reproduced here. The isolated surge verifier reproduces the current stored indicators while preserving the release data. National and subnational dashboards are separate products and should not be joined as though they have identical coverage or denominators.
