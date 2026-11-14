import pandas as pd


def filter_sessions(df, selected_developers, selected_dates):
    """Filter sessions by developer and a single date or date range."""
    filtered = df[
        df["developer_id"].isin(selected_developers)
    ].copy()

    if isinstance(selected_dates, (tuple, list)):
        if len(selected_dates) == 2:
            start_date, end_date = selected_dates
            filtered = filtered[
                filtered["session_date"].dt.date.between(
                    start_date, end_date
                )
            ]
        elif len(selected_dates) == 1:
            selected_date = selected_dates[0]
            filtered = filtered[
                filtered["session_date"].dt.date == selected_date
            ]
    else:
        filtered = filtered[
            filtered["session_date"].dt.date == selected_dates
        ]

    return filtered
def calculate_developer_metric_trends(
    df,
    metric_column,
    min_active_days=2,
):
    """Calculate daily developer averages for a selected metric."""

    allowed_metrics = {
        "flow_indicator_score",
        "focus_rating",
        "cognitive_load_rating",
    }

    if metric_column not in allowed_metrics:
        raise ValueError(
            f"Unsupported metric: {metric_column}"
        )

    required_columns = {
        "session_date",
        "developer_id",
        metric_column,
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    if min_active_days < 1:
        raise ValueError("min_active_days must be at least 1")

    if df.empty:
        return pd.DataFrame(
            columns=[
                "session_date",
                "developer_id",
                "average_metric",
            ]
        )

    data = df.copy()

    data["session_date"] = pd.to_datetime(
        data["session_date"],
        errors="coerce",
    ).dt.normalize()

    data[metric_column] = pd.to_numeric(
        data[metric_column],
        errors="coerce",
    )

    data = data.dropna(
        subset=["session_date", "developer_id", metric_column]
    )

    daily = (
        data.groupby(
            ["session_date", "developer_id"],
            as_index=False,
        )
        .agg(
            average_metric=(metric_column, "mean")
        )
    )

    active_days = daily.groupby(
        "developer_id"
    )["session_date"].nunique()

    eligible = active_days[
        active_days >= min_active_days
    ].index

    return daily[
        daily["developer_id"].isin(eligible)
    ].reset_index(drop=True)


def calculate_developer_cohort_insights(df):
    """Compare developer averages with the average across the filtered cohort."""
    metrics = {
        "flow": {
            "column": "flow_indicator_score",
            "tolerance": 5.0,
        },
        "focus": {
            "column": "focus_rating",
            "tolerance": 0.2,
        },
        "cognitive_load": {
            "column": "cognitive_load_rating",
            "tolerance": 0.2,
        },
    }

    required_columns = {
        "developer_id",
        *(item["column"] for item in metrics.values()),
    }
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    result_columns = ["developer_id", "sessions"]

    for name in metrics:
        result_columns.extend([
            f"avg_{name}",
            f"cohort_avg_{name}",
            f"{name}_difference",
            f"{name}_comparison",
        ])

    if df.empty:
        return pd.DataFrame(columns=result_columns)

    data = df.copy()

    for item in metrics.values():
        column = item["column"]
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce",
        )

    data = data.dropna(subset=["developer_id"])

    if data.empty:
        return pd.DataFrame(columns=result_columns)

    aggregations = {"sessions": ("developer_id", "size")}

    for name, item in metrics.items():
        aggregations[f"avg_{name}"] = (
            item["column"],
            "mean",
        )

    result = (
        data.groupby("developer_id", as_index=False)
        .agg(**aggregations)
    )

    for name, item in metrics.items():
        average_column = f"avg_{name}"
        cohort_column = f"cohort_avg_{name}"
        difference_column = f"{name}_difference"
        comparison_column = f"{name}_comparison"

        cohort_average = result[average_column].mean()

        result[cohort_column] = cohort_average
        result[difference_column] = (
            result[average_column] - cohort_average
        )

        difference = result[difference_column]
        tolerance = item["tolerance"]

        result[comparison_column] = "Insufficient data"
        valid = difference.notna()

        result.loc[
            valid & (difference > tolerance),
            comparison_column,
        ] = "Above cohort"

        result.loc[
            valid & (difference < -tolerance),
            comparison_column,
        ] = "Below cohort"

        result.loc[
            valid & (difference.abs() <= tolerance),
            comparison_column,
        ] = "Near cohort"

    return result[result_columns].sort_values(
        "developer_id"
    ).reset_index(drop=True)


def calculate_developer_session_consistency(df):
    """Summarize session-level flow-score variation for each developer."""

    required_columns = {
        "developer_id",
        "flow_indicator_score",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    result_columns = [
        "developer_id",
        "sessions",
        "avg_flow",
        "flow_std_dev",
        "min_flow",
        "max_flow",
        "flow_range",
        "consistency",
    ]

    if df.empty:
        return pd.DataFrame(columns=result_columns)

    data = df[
        ["developer_id", "flow_indicator_score"]
    ].copy()

    data["flow_indicator_score"] = pd.to_numeric(
        data["flow_indicator_score"],
        errors="coerce",
    ).replace(
        [float("inf"), float("-inf")],
        float("nan"),
    )

    data = data.dropna(
        subset=["developer_id", "flow_indicator_score"]
    )

    if data.empty:
        return pd.DataFrame(columns=result_columns)

    result = (
        data.groupby("developer_id")
        .agg(
            sessions=("flow_indicator_score", "count"),
            avg_flow=("flow_indicator_score", "mean"),
            flow_std_dev=(
                "flow_indicator_score",
                lambda values: values.std(ddof=0),
            ),
            min_flow=("flow_indicator_score", "min"),
            max_flow=("flow_indicator_score", "max"),
        )
        .reset_index()
    )

    result["flow_range"] = result["max_flow"] - result["min_flow"]

    result["consistency"] = "Insufficient data"

    enough_data = result["sessions"] >= 2

    result.loc[
        enough_data & (result["flow_std_dev"] <= 5),
        "consistency",
    ] = "Consistent"

    result.loc[
        enough_data
        & (result["flow_std_dev"] > 5)
        & (result["flow_std_dev"] <= 10),
        "consistency",
    ] = "Moderate variation"

    result.loc[
        enough_data & (result["flow_std_dev"] > 10),
        "consistency",
    ] = "High variation"

    return result[result_columns].sort_values(
        "developer_id"
    ).reset_index(drop=True)
# Python code goes here


def calculate_developer_workload_balance(df):
    """Compare each developer's coding-time share with their session share."""
    required_columns = {
        "developer_id",
        "session_id",
        "coding_time_min",
    }
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    result_columns = [
        "developer_id",
        "sessions",
        "coding_minutes",
        "coding_hours",
        "avg_coding_minutes",
        "session_share_pct",
        "coding_time_share_pct",
        "share_gap_pp",
    ]

    if df.empty:
        return pd.DataFrame(columns=result_columns)

    data = df[
        ["developer_id", "session_id", "coding_time_min"]
    ].copy()

    data["coding_time_min"] = pd.to_numeric(
        data["coding_time_min"],
        errors="coerce",
    ).replace([float("inf"), float("-inf")], float("nan"))

    data = data.dropna(
        subset=["developer_id", "session_id", "coding_time_min"]
    )
    data = data[data["coding_time_min"] >= 0]

    if data.empty:
        return pd.DataFrame(columns=result_columns)

    data = data.drop_duplicates(subset=["session_id"])

    total_sessions = len(data)
    total_coding_minutes = data["coding_time_min"].sum()

    if total_coding_minutes <= 0:
        return pd.DataFrame(columns=result_columns)

    result = (
        data.groupby("developer_id")
        .agg(
            sessions=("session_id", "count"),
            coding_minutes=("coding_time_min", "sum"),
            avg_coding_minutes=("coding_time_min", "mean"),
        )
        .reset_index()
    )

    result["coding_hours"] = result["coding_minutes"] / 60
    result["session_share_pct"] = (
        result["sessions"] / total_sessions * 100
    )
    result["coding_time_share_pct"] = (
        result["coding_minutes"] / total_coding_minutes * 100
    )
    result["share_gap_pp"] = (
        result["coding_time_share_pct"]
        - result["session_share_pct"]
    )

    return result[result_columns].sort_values(
        "developer_id"
    ).reset_index(drop=True)


def calculate_developer_trend_direction(
    df,
    metric_column,
    min_active_days=2,
    stable_threshold=0.01,
):
    """Summarize first-to-latest daily metric changes by developer."""

    trend_data = calculate_developer_metric_trends(
        df,
        metric_column,
        min_active_days=min_active_days,
    )

    result_columns = [
        "developer_id",
        "active_days",
        "first_average",
        "latest_average",
        "absolute_change",
        "percentage_change",
        "trend_direction",
    ]

    if trend_data.empty:
        return pd.DataFrame(columns=result_columns)

    if stable_threshold < 0:
        raise ValueError("stable_threshold cannot be negative")

    trend_data = trend_data.sort_values(
        ["developer_id", "session_date"]
    )

    result = (
        trend_data.groupby("developer_id")
        .agg(
            active_days=("session_date", "nunique"),
            first_average=("average_metric", "first"),
            latest_average=("average_metric", "last"),
        )
        .reset_index()
    )

    result["absolute_change"] = (
        result["latest_average"] - result["first_average"]
    )

    result["percentage_change"] = (
        result["absolute_change"]
        .div(result["first_average"].abs().replace(0, float("nan")))
        * 100
    )

    result["trend_direction"] = "Stable"
    result.loc[
        result["absolute_change"] > stable_threshold,
        "trend_direction",
    ] = "Increasing"
    result.loc[
        result["absolute_change"] < -stable_threshold,
        "trend_direction",
    ] = "Decreasing"

    return result[result_columns].sort_values(
        "developer_id"
    ).reset_index(drop=True)


def calculate_developer_metric_correlations(df, min_periods=3):
    """Calculate Pearson correlations between independent session metrics."""
    metric_columns = [
        "coding_time_min",
        "idle_time_min",
        "interruptions",
        "context_switches",
        "tasks_completed",
        "focus_rating",
        "cognitive_load_rating",
    ]

    if min_periods < 2:
        raise ValueError("min_periods must be at least 2")

    missing_columns = set(metric_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    if df.empty:
        return pd.DataFrame(
            index=metric_columns,
            columns=metric_columns,
            dtype=float,
        )

    data = df[metric_columns].copy()

    for column in metric_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce",
        )

    data = data.replace([float("inf"), float("-inf")], float("nan"))

    return data.corr(
        method="pearson",
        min_periods=min_periods,
    )
