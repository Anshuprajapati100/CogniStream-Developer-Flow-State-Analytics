import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "cognistream.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS developers (
                developer_id TEXT PRIMARY KEY,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                developer_id TEXT NOT NULL,
                session_date TEXT NOT NULL,
                session_duration_min INTEGER NOT NULL
                    CHECK (session_duration_min > 0),
                coding_time_min INTEGER NOT NULL
                    CHECK (coding_time_min >= 0),
                idle_time_min INTEGER NOT NULL
                    CHECK (idle_time_min >= 0),
                other_work_time_min INTEGER NOT NULL
                    CHECK (other_work_time_min >= 0),
                interruptions INTEGER NOT NULL
                    CHECK (interruptions >= 0),
                context_switches INTEGER NOT NULL
                    CHECK (context_switches >= 0),
                tasks_completed INTEGER NOT NULL
                    CHECK (tasks_completed >= 0),
                focus_rating INTEGER NOT NULL
                    CHECK (focus_rating BETWEEN 1 AND 5),
                cognitive_load_rating INTEGER NOT NULL
                    CHECK (cognitive_load_rating BETWEEN 1 AND 5),
                data_source TEXT NOT NULL DEFAULT 'manual',
                FOREIGN KEY (developer_id)
                    REFERENCES developers(developer_id),
                CHECK (
                    coding_time_min + idle_time_min
                    + other_work_time_min = session_duration_min
                )
            )
        """)

    print("CogniStream database initialized successfully!")


def add_developer(developer_id):
    developer_id = developer_id.strip().upper()

    if not developer_id:
        raise ValueError("Developer ID cannot be empty.")

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO developers (developer_id) VALUES (?)",
            (developer_id,)
        )


def get_developers():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT developer_id FROM developers ORDER BY developer_id"
        ).fetchall()

    return [row[0] for row in rows]


def add_session(session):
    required = [
        "session_id",
        "developer_id",
        "session_date",
        "session_duration_min",
        "coding_time_min",
        "idle_time_min",
        "other_work_time_min",
        "interruptions",
        "context_switches",
        "tasks_completed",
        "focus_rating",
        "cognitive_load_rating",
    ]

    missing = [key for key in required if key not in session]

    if missing:
        raise ValueError(f"Missing session fields: {missing}")

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO sessions (
                session_id, developer_id, session_date,
                session_duration_min, coding_time_min,
                idle_time_min, other_work_time_min,
                interruptions, context_switches,
                tasks_completed, focus_rating,
                cognitive_load_rating
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(session[key] for key in required))


def get_sessions():
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row

        rows = conn.execute(
            "SELECT * FROM sessions ORDER BY session_date, session_id"
        ).fetchall()

    return [dict(row) for row in rows]


if __name__ == "__main__":
    initialize_database()


def delete_developer(developer_id):
    """Delete a registered developer only when no sessions exist."""

    developer_id = developer_id.strip().upper()

    if not developer_id:
        raise ValueError("Developer ID is required.")

    with get_connection() as conn:
        exists = conn.execute(
            "SELECT 1 FROM developers WHERE developer_id = ?",
            (developer_id,)
        ).fetchone()

        if not exists:
            raise ValueError("Developer not found.")

        count = conn.execute(
            "SELECT COUNT(*) FROM sessions WHERE developer_id = ?",
            (developer_id,)
        ).fetchone()[0]

        if count > 0:
            raise ValueError(
                f"Developer has {count} saved sessions. "
                "Delete those sessions first."
            )

        conn.execute(
            "DELETE FROM developers WHERE developer_id = ?",
            (developer_id,)
        )


def delete_session(session_id):
    """Delete one manually saved session."""

    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM sessions WHERE session_id = ?",
            (session_id,)
        )

        if cursor.rowcount == 0:
            raise ValueError("Session not found.")
