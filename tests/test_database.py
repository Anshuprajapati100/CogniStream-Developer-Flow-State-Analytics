import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import database.db as db


class TestCogniStreamDatabase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"

        self.db_patch = patch.object(db, "DB_PATH", self.db_path)
        self.db_patch.start()

        db.initialize_database()

    def tearDown(self):
        self.db_patch.stop()
        self.temp_dir.cleanup()

    def sample_session(self, session_id="TEST001"):
        return {
            "session_id": session_id,
            "developer_id": "DEVTEST",
            "session_date": "2026-10-17",
            "session_duration_min": 120,
            "coding_time_min": 90,
            "idle_time_min": 15,
            "other_work_time_min": 15,
            "interruptions": 2,
            "context_switches": 3,
            "tasks_completed": 1,
            "focus_rating": 3,
            "cognitive_load_rating": 3,
        }

    def test_add_developer(self):
        db.add_developer("DEVTEST")
        self.assertIn("DEVTEST", db.get_developers())

    def test_developer_normalization(self):
        db.add_developer(" devtest ")
        self.assertIn("DEVTEST", db.get_developers())

    def test_duplicate_developer(self):
        db.add_developer("DEVTEST")
        with self.assertRaises(sqlite3.IntegrityError):
            db.add_developer("DEVTEST")

    def test_empty_developer(self):
        with self.assertRaises(ValueError):
            db.add_developer(" ")

    def test_delete_developer(self):
        db.add_developer("DEVTEST")
        db.delete_developer("DEVTEST")
        self.assertNotIn("DEVTEST", db.get_developers())

    def test_delete_unknown_developer(self):
        with self.assertRaises(ValueError):
            db.delete_developer("UNKNOWN")

    def test_add_session(self):
        db.add_developer("DEVTEST")
        db.add_session(self.sample_session())
        self.assertEqual(len(db.get_sessions()), 1)

    def test_duplicate_session(self):
        db.add_developer("DEVTEST")
        db.add_session(self.sample_session())
        with self.assertRaises(sqlite3.IntegrityError):
            db.add_session(self.sample_session())

    def test_missing_fields(self):
        with self.assertRaises(ValueError):
            db.add_session({"session_id": "TEST001"})

    def test_invalid_duration(self):
        db.add_developer("DEVTEST")
        session = self.sample_session()
        session["session_duration_min"] = 0
        with self.assertRaises(ValueError):
            db.add_session(session)

    def test_invalid_time_total(self):
        db.add_developer("DEVTEST")
        session = self.sample_session()
        session["coding_time_min"] = 100
        with self.assertRaises(ValueError):
            db.add_session(session)

    def test_invalid_focus_rating(self):
        db.add_developer("DEVTEST")
        session = self.sample_session()
        session["focus_rating"] = 6
        with self.assertRaises(ValueError):
            db.add_session(session)

    def test_unknown_developer_session(self):
        with self.assertRaises(ValueError):
            db.add_session(self.sample_session())

    def test_protect_developer_with_sessions(self):
        db.add_developer("DEVTEST")
        db.add_session(self.sample_session())
        with self.assertRaises(ValueError):
            db.delete_developer("DEVTEST")

    def test_delete_session(self):
        db.add_developer("DEVTEST")
        db.add_session(self.sample_session())
        db.delete_session("TEST001")
        self.assertEqual(len(db.get_sessions()), 0)

    def test_delete_unknown_session(self):
        with self.assertRaises(ValueError):
            db.delete_session("UNKNOWN")



    def test_empty_session_id(self):
        session = self.sample_session(session_id=" ")
        with self.assertRaisesRegex(ValueError, "Session ID cannot be empty"):
            db.add_session(session)

    def test_empty_session_developer_id(self):
        session = self.sample_session()
        session["developer_id"] = " "
        with self.assertRaisesRegex(ValueError, "Developer ID cannot be empty"):
            db.add_session(session)

    def test_invalid_session_date(self):
        db.add_developer("DEVTEST")
        session = self.sample_session()
        session["session_date"] = "2026-02-30"
        with self.assertRaisesRegex(ValueError, "valid date"):
            db.add_session(session)

    def test_negative_event_counts(self):
        db.add_developer("DEVTEST")
        for field in ("interruptions", "context_switches", "tasks_completed"):
            with self.subTest(field=field):
                session = self.sample_session(session_id=f"TEST_{field}")
                session[field] = -1
                with self.assertRaisesRegex(ValueError, "cannot be negative"):
                    db.add_session(session)

    def test_non_integer_event_count(self):
        db.add_developer("DEVTEST")
        session = self.sample_session()
        session["interruptions"] = 1.5
        with self.assertRaisesRegex(ValueError, "whole number"):
            db.add_session(session)

    def test_invalid_cognitive_load_rating(self):
        db.add_developer("DEVTEST")
        session = self.sample_session()
        session["cognitive_load_rating"] = 0
        with self.assertRaisesRegex(ValueError, "between 1 and 5"):
            db.add_session(session)

    def test_session_id_normalization(self):
        db.add_developer("DEVTEST")
        session = self.sample_session(session_id=" test002 ")
        db.add_session(session)
        self.assertEqual(db.get_sessions()[0]["session_id"], "TEST002")


if __name__ == "__main__":
    unittest.main()
