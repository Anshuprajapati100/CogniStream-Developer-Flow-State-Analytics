import unittest
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_FILE = PROJECT_ROOT / "data/raw/developer_sessions_synthetic.csv"

CLEAN_FILE = PROJECT_ROOT / "data/processed/cleaned_developer_sessions.csv"

FLOW_FILE = PROJECT_ROOT / "reports/flow_cognitive_analysis.csv"


class TestCogniStreamPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.raw = pd.read_csv(RAW_FILE)
        cls.clean = pd.read_csv(CLEAN_FILE)
        cls.flow = pd.read_csv(FLOW_FILE)

    def test_raw_dataset_not_empty(self):
        self.assertFalse(self.raw.empty)

    def test_clean_dataset_not_empty(self):
        self.assertFalse(self.clean.empty)

    def test_session_ids_unique(self):
        self.assertTrue(self.clean["session_id"].is_unique)

    def test_no_missing_values(self):
        self.assertFalse(self.clean.isnull().any().any())

    def test_positive_session_duration(self):
        self.assertTrue(
            (self.clean["session_duration_min"] > 0).all()
        )

    def test_nonnegative_activity_values(self):
        columns = [
            "coding_time_min",
            "idle_time_min",
            "other_work_time_min",
            "interruptions",
            "context_switches",
            "tasks_completed",
        ]

        self.assertTrue(
            (self.clean[columns] >= 0).all().all()
        )

    def test_session_time_consistency(self):
        total = (
            self.clean["coding_time_min"]
            + self.clean["idle_time_min"]
            + self.clean["other_work_time_min"]
        )

        self.assertTrue(
            (total == self.clean["session_duration_min"]).all()
        )

    def test_focus_rating_range(self):
        self.assertTrue(
            self.clean["focus_rating"].between(1, 5).all()
        )

    def test_cognitive_load_rating_range(self):
        self.assertTrue(
            self.clean["cognitive_load_rating"].between(1, 5).all()
        )

    def test_flow_indicator_range(self):
        self.assertTrue(
            self.flow["flow_indicator_score"].between(0, 100).all()
        )

    def test_flow_indicator_bands(self):
        allowed = {"Low", "Moderate", "High"}

        self.assertTrue(
            set(self.flow["flow_indicator_band"]).issubset(allowed)
        )

    def test_cognitive_load_bands(self):
        allowed = {"Low", "Moderate", "High"}

        self.assertTrue(
            set(self.flow["cognitive_load_band"]).issubset(allowed)
        )

    def test_session_counts_match(self):
        self.assertEqual(len(self.raw), len(self.clean))
        self.assertEqual(len(self.clean), len(self.flow))

    def test_synthetic_data_label(self):
        self.assertTrue(
            (self.raw["data_source"] == "synthetic").all()
        )


if __name__ == "__main__":
    unittest.main()
