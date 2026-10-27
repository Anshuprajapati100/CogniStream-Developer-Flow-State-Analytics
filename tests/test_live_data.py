import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

import src.live_data as live_data


class TestLiveDataIntegration(unittest.TestCase):

    def setUp(self):
        self.session = {
            "session_id": "MAN001",
            "developer_id": "DEV005",
            "session_date": "2026-10-27",
            "session_duration_min": 60,
            "coding_time_min": 40,
            "idle_time_min": 10,
            "other_work_time_min": 10,
            "interruptions": 2,
            "context_switches": 3,
            "tasks_completed": 1,
            "focus_rating": 4,
            "cognitive_load_rating": 3,
            "data_source": "manual",
        }

        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.csv_path = Path(self.temp_dir.name) / "synthetic.csv"

    def write_synthetic_csv(self, session_id="S0001"):
        pd.DataFrame([{
            "session_id": session_id,
            "developer_id": "DEV001",
            "session_date": "2026-10-26",
            "data_source": "synthetic",
        }]).to_csv(self.csv_path, index=False)

    def test_empty_manual_sessions(self):
        result = live_data.prepare_manual_sessions([])

        self.assertTrue(result.empty)

    def test_manual_session_analytics(self):
        result = live_data.prepare_manual_sessions(
            [self.session]
        )

        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(
            result.iloc[0]["coding_activity_ratio"],
            66.6667,
            places=3,
        )
        self.assertAlmostEqual(
            result.iloc[0]["interruptions_per_hour"],
            2.0,
        )
        self.assertAlmostEqual(
            result.iloc[0]["context_switches_per_hour"],
            3.0,
        )
        self.assertIn("switches_per_hour", result.columns)
        self.assertAlmostEqual(
            result.iloc[0]["switches_per_hour"],
            result.iloc[0]["context_switches_per_hour"],
        )
        self.assertAlmostEqual(
            result.iloc[0]["flow_indicator_score"],
            69.0,
            places=1,
        )
        self.assertEqual(
            str(result.iloc[0]["flow_indicator_band"]),
            "Moderate",
        )
        self.assertEqual(
            str(result.iloc[0]["cognitive_load_band"]),
            "Moderate",
        )
        self.assertEqual(result.iloc[0]["data_source"], "manual")

    def test_combines_synthetic_and_manual_records(self):
        self.write_synthetic_csv()

        with (
            patch.object(live_data, "CSV_FILE", self.csv_path),
            patch.object(
                live_data, "get_sessions",
                return_value=[self.session],
            ),
        ):
            result = live_data.load_combined_data()

        self.assertEqual(len(result), 2)
        self.assertEqual(
            set(result["session_id"]),
            {"S0001", "MAN001"},
        )
        self.assertEqual(
            set(result["data_source"]),
            {"synthetic", "manual"},
        )
        self.assertTrue(
            pd.api.types.is_datetime64_any_dtype(
                result["session_date"]
            )
        )

    def test_loads_synthetic_records_without_manual_sessions(self):
        self.write_synthetic_csv()

        with (
            patch.object(live_data, "CSV_FILE", self.csv_path),
            patch.object(
                live_data, "get_sessions", return_value=[]
            ),
        ):
            result = live_data.load_combined_data()

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["session_id"], "S0001")

    def test_duplicate_session_ids_are_rejected(self):
        self.write_synthetic_csv(session_id="MAN001")

        with (
            patch.object(live_data, "CSV_FILE", self.csv_path),
            patch.object(
                live_data, "get_sessions",
                return_value=[self.session],
            ),
        ):
            with self.assertRaisesRegex(
                ValueError, "Duplicate session IDs"
            ):
                live_data.load_combined_data()

    def test_invalid_session_duration_is_rejected(self):
        invalid = self.session.copy()
        invalid["session_duration_min"] = 0
        invalid["coding_time_min"] = 0
        invalid["idle_time_min"] = 0
        invalid["other_work_time_min"] = 0

        with self.assertRaisesRegex(
            ValueError, "Session duration must be positive"
        ):
            live_data.prepare_manual_sessions([invalid])

    def test_inconsistent_session_times_are_rejected(self):
        invalid = self.session.copy()
        invalid["coding_time_min"] = 45

        with self.assertRaisesRegex(
            ValueError, "Session time components do not match"
        ):
            live_data.prepare_manual_sessions([invalid])

    def test_missing_synthetic_csv_is_rejected(self):
        missing_csv = Path(self.temp_dir.name) / "missing.csv"

        with (
            patch.object(live_data, "CSV_FILE", missing_csv),
            patch.object(
                live_data, "get_sessions", return_value=[]
            ),
        ):
            with self.assertRaisesRegex(
                FileNotFoundError, "Run python src/cognitive_load.py first"
            ):
                live_data.load_combined_data()


if __name__ == "__main__":
    unittest.main()
