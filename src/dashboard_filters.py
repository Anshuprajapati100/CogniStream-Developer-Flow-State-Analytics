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
