import unittest

import pandas as pd

from src.insights import generate_insights


class TestSmartInsights(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            "session_duration_min": [60, 120],
            "coding_time_min": [45, 90],
            "interruptions": [2, 4],
            "context_switches": [3, 6],
            "focus_rating": [4, 3],
            "cognitive_load_rating": [2, 4],
        })

    def test_six_insights_generated(self):
        result = generate_insights(self.df)
        self.assertEqual(len(result), 6)

    def test_empty_dataset(self):
        result = generate_insights(self.df.iloc[0:0])
        self.assertEqual(
            result,
            ["No data available for analysis."]
        )

    def test_missing_column(self):
        invalid = self.df.drop(columns=["focus_rating"])
        with self.assertRaises(ValueError):
            generate_insights(invalid)

    def test_missing_value(self):
        invalid = self.df.copy()
        invalid.loc[0, "coding_time_min"] = None
        with self.assertRaises(ValueError):
            generate_insights(invalid)

    def test_zero_session_duration(self):
        invalid = self.df.copy()
        invalid.loc[0, "session_duration_min"] = 0
        with self.assertRaises(ValueError):
            generate_insights(invalid)

    def test_negative_coding_time(self):
        invalid = self.df.copy()
        invalid.loc[0, "coding_time_min"] = -10
        with self.assertRaises(ValueError):
            generate_insights(invalid)

    def test_coding_time_exceeds_duration(self):
        invalid = self.df.copy()
        invalid.loc[0, "coding_time_min"] = 100
        with self.assertRaises(ValueError):
            generate_insights(invalid)


if __name__ == "__main__":
    unittest.main()
