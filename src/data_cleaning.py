import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = PROJECT_ROOT / "data/raw/developer_sessions_synthetic.csv"

OUTPUT_FILE = PROJECT_ROOT / "data/processed/cleaned_developer_sessions.csv"


def clean_developer_data():

    print("\n===== CogniStream Data Cleaning =====")

    # Step 1: Load dataset
    df = pd.read_csv(INPUT_FILE)

    print(f"Original Records: {len(df)}")
    print(f"Original Columns: {len(df.columns)}")

    # Step 2: Remove exact duplicate records
    duplicates = df.duplicated().sum()

    df = df.drop_duplicates().copy()

    print(f"Duplicate Records Removed: {duplicates}")

    # Step 3: Convert numerical columns
    numeric_columns = [
        "session_duration_min",
        "coding_time_min",
        "idle_time_min",
        "other_work_time_min",
        "interruptions",
        "context_switches",
        "tasks_completed",
        "focus_rating",
        "cognitive_load_rating"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Step 4: Validate session dates
    df["session_date"] = pd.to_datetime(
        df["session_date"],
        errors="coerce",
        format="%Y-%m-%d"
    )

    # Step 5: Check missing or invalid values
    missing_values = df.isnull().sum().sum()

    print(f"Missing or Invalid Values: {missing_values}")

    if missing_values > 0:
        raise ValueError(
            "Dataset contains missing or invalid values."
        )

    # Step 6: Check unique session identifiers
    if df["session_id"].duplicated().any():
        raise ValueError("Duplicate session IDs detected.")

    # Step 7: Validate session duration
    if (df["session_duration_min"] <= 0).any():
        raise ValueError("Invalid session duration detected.")

    # Step 8: Validate non-negative activity metrics
    activity_columns = [
        "coding_time_min",
        "idle_time_min",
        "other_work_time_min",
        "interruptions",
        "context_switches",
        "tasks_completed"
    ]

    if (df[activity_columns] < 0).any().any():
        raise ValueError("Negative activity values detected.")

    # Step 9: Check time consistency
    total_activity_time = (
        df["coding_time_min"]
        + df["idle_time_min"]
        + df["other_work_time_min"]
    )

    if not total_activity_time.eq(
        df["session_duration_min"]
    ).all():
        raise ValueError("Session time mismatch detected.")

    # Step 10: Validate ratings
    rating_columns = [
        "focus_rating",
        "cognitive_load_rating"
    ]

    for column in rating_columns:
        if not df[column].between(1, 5).all():
            raise ValueError(f"Invalid values in {column}")

    # Step 11: Format dates
    df["session_date"] = df[
        "session_date"
    ].dt.strftime("%Y-%m-%d")

    # Step 12: Save cleaned dataset
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(OUTPUT_FILE, index=False)

    print("\nData Cleaning Completed Successfully!")
    print(f"Cleaned Records: {len(df)}")
    print(f"Total Columns: {len(df.columns)}")
    print(f"Missing Values: {df.isnull().sum().sum()}")
    print(f"Output File: {OUTPUT_FILE}")

    return df


if __name__ == "__main__":
    clean_developer_data()
