#!/usr/bin/env python3
"""Extract the pinned 71-country historical snapshot without changing values."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_RECORD = ROOT / "metadata/source_snapshot_71_20261018.json"
TARGET = ROOT / "data/mleed_country_month_2012_2025.csv"


def extract_bytes(source: Path, record: dict) -> bytes:
    """Retain numeric tokens and field order; sort the chosen country-month rows."""
    if hashlib.sha256(source.read_bytes()).hexdigest() != record["source"]["csv_sha256"]:
        raise ValueError("Source checksum differs from the pinned October 2026 export")
    data = pd.read_csv(source, dtype=str, keep_default_na=False)
    window = record["extraction"]
    data = data.loc[data.date.between(window["start_date"], window["end_date"])].copy()
    if data.duplicated(["country", "date"]).any():
        raise ValueError("Duplicate country-month keys in source")
    if len(data) != 11928 or data.country.nunique() != 71 or len(data.columns) != 88:
        raise ValueError("Source does not contain the expected 71-country historical panel")
    data = data.sort_values(["country", "date"])
    encoded = data.to_csv(index=False, lineterminator="\n").encode("utf-8")
    if hashlib.sha256(encoded).hexdigest() != window["data_sha256"]:
        raise ValueError("Extracted bytes differ from the recorded historical snapshot")
    return encoded


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-csv", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Compare extraction with the current CSV")
    mode.add_argument("--write", action="store_true", help="Write the verified historical snapshot")
    args = parser.parse_args()
    record = json.loads(SOURCE_RECORD.read_text())
    encoded = extract_bytes(args.source_csv, record)
    if args.check:
        if TARGET.read_bytes() != encoded:
            raise SystemExit("Canonical CSV differs from the pinned historical extraction")
        print("Verified all 11,928 rows and 88 columns against the pinned source bytes.")
    else:
        if TARGET.exists():
            allowed = {record["previous_snapshot"]["data_sha256"], record["extraction"]["data_sha256"]}
            if hashlib.sha256(TARGET.read_bytes()).hexdigest() not in allowed:
                raise SystemExit("Refusing to replace an unrecognized canonical CSV")
        TARGET.write_bytes(encoded)
        print(f"Wrote {TARGET}")


if __name__ == "__main__":
    main()
