#!/usr/bin/env python3
"""Validate the public MLEED panel and rebuild neutral overview outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import PercentFormatter


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = REPO_ROOT / "data" / "mleed_country_month_2012_2025.csv"
DEFAULT_OUTPUTS = REPO_ROOT / "outputs"
DEFAULT_FIGURES = REPO_ROOT / "figures"

START_DATE = pd.Timestamp("2012-01-01")
END_DATE = pd.Timestamp("2025-12-01")
EXPECTED_COUNTRIES = 69
EXPECTED_MONTHS = 168
SCHEMA_FILE = REPO_ROOT / "metadata" / "schema.json"

EVENT_COLUMNS = [
    "sudden-onset environmental disaster",
    "environmental cooperation",
    "environmental government initiatives",
    "environmental security",
    "environmental arrest",
    "human-induced disaster",
    "displacement",
    "environmental legal action",
    "slow-onset environmental disaster",
    "environmental corruption",
    "environmental crime",
    "environmental legal change",
    "environmental activism",
    "environmental corporate initiatives",
    "lethal environmental violence",
    "environmental protests",
    "nonlethal environmental violence",
]

AUXILIARY_COLUMNS = [
    "environmental opinion",
    "environmental -999",
    "-999",
]

TOTAL_COLUMNS = [
    "total_articles",
    "total_from_source",
    "total_label_events",
    "total_local_docs",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--outputs", type=Path, default=DEFAULT_OUTPUTS)
    parser.add_argument("--figures", type=Path, default=DEFAULT_FIGURES)
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Run checks without replacing the CSV, JSON, or PNG outputs.",
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_and_validate(path: Path) -> tuple[pd.DataFrame, dict[str, object]]:
    data = pd.read_csv(path)

    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    expected_columns = [field["name"] for field in schema["fields"]]
    if list(data.columns) != expected_columns:
        raise ValueError("CSV columns or column order differ from metadata/schema.json")

    required = {
        "country",
        "date",
        "year",
        "month",
        *TOTAL_COLUMNS,
        *EVENT_COLUMNS,
        *AUXILIARY_COLUMNS,
    }
    missing = sorted(required.difference(data.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    if data.isna().any().any():
        missing_cells = int(data.isna().sum().sum())
        raise ValueError(f"Dataset contains {missing_cells:,} missing cells")

    expected_countries = set(schema["country_names"])
    if set(data["country"]) != expected_countries:
        raise ValueError("Country names differ from the deposited snapshot schema")

    numeric = data.drop(columns=["country", "date"])
    if not all(pd.api.types.is_numeric_dtype(dtype) for dtype in numeric.dtypes):
        raise ValueError("Non-numeric values detected in numeric fields")
    if not np.isfinite(numeric.to_numpy()).all():
        raise ValueError("Non-finite values detected in numeric fields")

    data["date"] = pd.to_datetime(data["date"], errors="raise")
    if data.duplicated(["country", "date"]).any():
        raise ValueError("Duplicate country-month rows detected")

    if not (data["date"].dt.day == 1).all():
        raise ValueError("All dates must be month-start dates")
    if not (data["year"] == data["date"].dt.year).all():
        raise ValueError("The year column does not agree with date")
    if not (data["month"] == data["date"].dt.month).all():
        raise ValueError("The month column does not agree with date")

    country_count = int(data["country"].nunique())
    if country_count != EXPECTED_COUNTRIES:
        raise ValueError(
            f"Expected {EXPECTED_COUNTRIES} countries, found {country_count}"
        )

    expected_index = pd.date_range(START_DATE, END_DATE, freq="MS")
    month_counts = data.groupby("country")["date"].nunique()
    if not (month_counts == EXPECTED_MONTHS).all():
        raise ValueError("At least one country does not have all 168 months")
    for country, group in data.groupby("country"):
        observed = pd.DatetimeIndex(group["date"].sort_values())
        if not observed.equals(expected_index):
            raise ValueError(f"Country panel is incomplete or misaligned: {country}")

    count_columns = EVENT_COLUMNS + AUXILIARY_COLUMNS + TOTAL_COLUMNS
    if (data[count_columns] < 0).any().any():
        raise ValueError("Negative values detected in count columns")
    if (data[count_columns] % 1 != 0).any().any():
        raise ValueError("Non-integer values detected in count columns")

    if not data["total_articles"].equals(data["total_from_source"]):
        raise ValueError("total_articles and total_from_source differ")

    all_label_columns = EVENT_COLUMNS + AUXILIARY_COLUMNS
    label_total = data[all_label_columns].sum(axis=1)
    if not label_total.equals(data["total_label_events"]):
        raise ValueError("Raw label columns do not sum to total_label_events")

    denominator = data["total_local_docs"]
    if (denominator <= 0).any():
        raise ValueError("total_local_docs must be positive in every row")
    if (data["total_articles"] > denominator).any():
        raise ValueError("Environmental article count exceeds local-document denominator")
    if ((data["total_label_events"] < data["total_articles"]) |
            (data["total_label_events"] > 2 * data["total_articles"])).any():
        raise ValueError("Label totals fall outside one to two labels per included article")
    for column in all_label_columns:
        normalized = f"{column}Norm"
        if normalized not in data.columns:
            raise ValueError(f"Missing normalized column: {normalized}")
        difference = (data[normalized] - data[column] / denominator).abs()
        if difference.max() > 1e-9:
            raise ValueError(f"Normalized values do not reconcile for {column}")

        for suffix in ("NormShock", "NormShockCountGt3"):
            derived = f"{column}{suffix}"
            if derived not in data.columns:
                raise ValueError(f"Missing indicator column: {derived}")
            if not set(data[derived].unique()).issubset({0, 1}):
                raise ValueError(f"Non-binary values detected in {derived}")

    summary = {
        "data_file": path.name,
        "sha256": sha256(path),
        "rows": int(len(data)),
        "columns": int(len(data.columns)),
        "countries": country_count,
        "months_per_country": EXPECTED_MONTHS,
        "start_month": START_DATE.strftime("%Y-%m"),
        "end_month": END_DATE.strftime("%Y-%m"),
        "duplicate_country_months": 0,
        "missing_cells": 0,
        "minimum_total_local_docs": int(denominator.min()),
        "maximum_total_local_docs": int(denominator.max()),
        "totals": {column: int(data[column].sum()) for column in TOTAL_COLUMNS},
        "totals_note": "Summed country-month contributions, not unique global documents; international reports may contribute to multiple countries.",
        "checks": {
            "exact_schema_and_country_names": "pass",
            "finite_numeric_fields": "pass",
            "balanced_panel": "pass",
            "date_year_month_alignment": "pass",
            "nonnegative_integer_counts": "pass",
            "article_and_label_bounds": "pass",
            "label_total_reconciliation": "pass",
            "normalization_reconciliation": "pass",
            "binary_surge_indicators": "pass",
        },
        "validation_scope": "Structural and arithmetic checks only; these do not establish source-collection completeness or classifier accuracy.",
    }
    return data, summary


def build_coverage(data: pd.DataFrame, group: str) -> pd.DataFrame:
    """Summarize the observed release; zero labels are not absent source coverage."""
    return data.groupby(group, sort=True).agg(
        rows=("date", "size"),
        first_month=("date", "min"),
        last_month=("date", "max"),
        environmental_articles=("total_articles", "sum"),
        assigned_labels=("total_label_events", "sum"),
        locally_relevant_documents=("total_local_docs", "sum"),
        minimum_monthly_local_documents=("total_local_docs", "min"),
        months_with_zero_environmental_articles=("total_articles", lambda x: int((x == 0).sum())),
    ).reset_index()


def build_indicator_diagnostics(data: pd.DataFrame) -> pd.DataFrame:
    """Expose departures from the literal suffix interpretation without changing data."""
    output = []
    for label in EVENT_COLUMNS + AUXILIARY_COLUMNS:
        expected = (data[f"{label}NormShock"] == 1) & (data[label] > 3)
        mismatch = data[f"{label}NormShockCountGt3"] != expected.astype(int)
        for _, row in data.loc[mismatch].iterrows():
            output.append({
                "country": row["country"], "date": row["date"].strftime("%Y-%m-%d"),
                "label": label, "raw_count": int(row[label]),
                "stored_shock": int(row[f"{label}NormShock"]),
                "stored_screened_shock": int(row[f"{label}NormShockCountGt3"]),
                "shock_and_raw_count_gt3": int(expected.loc[row.name]),
            })
    columns = ["country", "date", "label", "raw_count", "stored_shock",
               "stored_screened_shock", "shock_and_raw_count_gt3"]
    return pd.DataFrame(output, columns=columns).sort_values(["country", "date", "label"])


def build_event_distribution(data: pd.DataFrame) -> pd.DataFrame:
    counts = data[EVENT_COLUMNS].sum().astype("int64")
    violence = (
        counts.pop("lethal environmental violence")
        + counts.pop("nonlethal environmental violence")
    )
    counts.loc["environmental violence"] = violence

    output = (
        counts.rename_axis("event")
        .reset_index(name="count")
        .sort_values(["count", "event"], ascending=[False, True])
        .reset_index(drop=True)
    )
    output["percentage"] = output["count"] / output["count"].sum()
    if len(output) != 16:
        raise ValueError(f"Expected 16 pooled event categories, found {len(output)}")
    return output


def format_event_label(label: str) -> str:
    return label.removeprefix("environmental ").capitalize()


def plot_event_distribution(distribution: pd.DataFrame, path: Path) -> None:
    plot_data = distribution.iloc[::-1].copy()
    colors = ["#8FA7BD"] * len(plot_data)
    colors[-1] = "#1B365D"

    fig, axis = plt.subplots(figsize=(9, 6.5))
    bars = axis.barh(
        plot_data["event"].map(format_event_label),
        plot_data["percentage"],
        color=colors,
    )
    axis.set_title("Distribution of MLEED environmental event labels", loc="left")
    axis.set_xlabel("Share of labels in the 16-category taxonomy")
    axis.xaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.tick_params(axis="y", length=0)
    axis.grid(axis="x", color="#E6E8EB", linewidth=0.7)
    axis.set_axisbelow(True)

    maximum = float(plot_data["percentage"].max())
    axis.set_xlim(0, maximum * 1.18)
    for bar, percentage in zip(bars, plot_data["percentage"]):
        axis.text(
            bar.get_width() + maximum * 0.012,
            bar.get_y() + bar.get_height() / 2,
            f"{percentage:.1%}",
            va="center",
            fontsize=8,
        )

    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    data, quality_summary = load_and_validate(args.data)
    diagnostics = build_indicator_diagnostics(data)
    quality_summary["indicator_diagnostic"] = {
        "comparison": "NormShockCountGt3 versus (NormShock == 1 and raw_count > 3)",
        "mismatching_cells": int(len(diagnostics)),
        "affected_label_series": int(diagnostics["label"].nunique()),
        "status": "unresolved" if len(diagnostics) else "consistent_with_comparison",
        "interpretation": "A diagnostic comparison, not a verified reconstruction of the production algorithm. Stored indicators are unchanged.",
    }
    print(json.dumps(quality_summary, indent=2))

    if args.validate_only:
        return

    args.outputs.mkdir(parents=True, exist_ok=True)
    args.figures.mkdir(parents=True, exist_ok=True)

    distribution = build_event_distribution(data)
    distribution.to_csv(args.outputs / "event_distribution.csv", index=False)
    build_coverage(data, "country").to_csv(args.outputs / "country_coverage.csv", index=False, date_format="%Y-%m-%d")
    build_coverage(data, "year").to_csv(args.outputs / "year_coverage.csv", index=False, date_format="%Y-%m-%d")
    diagnostics.to_csv(args.outputs / "indicator_diagnostics.csv", index=False)
    with (args.outputs / "data_quality_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(quality_summary, handle, indent=2)
        handle.write("\n")
    plot_event_distribution(distribution, args.figures / "event_distribution.png")

    print(f"Wrote {args.outputs / 'event_distribution.csv'}")
    print(f"Wrote {args.outputs / 'data_quality_summary.json'}")
    print(f"Wrote {args.figures / 'event_distribution.png'}")


if __name__ == "__main__":
    main()
