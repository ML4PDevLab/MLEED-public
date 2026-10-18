#!/usr/bin/env python3
"""Verify the current surge indicators from their pinned complete input window."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import urllib.request
import warnings

import numpy as np
import pandas as pd

from recovered_surge import PeakDetector, convert_to_training_data_2
from freeze_snapshot import SOURCE_RECORD, extract_bytes
from verify_evaluation import compare_saved


ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "data/mleed_country_month_2012_2025.csv"
PROVENANCE = ROOT / "validation/surge_provenance.json"
SUMMARY = ROOT / "outputs/surge_reconstruction_summary.json"
DEFAULT_SOURCE = ROOT / "analysis/full-mleed-source-20261013.csv"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_definitions(provenance: dict) -> None:
    text = (ROOT / "scripts/recovered_surge.py").read_text()
    parsed = ast.parse(text)
    for source in provenance["source_files"]:
        node = next(n for n in parsed.body if isinstance(n, (ast.ClassDef, ast.FunctionDef))
                    and n.name == source["retained_definition"])
        observed = hashlib.sha256(ast.get_source_segment(text, node).encode()).hexdigest()
        if observed != source["definition_sha256"]:
            raise ValueError("Recovered definition differs from the recorded upstream source")


def verify_indicators(data: pd.DataFrame, reference: pd.DataFrame) -> dict:
    labels = [c for c in reference.columns if c.endswith("Norm")]
    if data.duplicated(["country", "date"]).any():
        raise ValueError("Input contains duplicate country-month keys")
    detector = PeakDetector(12, 0.88, 1, 0.05, 0.2)
    result = {
        "source_rows": int(len(data)), "source_countries": int(data.country.nunique()),
        "source_start_month": str(data.date.min())[:7], "source_end_month": str(data.date.max())[:7],
        "source_missing_normalized_cells": int(data[labels].isna().sum().sum()),
        "release_rows": int(len(reference)), "release_countries": int(reference.country.nunique()),
        "release_missing_normalized_cells": int(reference[labels].isna().sum().sum()),
        "comparison_cells_per_family": 0,
        "NormShock_differences": 0, "NormShockCountGt3_differences": 0,
        "count_screen_rule_differences": 0,
        "stored_NormShock_positive_cells": 0, "stored_NormShockCountGt3_positive_cells": 0,
    }
    for country, group_reference in reference.groupby("country", sort=True):
        group = data.loc[data.country == country].sort_values("date")
        if not set(group_reference.date).issubset(set(group.date)):
            raise ValueError(f"Source does not contain the release months for {country}")
        overlap = group.date.isin(group_reference.date).to_numpy()
        historical = group.loc[overlap]
        expected = group_reference.set_index("date").loc[historical.date]
        for label in labels:
            # Retain later missing values to reproduce the published source's behavior.
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                _, _, predictions = convert_to_training_data_2(
                    group[label].to_numpy(), country, label, detector, None
                )
            predicted = np.asarray(predictions, dtype=int)[overlap]
            raw = historical[label[:-4]].to_numpy()
            screened = ((predicted == 1) & (raw > 3)).astype(int)
            stored = expected[label + "Shock"].to_numpy()
            stored_screen = expected[label + "ShockCountGt3"].to_numpy()
            result["NormShock_differences"] += int(np.count_nonzero(predicted != stored))
            result["NormShockCountGt3_differences"] += int(np.count_nonzero(screened != stored_screen))
            result["count_screen_rule_differences"] += int(np.count_nonzero(stored_screen != ((stored == 1) & (raw > 3))))
            result["stored_NormShock_positive_cells"] += int(stored.sum())
            result["stored_NormShockCountGt3_positive_cells"] += int(stored_screen.sum())
            result["comparison_cells_per_family"] += len(predicted)
    if result["comparison_cells_per_family"] != len(reference) * len(labels):
        raise ValueError("Indicator comparison did not cover every release row and label")
    if any(result[k] for k in ["NormShock_differences", "NormShockCountGt3_differences", "count_screen_rule_differences"]):
        raise ValueError(f"Current indicators do not reproduce: {result}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-csv", type=Path, default=DEFAULT_SOURCE,
                        help="Complete source CSV with the recorded checksum")
    parser.add_argument("--download-source", action="store_true",
                        help="Download the pinned public aggregate CSV if the source path is absent")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true", help="Verify against the saved result")
    modes.add_argument("--write-summary", action="store_true", help="Write the verified result only")
    args = parser.parse_args()
    provenance = json.loads(PROVENANCE.read_text())
    verify_definitions(provenance)
    source = provenance["full_window_source"]
    if args.download_source and not args.source_csv.exists():
        args.source_csv.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(source["csv_url"], timeout=60) as response:
            contents = response.read()
        if hashlib.sha256(contents).hexdigest() != source["csv_sha256"]:
            raise SystemExit("Downloaded source checksum differs; no file written")
        with args.source_csv.open("xb") as handle:
            handle.write(contents)
    if not args.source_csv.is_file():
        raise SystemExit("Complete source CSV is required. Use --download-source or --source-csv PATH.")
    if digest(args.source_csv) != source["csv_sha256"]:
        raise ValueError("Source checksum differs from the pinned October 2026 export")
    if digest(FROZEN) != provenance["frozen_data_sha256"]:
        raise ValueError("Release checksum differs from the recorded snapshot")
    if extract_bytes(args.source_csv, json.loads(SOURCE_RECORD.read_text())) != FROZEN.read_bytes():
        raise ValueError("Release is not the recorded historical extraction of the source")
    result = {
        "code_revision": provenance["code_revision"], "mode": provenance["mode"],
        "parameters": provenance["parameters"], "release_data_sha256": digest(FROZEN),
        "full_window_source_sha256": digest(args.source_csv),
        "source_revision": source["revision"],
        **verify_indicators(pd.read_csv(args.source_csv), pd.read_csv(FROZEN)),
        "status": "exact_reproduction",
        "window_note": "The complete source window is supplied before selecting the 2012–2025 release months. Later missing normalized values are retained; none occur in the release.",
    }
    if args.write_summary:
        SUMMARY.write_text(json.dumps(result, indent=2) + "\n")
    if args.check:
        compare_saved(json.loads(SUMMARY.read_text()), result, "surge_reproduction")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
