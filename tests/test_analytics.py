import unittest

import pandas as pd

from src.analytics import calculate_metrics


class TestAnalyticsValidation(unittest.TestCase):

    def setUp(self):
        self.data = pd.DataFrame({
            "session_duration_min": [60, 120],
            "coding_time_min": [30, 90],
            "interruptions": [2, 4],
            "context_switches": [3, 6],
        })

    def test_calculates_activity_metrics(self):
        result = calculate_metrics(self.data)

        self.assertAlmostEqual(
            result.loc[0, "coding_activity_ratio"], 50.0
        )
        self.assertAlmostEqual(
            result.loc[0, "interruptions_per_hour"], 2.0
        )
        self.assertAlmostEqual(
            result.loc[0, "context_switches_per_hour"], 3.0
        )

    def test_rejects_empty_dataset(self):
        with self.assertRaisesRegex(ValueError, "at least one session"):
            calculate_metrics(self.data.iloc[0:0])

    def test_rejects_missing_column(self):
        invalid = self.data.drop(columns=["interruptions"])

        with self.assertRaisesRegex(ValueError, "Missing required columns"):
            calculate_metrics(invalid)

    def test_rejects_zero_duration(self):
        invalid = self.data.copy()
        invalid.loc[0, "session_duration_min"] = 0

        with self.assertRaisesRegex(ValueError, "duration must be positive"):
            calculate_metrics(invalid)

    def test_rejects_non_numeric_values(self):
        invalid = self.data.copy()
        invalid["coding_time_min"] = invalid["coding_time_min"].astype(object)
        invalid.loc[0, "coding_time_min"] = "invalid"

        with self.assertRaisesRegex(ValueError, "finite numeric values"):
            calculate_metrics(invalid)

    def test_rejects_missing_numeric_values(self):
        invalid = self.data.copy()
        invalid.loc[0, "interruptions"] = float("nan")

        with self.assertRaisesRegex(ValueError, "finite numeric values"):
            calculate_metrics(invalid)

    def test_rejects_infinite_values(self):
        invalid = self.data.copy()
        invalid["context_switches"] = (
            invalid["context_switches"].astype(float)
        )
        invalid.loc[0, "context_switches"] = float("inf")

        with self.assertRaisesRegex(ValueError, "finite numeric values"):
            calculate_metrics(invalid)

    def test_rejects_coding_time_exceeding_duration(self):
        invalid = self.data.copy()
        invalid.loc[0, "coding_time_min"] = 61

        with self.assertRaisesRegex(ValueError, "Coding time"):
            calculate_metrics(invalid)

    def test_rejects_negative_event_counts(self):
        invalid = self.data.copy()
        invalid.loc[0, "interruptions"] = -1

        with self.assertRaisesRegex(ValueError, "interruptions"):
            calculate_metrics(invalid)
    
    def test_rejects_fractional_event_counts(self):
        for column in ["interruptions", "context_switches"]:
            with self.subTest(column=column):
                invalid = self.data.copy()
                invalid[column] = invalid[column].astype(float)
                invalid.loc[0, column] = 1.5

                with self.assertRaisesRegex(
                    ValueError,
                    "whole-number counts"
                ):
                    calculate_metrics(invalid)

    def test_accepts_whole_number_event_counts(self):
        valid = self.data.copy()
        valid["interruptions"] = [2.0, 4.0]
        valid["context_switches"] = [3.0, 6.0]

        result = calculate_metrics(valid)

        self.assertEqual(len(result), 2)

if __name__ == "__main__":
    unittest.main()
