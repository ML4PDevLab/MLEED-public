#!/usr/bin/env python3
"""Check that consequential data corruption fails validation and pooling reconciles."""

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from build_overview import DEFAULT_DATA, EVENT_COLUMNS, load_and_validate
from export_long import make_long


class ReleaseValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, _ = load_and_validate(DEFAULT_DATA)

    def rejected(self, frame, message):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.csv"
            frame.to_csv(path, index=False, date_format="%Y-%m-%d")
            with self.assertRaisesRegex(ValueError, message):
                load_and_validate(path)

    def test_duplicate_country_month_rejected(self):
        frame = self.data.copy()
        frame.iloc[1] = frame.iloc[0]
        self.rejected(frame, "Duplicate country-month")

    def test_missing_country_month_rejected(self):
        self.rejected(self.data.iloc[1:], "all 168 months")

    def test_changed_country_name_rejected(self):
        frame = self.data.copy()
        frame.loc[0, "country"] = "Unregistered country"
        self.rejected(frame, "Country names")

    def test_fractional_count_rejected(self):
        frame = self.data.copy()
        frame[EVENT_COLUMNS[0]] = frame[EVENT_COLUMNS[0]].astype(float)
        frame.loc[0, EVENT_COLUMNS[0]] = 0.5
        self.rejected(frame, "Non-integer")

    def test_wrong_normalization_rejected(self):
        frame = self.data.copy()
        frame.loc[0, EVENT_COLUMNS[0] + "Norm"] += 0.001
        self.rejected(frame, "Normalized values")

    def test_infinite_normalization_rejected(self):
        frame = self.data.copy()
        frame.loc[0, EVENT_COLUMNS[0] + "Norm"] = float("inf")
        self.rejected(frame, "Non-finite")

    def test_nonbinary_indicator_rejected(self):
        frame = self.data.copy()
        frame.loc[0, EVENT_COLUMNS[0] + "NormShock"] = 2
        self.rejected(frame, "Non-binary")

    def test_long_export_preserves_counts_and_rates(self):
        long = make_long(self.data)
        self.assertEqual(len(long), len(self.data) * 16)
        self.assertFalse(long.duplicated(["country", "date", "category"]).any())
        expected = self.data.set_index(["country", "date"])[EVENT_COLUMNS].sum(axis=1).sort_index()
        actual = long.groupby(["country", "date"])["label_count"].sum().sort_index()
        pd.testing.assert_series_equal(actual, expected, check_names=False)
        violence = long[long["category"] == "environmental violence"]["label_count"].sum()
        self.assertEqual(violence, self.data[["lethal environmental violence", "nonlethal environmental violence"]].sum().sum())
        self.assertTrue((long["labels_per_10000_documents"] == long["label_count"] / long["total_local_docs"] * 10_000).all())


if __name__ == "__main__":
    unittest.main()
