#!/usr/bin/env python3
"""Compare a recovered surge routine with frozen indicators; never replace data."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import warnings

import numpy as np
import pandas as pd

from recovered_surge import PeakDetector, convert_to_training_data_2
from verify_evaluation import compare_saved


ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "data/mleed_country_month_2012_2025.csv"
PROVENANCE = ROOT / "validation/surge_provenance.json"
SUMMARY = ROOT / "outputs/surge_reconstruction_summary.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_definitions(provenance):
    text = (ROOT / "scripts/recovered_surge.py").read_text()
    parsed = ast.parse(text)
    for source in provenance["source_files"]:
        node = next(n for n in parsed.body if isinstance(n, (ast.ClassDef, ast.FunctionDef))
                    and n.name == source["retained_definition"])
        observed = hashlib.sha256(ast.get_source_segment(text, node).encode()).hexdigest()
        if observed != source["definition_sha256"]:
            raise ValueError("Recovered definition differs from the recorded upstream source")


def compare_input(data, frozen):
    labels = [c for c in frozen.columns if c.endswith("Norm")]
    if data.duplicated(["country", "date"]).any():
        raise ValueError("Input contains duplicate country-month keys")
    detector = PeakDetector(12, 0.88, 1, 0.05, 0.2)
    result = {
        "source_rows": int(len(data)),
        "source_countries": int(data.country.nunique()),
        "source_start_month": str(data.date.min())[:7],
        "source_end_month": str(data.date.max())[:7],
        "source_missing_normalized_cells": int(data[labels].isna().sum().sum()),
        "comparison_cells": 0,
        "candidate_vs_own_source_shock_differences": 0,
        "candidate_vs_own_source_screen_differences": 0,
        "candidate_vs_frozen_shock_differences": 0,
        "candidate_vs_frozen_screen_differences": 0,
        "own_source_vs_frozen_shock_differences": 0,
        "own_source_vs_frozen_screen_differences": 0,
        "own_source_vs_frozen_raw_count_differences": 0,
        "own_source_vs_frozen_normalized_differences": 0,
        "candidate_positive_shocks": 0,
        "stored_frozen_positive_shocks": 0,
    }
    for country, reference in frozen.groupby("country", sort=True):
        group = data.loc[data.country == country].sort_values("date")
        if not set(reference.date).issubset(set(group.date)):
            raise ValueError(f"Input does not contain the frozen comparison months for {country}")
        overlap = group.date.isin(reference.date).to_numpy()
        historical = group.loc[overlap]
        reference = reference.set_index("date").loc[historical.date]
        for label in labels:
            # NaNs are deliberately retained to reproduce the source's numerical behavior.
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                _, _, predictions = convert_to_training_data_2(
                    group[label].to_numpy(), country, label, detector, None
                )
            candidate = np.asarray(predictions, dtype=int)[overlap]
            raw = historical[label[:-4]].to_numpy()
            screened = ((candidate == 1) & (raw > 3)).astype(int)
            source_shock = historical[label + "Shock"].to_numpy()
            source_screen = historical[label + "ShockCountGt3"].to_numpy()
            frozen_shock = reference[label + "Shock"].to_numpy()
            frozen_screen = reference[label + "ShockCountGt3"].to_numpy()
            for key, left, right in [
                ("candidate_vs_own_source_shock_differences", candidate, source_shock),
                ("candidate_vs_own_source_screen_differences", screened, source_screen),
                ("candidate_vs_frozen_shock_differences", candidate, frozen_shock),
                ("candidate_vs_frozen_screen_differences", screened, frozen_screen),
                ("own_source_vs_frozen_shock_differences", source_shock, frozen_shock),
                ("own_source_vs_frozen_screen_differences", source_screen, frozen_screen),
                ("own_source_vs_frozen_raw_count_differences", raw, reference[label[:-4]].to_numpy()),
            ]:
                result[key] += int(np.count_nonzero(left != right))
            close = np.isclose(historical[label].to_numpy(), reference[label].to_numpy(), rtol=0, atol=1e-12, equal_nan=True)
            result["own_source_vs_frozen_normalized_differences"] += int((~close).sum())
            result["candidate_positive_shocks"] += int(candidate.sum())
            result["stored_frozen_positive_shocks"] += int(frozen_shock.sum())
            result["comparison_cells"] += len(candidate)
    expected = len(frozen) * len(labels)
    if result["comparison_cells"] != expected:
        raise ValueError(f"Expected {expected} shared flag cells")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-csv", type=Path, action="append", default=[],
                        help="Optional full historical source CSV; must match a recorded checksum")
    parser.add_argument("--check", action="store_true", help="Check computed comparisons against saved summary")
    parser.add_argument("--write-summary", action="store_true", help="Refresh summary only; requires both recorded historical inputs")
    args = parser.parse_args()
    if args.check and args.write_summary:
        parser.error("Choose either --check or --write-summary")
    provenance = json.loads(PROVENANCE.read_text())
    verify_definitions(provenance)
    if digest(FROZEN) != provenance["frozen_data_sha256"]:
        raise ValueError("Frozen dataset checksum differs from the comparison record")
    frozen = pd.read_csv(FROZEN)
    result = {
        "code_revision": provenance["code_revision"],
        "mode": provenance["mode"],
        "parameters": provenance["parameters"],
        "frozen_input_sha256": digest(FROZEN),
        "frozen_input": compare_input(frozen, frozen),
        "full_window_comparisons": [],
    }
    known = {item["sha256"]: item for item in provenance["historical_input_candidates"]}
    seen = set()
    for path in args.source_csv:
        checksum = digest(path)
        if checksum not in known or checksum in seen:
            raise ValueError("Each historical CSV must match a distinct recorded source checksum")
        seen.add(checksum)
        source = known[checksum]
        comparison = {"revision": source["revision"], "source_file_sha256": checksum,
                      **compare_input(pd.read_csv(path), frozen)}
        result["full_window_comparisons"].append(comparison)
    result["full_window_comparisons"].sort(key=lambda item: item["revision"])
    if args.write_summary:
        if seen != set(known):
            raise ValueError("Both recorded historical inputs are required to refresh the complete summary")
        SUMMARY.write_text(json.dumps(result, indent=2) + "\n")
    if args.check:
        stored = json.loads(SUMMARY.read_text())
        for key in result.keys() - {"full_window_comparisons"}:
            compare_saved(stored[key], result[key], key)
        stored_sources = {item["revision"]: item for item in stored["full_window_comparisons"]}
        for comparison in result["full_window_comparisons"]:
            compare_saved(stored_sources[comparison["revision"]], comparison, comparison["revision"])
    print(json.dumps(result, indent=2))
    if args.check and not args.source_csv:
        print("Verified frozen-input comparison only; historical full-window checks require --source-csv inputs.")


if __name__ == "__main__":
    main()
