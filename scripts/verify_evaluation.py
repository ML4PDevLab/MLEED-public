#!/usr/bin/env python3
"""Recalculate reported classifier metrics from the deposited aggregate matrices."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "validation" / "classification"
OUTPUT = ROOT / "outputs" / "evaluation_verification.json"


def table(path):
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        return header[1:], {row[0]: [float(x) for x in row[1:]] for row in reader}


def close(observed, expected, context):
    if not math.isclose(observed, expected, abs_tol=1e-10, rel_tol=1e-10):
        raise ValueError(f"{context}: {observed} differs from {expected}")


def verify(mode):
    suffix = f"{mode}_BINARY_THEN_EVENTS.csv"
    labels, matrix = table(DIRECTORY / f"confusion_matrix_raw_{suffix}")
    norm_labels, normalized = table(DIRECTORY / f"confusion_matrix_normalized_{suffix}")
    report_columns, report = table(DIRECTORY / f"classification_report_{suffix}")
    if list(matrix) != labels or list(normalized) != labels or norm_labels != labels:
        raise ValueError("Matrix row/column label alignment differs")
    if report_columns != ["precision", "recall", "f1-score", "support"]:
        raise ValueError("Unexpected classification report fields")
    supports, scores = [], []
    for i, label in enumerate(labels):
        row = matrix[label]
        if len(row) != len(labels) or any(x < 0 or not x.is_integer() for x in row):
            raise ValueError(f"Invalid raw counts for {label}")
        support = sum(row)
        predicted = sum(matrix[x][i] for x in labels)
        correct = row[i]
        precision = correct / predicted if predicted else 0.0
        recall = correct / support if support else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        values = [precision, recall, f1, support]
        for field, observed, expected in zip(report_columns, report[label], values):
            close(observed, expected, f"{mode}/{label}/{field}")
        for j, value in enumerate(row):
            close(normalized[label][j], value / support if support else 0, f"{mode}/{label}/normalized")
        supports.append(support)
        scores.append(values[:3])
    n = sum(supports)
    correct = sum(matrix[label][i] for i, label in enumerate(labels))
    accuracy = correct / n
    # The original report repeats scalar accuracy across four columns, including support.
    for value in report["accuracy"]:
        close(value, accuracy, f"{mode}/accuracy")
    aggregate = {}
    for kind in ["macro avg", "weighted avg"]:
        weights = [1.0] * len(labels) if kind == "macro avg" else supports
        values = [sum(row[j] * weight for row, weight in zip(scores, weights)) / sum(weights) for j in range(3)] + [n]
        for field, observed, expected in zip(report_columns, report[kind], values):
            close(observed, expected, f"{mode}/{kind}/{field}")
        aggregate[kind] = dict(zip(report_columns, values))
    return {"cases": int(n), "correct": int(correct), "accuracy": accuracy,
            "label_count": len(labels), **aggregate,
            "checks": "Raw matrices, row-normalized matrices, class metrics and averages reconcile."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify saved output without rewriting it")
    args = parser.parse_args()
    result = {
        "primary": verify("primary"),
        "primary_or_secondary": verify("primary_or_secondary"),
        "scope": "Arithmetic verification of archived aggregate evaluation reports. Does not verify training/test independence or model-version linkage to the public panel.",
        "primary_or_secondary_note": "Permissive top-two scoring; not standard single-prediction classification accuracy.",
    }
    with (ROOT / "validation/human_audit_summary.csv").open() as handle:
        human = {row["metric"]: int(row["count"]) for row in csv.DictReader(handle)}
    result["human_audit"] = {
        **human,
        "article_correct_fraction": human["correct_articles"] / human["reviewed_articles"],
        "selected_surges_valid_fraction": human["valid_surges"] / human["selected_surges"],
        "error_count_difference": human["reviewed_articles"] - human["correct_articles"] - human["event_error_flags"] - human["geographic_error_flags"],
        "scope": "Descriptive purposive surge audit with borderline cases counted correct; does not estimate population-wide accuracy.",
    }
    encoded = json.dumps(result, indent=2) + "\n"
    if args.check:
        if OUTPUT.read_text() != encoded:
            raise SystemExit("Saved evaluation verification differs from recalculated aggregates")
    else:
        OUTPUT.write_text(encoded)
    print(encoded, end="")


if __name__ == "__main__":
    main()
