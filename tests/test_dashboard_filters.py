import unittest
from datetime import date

import pandas as pd

from src.dashboard_filters import filter_sessions

from src.dashboard_filters import calculate_developer_metric_trends
from src.dashboard_filters import calculate_developer_cohort_insights
from src.dashboard_filters import calculate_developer_session_consistency

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


class TestDeveloperSessionConsistency(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            "developer_id": [
                "DEV001", "DEV001", "DEV001",
                "DEV002", "DEV002", "DEV003",
            ],
            "flow_indicator_score": [
                70, 72, 74,
                50, 80, 85,
            ],
        })

    def test_calculates_session_statistics(self):
        result = calculate_developer_session_consistency(
            self.df
        )

        dev1 = result[
            result["developer_id"] == "DEV001"
        ].iloc[0]

        self.assertEqual(dev1["sessions"], 3)
        self.assertEqual(dev1["avg_flow"], 72)
        self.assertAlmostEqual(
            dev1["flow_std_dev"],
            1.632993,
            places=5,
        )
        self.assertEqual(dev1["min_flow"], 70)
        self.assertEqual(dev1["max_flow"], 74)
        self.assertEqual(dev1["flow_range"], 4)

    def test_classifies_consistency_levels(self):
        result = calculate_developer_session_consistency(
            self.df
        )

        labels = result.set_index(
            "developer_id"
        )["consistency"]

        self.assertEqual(labels["DEV001"], "Consistent")
        self.assertEqual(labels["DEV002"], "High variation")
        self.assertEqual(
            labels["DEV003"],
            "Insufficient data",
        )

    def test_classifies_moderate_variation(self):
        df = pd.DataFrame({
            "developer_id": ["DEV001", "DEV001"],
            "flow_indicator_score": [50, 62],
        })

        result = calculate_developer_session_consistency(df)

        self.assertEqual(
            result.iloc[0]["consistency"],
            "Moderate variation",
        )

    def test_handles_missing_and_non_numeric_values(self):
        df = pd.DataFrame({
            "developer_id": [
                "DEV001", "DEV001", "DEV001",
            ],
            "flow_indicator_score": [
                70, None, "invalid",
            ],
        })

        result = calculate_developer_session_consistency(df)

        self.assertEqual(result.iloc[0]["sessions"], 1)
        self.assertEqual(
            result.iloc[0]["consistency"],
            "Insufficient data",
        )

    def test_empty_dataset(self):
        result = calculate_developer_session_consistency(
            self.df.iloc[0:0]
        )

        self.assertTrue(result.empty)

    def test_rejects_missing_columns(self):
        with self.assertRaises(ValueError):
            calculate_developer_session_consistency(
                self.df.drop(columns=["flow_indicator_score"])
            )


class TestDeveloperWorkloadBalance(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            "developer_id": [
                "DEV001", "DEV001", "DEV002", "DEV002", "DEV003",
            ],
            "session_id": [
                "S001", "S002", "S003", "S004", "S005",
            ],
            "coding_time_min": [
                60, 120, 90, 90, 140,
            ],
        })

    def test_calculates_workload_statistics(self):
        from src.dashboard_filters import calculate_developer_workload_balance

        result = calculate_developer_workload_balance(self.df)
        dev1 = result.set_index("developer_id").loc["DEV001"]

        self.assertEqual(dev1["sessions"], 2)
        self.assertEqual(dev1["coding_minutes"], 180)
        self.assertEqual(dev1["coding_hours"], 3)
        self.assertEqual(dev1["avg_coding_minutes"], 90)
        self.assertEqual(dev1["session_share_pct"], 40)
        self.assertAlmostEqual(dev1["coding_time_share_pct"], 36)
        self.assertAlmostEqual(dev1["share_gap_pp"], -4)

    def test_calculates_share_gap_for_all_developers(self):
        from src.dashboard_filters import calculate_developer_workload_balance

        result = calculate_developer_workload_balance(self.df)
        gaps = result.set_index("developer_id")["share_gap_pp"]

        self.assertAlmostEqual(gaps["DEV001"], -4)
        self.assertAlmostEqual(gaps["DEV002"], -4)
        self.assertAlmostEqual(gaps["DEV003"], 8)

    def test_handles_missing_and_non_numeric_values(self):
        from src.dashboard_filters import calculate_developer_workload_balance

        df = pd.DataFrame({
            "developer_id": ["DEV001", "DEV001", "DEV002"],
            "session_id": ["S001", "S002", "S003"],
            "coding_time_min": [60, None, "invalid"],
        })

        result = calculate_developer_workload_balance(df)

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["sessions"], 1)
        self.assertEqual(result.iloc[0]["coding_minutes"], 60)

    def test_excludes_negative_and_infinite_values(self):
        from src.dashboard_filters import calculate_developer_workload_balance

        df = pd.DataFrame({
            "developer_id": ["DEV001", "DEV001", "DEV002"],
            "session_id": ["S001", "S002", "S003"],
            "coding_time_min": [60, -10, float("inf")],
        })

        result = calculate_developer_workload_balance(df)

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["sessions"], 1)

    def test_empty_dataset(self):
        from src.dashboard_filters import calculate_developer_workload_balance

        result = calculate_developer_workload_balance(
            self.df.iloc[0:0]
        )

        self.assertTrue(result.empty)
        self.assertIn("share_gap_pp", result.columns)

    def test_zero_total_coding_time(self):
        from src.dashboard_filters import calculate_developer_workload_balance

        df = pd.DataFrame({
            "developer_id": ["DEV001", "DEV002"],
            "session_id": ["S001", "S002"],
            "coding_time_min": [0, 0],
        })

        result = calculate_developer_workload_balance(df)

        self.assertTrue(result.empty)

    def test_rejects_missing_columns(self):
        from src.dashboard_filters import calculate_developer_workload_balance

        with self.assertRaises(ValueError):
            calculate_developer_workload_balance(
                self.df.drop(columns=["coding_time_min"])
            )

    def test_ignores_duplicate_session_ids(self):
        from src.dashboard_filters import calculate_developer_workload_balance

        df = pd.concat(
            [self.df, self.df.iloc[[0]]],
            ignore_index=True,
        )

        result = calculate_developer_workload_balance(df)
        dev1 = result.set_index("developer_id").loc["DEV001"]

        self.assertEqual(dev1["sessions"], 2)
        self.assertEqual(dev1["coding_minutes"], 180)


class TestDeveloperTrendDirection(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            "session_date": pd.to_datetime([
                "2026-11-01", "2026-11-02",
                "2026-11-03", "2026-11-01",
                "2026-11-02", "2026-11-03",
                "2026-11-01", "2026-11-02",
                "2026-11-01",
            ]),
            "developer_id": [
                "DEV001", "DEV001", "DEV001",
                "DEV002", "DEV002", "DEV002",
                "DEV003", "DEV003", "DEV004",
            ],
            "flow_indicator_score": [
                60, 70, 80,
                80, 70, 60,
                50, 50,
                90,
            ],
        })

    def test_identifies_increasing_trend(self):
        from src.dashboard_filters import calculate_developer_trend_direction

        result = calculate_developer_trend_direction(
            self.df, "flow_indicator_score"
        )
        dev1 = result.set_index("developer_id").loc["DEV001"]

        self.assertEqual(dev1["trend_direction"], "Increasing")
        self.assertEqual(dev1["absolute_change"], 20)
        self.assertAlmostEqual(dev1["percentage_change"], 100 / 3)

    def test_identifies_decreasing_trend(self):
        from src.dashboard_filters import calculate_developer_trend_direction

        result = calculate_developer_trend_direction(
            self.df, "flow_indicator_score"
        )
        dev2 = result.set_index("developer_id").loc["DEV002"]

        self.assertEqual(dev2["trend_direction"], "Decreasing")
        self.assertEqual(dev2["absolute_change"], -20)

    def test_identifies_stable_trend(self):
        from src.dashboard_filters import calculate_developer_trend_direction

        result = calculate_developer_trend_direction(
            self.df, "flow_indicator_score"
        )
        dev3 = result.set_index("developer_id").loc["DEV003"]

        self.assertEqual(dev3["trend_direction"], "Stable")
        self.assertEqual(dev3["absolute_change"], 0)

    def test_excludes_developers_with_insufficient_days(self):
        from src.dashboard_filters import calculate_developer_trend_direction

        result = calculate_developer_trend_direction(
            self.df, "flow_indicator_score"
        )

        self.assertNotIn("DEV004", result["developer_id"].tolist())

    def test_rejects_negative_stable_threshold(self):
        from src.dashboard_filters import calculate_developer_trend_direction

        with self.assertRaises(ValueError):
            calculate_developer_trend_direction(
                self.df,
                "flow_indicator_score",
                stable_threshold=-1,
            )

    def test_rejects_missing_columns(self):
        from src.dashboard_filters import calculate_developer_trend_direction

        with self.assertRaises(ValueError):
            calculate_developer_trend_direction(
                self.df.drop(columns=["flow_indicator_score"]),
                "flow_indicator_score",
            )
