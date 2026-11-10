import unittest
from datetime import date

import pandas as pd

from src.dashboard_filters import filter_sessions

from src.dashboard_filters import calculate_developer_metric_trends
from src.dashboard_filters import calculate_developer_cohort_insights

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


class TestDeveloperCohortInsights(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            "developer_id": [
                "DEV001", "DEV001",
                "DEV002", "DEV002",
                "DEV003", "DEV003",
            ],
            "flow_indicator_score": [
                80, 80, 60, 60, 70, 70,
            ],
            "focus_rating": [
                5, 5, 3, 3, 4, 4,
            ],
            "cognitive_load_rating": [
                4, 4, 2, 2, 3, 3,
            ],
        })

    def test_calculates_developer_and_cohort_averages(self):
        result = calculate_developer_cohort_insights(self.df)

        dev001 = result.set_index("developer_id").loc["DEV001"]

        self.assertEqual(dev001["avg_flow"], 80.0)
        self.assertEqual(dev001["cohort_avg_flow"], 70.0)
        self.assertEqual(dev001["sessions"], 2)

    def test_classifies_developers_above_near_and_below_cohort(self):
        result = calculate_developer_cohort_insights(self.df)
        result = result.set_index("developer_id")

        self.assertEqual(
            result.loc["DEV001", "flow_comparison"],
            "Above cohort",
        )
        self.assertEqual(
            result.loc["DEV002", "flow_comparison"],
            "Below cohort",
        )
        self.assertEqual(
            result.loc["DEV003", "flow_comparison"],
            "Near cohort",
        )

    def test_handles_missing_metric_values(self):
        data = self.df.copy()
        data["focus_rating"] = float("nan")

        result = calculate_developer_cohort_insights(data)

        self.assertTrue(
            (result["focus_comparison"] == "Insufficient data").all()
        )

    def test_empty_dataset(self):
        result = calculate_developer_cohort_insights(
            self.df.iloc[0:0]
        )

        self.assertTrue(result.empty)
        self.assertIn("flow_comparison", result.columns)

    def test_rejects_missing_columns(self):
        with self.assertRaises(ValueError):
            calculate_developer_cohort_insights(
                self.df.drop(columns=["focus_rating"])
            )
