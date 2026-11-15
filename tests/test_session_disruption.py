import unittest
import pandas as pd

from src.dashboard_filters import calculate_session_disruption_analysis


class TestSessionDisruptionAnalysis(unittest.TestCase):

    def setUp(self):
        self.data = pd.DataFrame({
            "session_duration_min": [60, 60, 60, 60, 60],
            "interruptions": [1, 2, 3, 4, 5],
            "context_switches": [2, 4, 6, 8, 10],
            "focus_rating": [5, 4, 3, 2, 1],
            "cognitive_load_rating": [1, 2, 3, 4, 5],
            "flow_indicator_score": [80, 70, 60, 50, 40],
        })

    def test_correct_bands_and_aggregates(self):
        result = calculate_session_disruption_analysis(
            self.data, low_threshold=2, high_threshold=4
        )
        self.assertEqual(
            result["disruption_band"].tolist(),
            ["Low", "Moderate", "High"],
        )
        self.assertEqual(result["session_count"].tolist(), [2, 2, 1])
        self.assertAlmostEqual(
            result.loc[0, "average_interruptions_per_hour"], 1.5
        )
        self.assertAlmostEqual(
            result.loc[1, "average_context_switches_per_hour"], 7
        )
        self.assertAlmostEqual(
            result.loc[2, "average_focus_rating"], 1
        )

    def test_threshold_boundaries(self):
        data = self.data.iloc[:3].copy()
        data["interruptions"] = [2, 3, 4]
        result = calculate_session_disruption_analysis(
            data, low_threshold=2, high_threshold=3
        )
        self.assertEqual(result["session_count"].tolist(), [1, 1, 1])

    def test_empty_dataframe(self):
        result = calculate_session_disruption_analysis(
            self.data.iloc[0:0]
        )
        self.assertEqual(len(result), 0)
        self.assertEqual(len(result.columns), 7)

    def test_missing_column(self):
        data = self.data.drop(columns=["focus_rating"])
        with self.assertRaisesRegex(ValueError, "Missing required columns"):
            calculate_session_disruption_analysis(data)

    def test_invalid_rows_are_excluded(self):
        data = self.data.copy()
        data["interruptions"] = data["interruptions"].astype(object)
        data["context_switches"] = data["context_switches"].astype(object)
        data.loc[0, "session_duration_min"] = 0
        data.loc[1, "interruptions"] = "invalid"
        data.loc[2, "context_switches"] = float("inf")
        data.loc[3, "interruptions"] = -1
        result = calculate_session_disruption_analysis(
            data, low_threshold=2, high_threshold=4
        )
        self.assertEqual(result["session_count"].sum(), 1)

    def test_invalid_thresholds(self):
        with self.assertRaisesRegex(ValueError, "Thresholds must be finite"):
            calculate_session_disruption_analysis(
                self.data, low_threshold=4, high_threshold=2
            )
        with self.assertRaisesRegex(ValueError, "Thresholds must be finite"):
            calculate_session_disruption_analysis(
                self.data, low_threshold=float("inf"), high_threshold=4
            )

    def test_original_dataframe_is_not_modified(self):
        original = self.data.copy(deep=True)
        calculate_session_disruption_analysis(
            self.data, low_threshold=2, high_threshold=4
        )
        pd.testing.assert_frame_equal(self.data, original)


if __name__ == "__main__":
    unittest.main()
