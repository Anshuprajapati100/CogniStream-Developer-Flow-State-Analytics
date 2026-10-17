from pathlib import Path

import pandas as pd

from database.db import get_sessions

ROOT = Path(__file__).resolve().parents[1]
CSV_FILE = ROOT / "reports/flow_cognitive_analysis.csv"


def prepare_manual_sessions(sessions):
    """Calculate analytics for manually entered sessions."""

    if not sessions:
        return pd.DataFrame()

    df = pd.DataFrame(sessions)

    duration = df["session_duration_min"]

    if (duration <= 0).any():
        raise ValueError("Session duration must be positive.")

    if not (
        df["coding_time_min"]
        + df["idle_time_min"]
        + df["other_work_time_min"]
    ).eq(duration).all():
        raise ValueError("Session time components do not match.")

    df["coding_activity_ratio"] = (
        df["coding_time_min"] / duration * 100
    )

    df["interruptions_per_hour"] = (
        df["interruptions"] / duration * 60
    )

    df["context_switches_per_hour"] = (
        df["context_switches"] / duration * 60
    )

    df["coding_component"] = (
        df["coding_activity_ratio"].clip(0, 100)
    )

    df["interruption_component"] = (
        100 * (1 - df["interruptions_per_hour"] / 6)
    ).clip(0, 100)

    df["switching_component"] = (
        100 * (1 - df["context_switches_per_hour"] / 10)
    ).clip(0, 100)

    df["focus_component"] = (
        (df["focus_rating"] - 1) / 4 * 100
    )

    df["flow_indicator_score"] = (
        0.35 * df["coding_component"]
        + 0.25 * df["interruption_component"]
        + 0.20 * df["switching_component"]
        + 0.20 * df["focus_component"]
    ).round(2)

    df["flow_indicator_band"] = pd.cut(
        df["flow_indicator_score"],
        bins=[-0.01, 40, 70, 100],
        labels=["Low", "Moderate", "High"],
    )

    df["cognitive_load_band"] = pd.cut(
        df["cognitive_load_rating"],
        bins=[0, 2, 3, 5],
        labels=["Low", "Moderate", "High"],
    )

    df["data_source"] = "manual"

    return df


def load_combined_data():
    """Combine existing synthetic records and manual SQLite sessions."""

    if not CSV_FILE.exists():
        raise FileNotFoundError(
            "Run python src/cognitive_load.py first."
        )

    synthetic = pd.read_csv(CSV_FILE)

    manual = prepare_manual_sessions(get_sessions())

    if manual.empty:
        combined = synthetic.copy()
    else:
        duplicates = set(synthetic["session_id"]) & set(
            manual["session_id"]
        )

        if duplicates:
            raise ValueError(
                f"Duplicate session IDs: {sorted(duplicates)}"
            )

        combined = pd.concat(
            [synthetic, manual],
            ignore_index=True,
        )

    combined["session_date"] = pd.to_datetime(
        combined["session_date"]
    )

    return combined
