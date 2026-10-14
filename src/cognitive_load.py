import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = PROJECT_ROOT / "reports/session_analytics.csv"
OUTPUT_FILE = PROJECT_ROOT / "reports/flow_cognitive_analysis.csv"


def analyze_flow_and_load():
    print("\n===== CogniStream Flow & Cognitive Load Analysis =====")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "Analytics report not found. Run: python src/analytics.py"
        )

    df = pd.read_csv(INPUT_FILE)

    required_columns = [
        "session_duration_min",
        "coding_time_min",
        "interruptions",
        "context_switches",
        "focus_rating",
        "cognitive_load_rating"
    ]

    if df.empty:
        raise ValueError("Input dataset is empty.")

    if not set(required_columns).issubset(df.columns):
        raise ValueError("Required analytics columns are missing.")

    if df[required_columns].isna().any().any():
        raise ValueError("Input contains missing values.")

    if (df["session_duration_min"] <= 0).any():
        raise ValueError("Invalid session duration.")

    if not df["focus_rating"].between(1, 5).all():
        raise ValueError("Focus ratings must be between 1 and 5.")

    if not df["cognitive_load_rating"].between(1, 5).all():
        raise ValueError("Cognitive load ratings must be between 1 and 5.")

    if (df[["coding_time_min", "interruptions", "context_switches"]] < 0).any().any():
        raise ValueError("Negative activity values detected.")

    # Coding activity normalized to 0–100
    df["coding_component"] = (
        df["coding_time_min"] / df["session_duration_min"] * 100
    ).clip(0, 100)

    # Calculate interruptions and switches per hour
    df["interruptions_per_hour"] = (
        df["interruptions"] / df["session_duration_min"] * 60
    )

    df["switches_per_hour"] = (
        df["context_switches"] / df["session_duration_min"] * 60
    )

    # Heuristic scales for prototype scoring
    df["interruption_component"] = (
        100 * (1 - df["interruptions_per_hour"] / 6)
    ).clip(0, 100)

    df["switching_component"] = (
        100 * (1 - df["switches_per_hour"] / 10)
    ).clip(0, 100)

    df["focus_component"] = (
        (df["focus_rating"] - 1) / 4 * 100
    )

    # Experimental composite score
    df["flow_indicator_score"] = (
        0.35 * df["coding_component"]
        + 0.25 * df["interruption_component"]
        + 0.20 * df["switching_component"]
        + 0.20 * df["focus_component"]
    ).round(2)

    # Descriptive bands, not diagnosed flow states
    df["flow_indicator_band"] = pd.cut(
        df["flow_indicator_score"],
        bins=[-0.01, 40, 70, 100],
        labels=["Low", "Moderate", "High"]
    )

    # Self-reported cognitive load retained separately
    df["cognitive_load_band"] = pd.cut(
        df["cognitive_load_rating"],
        bins=[0, 2, 3, 5],
        labels=["Low", "Moderate", "High"]
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Total Sessions Analyzed: {len(df)}")
    print(f"Average Flow Indicator Score: {df['flow_indicator_score'].mean():.2f}")

    print("\nFlow Indicator Distribution:")
    print(df["flow_indicator_band"].value_counts().to_string())

    print("\nSelf-Reported Cognitive Load Distribution:")
    print(df["cognitive_load_band"].value_counts().to_string())

    print(f"\nAnalysis saved to: {OUTPUT_FILE}")
    print("Flow & Cognitive Load Analysis Completed Successfully!")


if __name__ == "__main__":
    analyze_flow_and_load()
