import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path


def generate_developer_data():

    random.seed(42)

    developers = [
        "DEV001",
        "DEV002",
        "DEV003",
        "DEV004"
    ]

    records = []
    start_date = datetime(2026, 9, 1)

    for i in range(120):

        session_duration = random.randint(60, 180)
        idle_time = random.randint(5, 25)
        other_work_time = random.randint(5, 30)

        coding_time = (
            session_duration - idle_time - other_work_time
        )

        record = {
            "session_id": f"S{i+1:04d}",
            "developer_id": random.choice(developers),
            "session_date": (
                start_date + timedelta(days=i // 6)
            ).strftime("%Y-%m-%d"),
            "session_duration_min": session_duration,
            "coding_time_min": coding_time,
            "idle_time_min": idle_time,
            "other_work_time_min": other_work_time,
            "interruptions": random.randint(0, 7),
            "context_switches": random.randint(0, 12),
            "tasks_completed": random.randint(0, 5),
            "focus_rating": random.randint(1, 5),
            "cognitive_load_rating": random.randint(1, 5),
            "data_source": "synthetic"
        }

        records.append(record)

    df = pd.DataFrame(records)

    project_root = Path(__file__).resolve().parents[1]

    output_path = (
        project_root / "data/raw/developer_sessions_synthetic.csv"
    )

    output_path.parent.mkdir(
        parents=True, exist_ok=True
    )

    df.to_csv(output_path, index=False)

    print("\n===== CogniStream Data Collection =====")
    print("Dataset generated successfully!")
    print(f"Total Sessions: {len(df)}")
    print(f"Total Developers: {df['developer_id'].nunique()}")
    print(f"Dataset Shape: {df.shape}")
    print(f"Saved to: {output_path}")

    return df


if __name__ == "__main__":
    generate_developer_data()
