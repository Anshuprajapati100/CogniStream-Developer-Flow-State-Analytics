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
