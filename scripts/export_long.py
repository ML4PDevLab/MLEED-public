#!/usr/bin/env python3
"""Export the public panel as country-month-category records, pooling violence."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from build_overview import DEFAULT_DATA, EVENT_COLUMNS, load_and_validate


def make_long(data: pd.DataFrame) -> pd.DataFrame:
    """Keep 16 substantive categories; rates are label counts per 10,000 documents."""
    counts = data[["country", "date", "total_local_docs", *EVENT_COLUMNS]].copy()
    counts["environmental violence"] = (
        counts.pop("lethal environmental violence")
        + counts.pop("nonlethal environmental violence")
    )
    long = counts.melt(
        id_vars=["country", "date", "total_local_docs"],
        var_name="category", value_name="label_count",
    )
    long["labels_per_10000_documents"] = long["label_count"] / long["total_local_docs"] * 10_000
    return long.sort_values(["country", "date", "category"]).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output", type=Path, required=True, help="New CSV path, outside data/")
    args = parser.parse_args()
    if args.output.resolve() == args.data.resolve() or args.output.exists():
        raise SystemExit("Choose a new output path; this script does not overwrite existing files.")
    if args.output.resolve().is_relative_to(DEFAULT_DATA.parent.resolve()):
        raise SystemExit("Write derived analysis files outside the canonical data/ directory.")
    data, _ = load_and_validate(args.data)
    output = make_long(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False, date_format="%Y-%m-%d")
    print(f"Wrote {len(output):,} country-month-category records to {args.output}")


if __name__ == "__main__":
    main()
