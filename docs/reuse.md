# Reusing the national monthly data

## Reading and joining

Read the UTF-8 CSV with `country` as text and `date` as a month-start date. The primary key is `(country, date)`. The file is balanced across 69 countries and 168 months, but this structural property does not establish completeness of underlying news collection.

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

The indicators are retained from the historical export. Their production algorithm and fitted state have not been linked to this snapshot. `NormShockCountGt3` must not be interpreted only from its suffix: 36 cells fail the literal comparison with `NormShock` and raw count greater than three. [The diagnostic file](../outputs/indicator_diagnostics.csv) identifies each affected country, month, and label.

This discrepancy does not change the independently checked count-to-denominator identities. Analysts can build a new surge measure from count or normalized series, but should give it a new name and report its baseline, window, threshold, minimum count, and treatment of early months. Do not silently overwrite stored fields or claim to reproduce their historical method.

## Supplied code

`build_overview.py` validates the panel and recreates neutral descriptive outputs. `export_long.py` creates 185,472 country-month-category rows with six fields: `country`, `date`, `total_local_docs`, `category`, `label_count`, and `labels_per_10000_documents`. The denominator repeats for each category and must not be summed across categories.

`verify_evaluation.py` recalculates aggregate classifier metrics and human-audit fractions. It does not retrain a model or rerun news collection. [Validation documentation](../validation/README.md) explains what the evaluation samples support.

These scripts run without database credentials. Collection, translation, inference, geographic extraction, and historical surge fitting are not reproduced here. National and subnational dashboards are separate products and should not be joined as though they have identical coverage or denominators.
