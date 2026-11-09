import unittest
from datetime import date

import pandas as pd

from src.dashboard_filters import filter_sessions

from src.dashboard_filters import calculate_developer_metric_trends

class TestDeveloperMetricTrends(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            "session_date": pd.to_datetime([
                "2026-11-04",
                "2026-11-04",
                "2026-11-05",
                "2026-11-05",
                "2026-11-04",
            ]),
            "developer_id": [
                "DEV001",
                "DEV001",
                "DEV001",
                "DEV001",
                "DEV002",
            ],
            "flow_indicator_score": [60, 80, 70, 90, 75],
            "focus_rating": [3, 5, 4, 4, 3],
            "cognitive_load_rating": [2, 4, 3, 5, 3],
        })

    def test_calculates_daily_flow_averages(self):
        result = calculate_developer_metric_trends(
            self.df, "flow_indicator_score"
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(
            result["average_metric"].tolist(),
            [70.0, 80.0],
        )

    def test_calculates_focus_averages(self):
        result = calculate_developer_metric_trends(
            self.df, "focus_rating"
        )
        self.assertEqual(
            result["average_metric"].tolist(),
            [4.0, 4.0],
        )

    def test_calculates_cognitive_load_averages(self):
        result = calculate_developer_metric_trends(
            self.df, "cognitive_load_rating"
        )
        self.assertEqual(
            result["average_metric"].tolist(),
            [3.0, 4.0],
        )

    def test_excludes_developers_with_insufficient_days(self):
        result = calculate_developer_metric_trends(
            self.df, "flow_indicator_score"
        )
        self.assertNotIn(
            "DEV002",
            result["developer_id"].tolist(),
        )

    def test_empty_dataset(self):
        result = calculate_developer_metric_trends(
            self.df.iloc[0:0],
            "flow_indicator_score",
        )
        self.assertTrue(result.empty)

    def test_rejects_unsupported_metric(self):
        with self.assertRaises(ValueError):
            calculate_developer_metric_trends(
                self.df, "unknown_metric"
            )

    def test_rejects_missing_columns(self):
        with self.assertRaises(ValueError):
            calculate_developer_metric_trends(
                self.df.drop(columns=["focus_rating"]),
                "focus_rating",
            )

class TestDashboardFilters(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            "session_id": ["S001", "S002", "S003"],
            "developer_id": ["DEV001", "DEV002", "DEV001"],
            "session_date": pd.to_datetime([
                "2026-11-04",
                "2026-11-05",
                "2026-11-06",
            ]),
        })

    def test_filters_single_selected_date(self):
        result = filter_sessions(
            self.df, ["DEV001"], date(2026, 11, 6)
        )
        self.assertEqual(result["session_id"].tolist(), ["S003"])

    def test_filters_date_range(self):
        result = filter_sessions(
            self.df,
            ["DEV001", "DEV002"],
            (date(2026, 11, 4), date(2026, 11, 5)),
        )
        self.assertEqual(
            result["session_id"].tolist(), ["S001", "S002"]
        )

    def test_empty_developer_selection_returns_empty(self):
        result = filter_sessions(
            self.df,
            [],
            (date(2026, 11, 4), date(2026, 11, 6)),
        )
        self.assertTrue(result.empty)

    def test_filters_by_developer(self):
        result = filter_sessions(
            self.df,
            ["DEV001"],
            (date(2026, 11, 4), date(2026, 11, 6)),
        )
        self.assertEqual(
            result["session_id"].tolist(), ["S001", "S003"]
        )


if __name__ == "__main__":
    unittest.main()
