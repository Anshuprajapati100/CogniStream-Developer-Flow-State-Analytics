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
