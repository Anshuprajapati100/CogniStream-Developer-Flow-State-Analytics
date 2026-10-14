import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = (
    PROJECT_ROOT / "data/processed/cleaned_developer_sessions.csv"
)


def load_data():
    """Load the cleaned developer activity dataset."""
    return pd.read_csv(DATA_FILE)


def calculate_metrics(df):
    """Calculate developer activity metrics."""

    df = df.copy()

    df["coding_activity_ratio"] = (
        df["coding_time_min"]
        / df["session_duration_min"]
        * 100
    )

    df["interruptions_per_hour"] = (
        df["interruptions"]
        / df["session_duration_min"]
        * 60
    )

    df["context_switches_per_hour"] = (
        df["context_switches"]
        / df["session_duration_min"]
        * 60
    )

    return df


def generate_summary(df):
    """Generate project-level analytics summary."""

    summary = {
        "Total Sessions": len(df),
        "Total Developers": df["developer_id"].nunique(),
        "Total Coding Hours": round(
            df["coding_time_min"].sum() / 60, 2
        ),
        "Average Session Duration (min)": round(
            df["session_duration_min"].mean(), 2
        ),
        "Average Coding Time (min)": round(
            df["coding_time_min"].mean(), 2
        ),
        "Overall Coding Activity (%)": round(
            df["coding_time_min"].sum()
            / df["session_duration_min"].sum()
            * 100, 2
        ),
        "Total Interruptions": int(
            df["interruptions"].sum()
        ),
        "Total Context Switches": int(
            df["context_switches"].sum()
        ),
        "Average Focus Rating": round(
            df["focus_rating"].mean(), 2
        ),
        "Average Cognitive Load Rating": round(
            df["cognitive_load_rating"].mean(), 2
        ),
    }

    return summary


def developer_analysis(df):
    """Compare developer activity patterns."""

    result = df.groupby("developer_id").agg(
        total_sessions=("session_id", "count"),
        coding_hours=("coding_time_min", lambda x: round(x.sum() / 60, 2)),
        avg_focus=("focus_rating", "mean"),
        avg_cognitive_load=("cognitive_load_rating", "mean"),
        total_interruptions=("interruptions", "sum"),
        total_context_switches=("context_switches", "sum"),
        avg_coding_activity=("coding_activity_ratio", "mean"),
    )

    return result.round(2)


def save_analytics(df, developer_stats):

    output_dir = PROJECT_ROOT / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        output_dir / "session_analytics.csv",
        index=False
    )

    developer_stats.to_csv(
        output_dir / "developer_summary.csv"
    )


def main():

    print("\n===== CogniStream Analytics =====")

    df = load_data()

    df = calculate_metrics(df)

    summary = generate_summary(df)

    print("\nPROJECT SUMMARY")
    print("--------------------------------")

    for metric, value in summary.items():
        print(f"{metric}: {value}")

    developer_stats = developer_analysis(df)

    print("\nDEVELOPER ANALYSIS")
    print("--------------------------------")
    print(developer_stats.to_string())

    save_analytics(df, developer_stats)

    print("\nAnalytics completed successfully!")
    print("Reports saved in reports/ folder.")


if __name__ == "__main__":
    main()
