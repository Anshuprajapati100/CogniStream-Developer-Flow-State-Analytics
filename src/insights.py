import pandas as pd


def generate_insights(df):
    """Generate descriptive insights from developer session data."""

    if df.empty:
        return ["No data available for analysis."]

    required = {
        "coding_time_min",
        "session_duration_min",
        "interruptions",
        "context_switches",
        "focus_rating",
        "cognitive_load_rating",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    if df[list(required)].isna().any().any():
        raise ValueError("Input contains missing values.")

    if (df["session_duration_min"] <= 0).any():
        raise ValueError("Session durations must be positive.")

    if (df["coding_time_min"] < 0).any():
        raise ValueError("Coding time cannot be negative.")

    if (df["coding_time_min"] > df["session_duration_min"]).any():
        raise ValueError("Coding time exceeds session duration.")

    total_hours = df["session_duration_min"].sum() / 60
    coding_hours = df["coding_time_min"].sum() / 60

    activity_ratio = coding_hours / total_hours * 100

    interruptions_per_hour = (
        df["interruptions"].sum() / total_hours
    )

    switches_per_hour = (
        df["context_switches"].sum() / total_hours
    )

    average_focus = df["focus_rating"].mean()
    average_load = df["cognitive_load_rating"].mean()

    # Demonstration threshold: at least 3 interruptions/hour
    session_interruption_rate = (
        df["interruptions"]
        / df["session_duration_min"]
        * 60
    )

    high_interruption_sessions = (
        session_interruption_rate >= 3
    ).sum()

    insights = [
        (
            f"Coding activity represents {activity_ratio:.1f}% "
            "of recorded session time."
        ),
        (
            f"Average interruption frequency is "
            f"{interruptions_per_hour:.2f} per hour."
        ),
        (
            f"Average context-switching frequency is "
            f"{switches_per_hour:.2f} per hour."
        ),
        (
            f"Average simulated focus rating is "
            f"{average_focus:.2f}/5."
        ),
        (
            f"Average simulated cognitive load rating is "
            f"{average_load:.2f}/5."
        ),
        (
            f"{high_interruption_sessions} of {len(df)} sessions "
            "have at least 3 interruptions per hour "
            "(illustrative threshold)."
        ),
    ]

    return insights
