import unittest
from datetime import date

import pandas as pd

from src.dashboard_filters import filter_sessions


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
