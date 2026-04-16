import json
import sqlite3
from pathlib import Path


class ActivityStore:
    def __init__(self, db_path: Path, seed_path: Path):
        self.db_path = db_path
        self.seed_path = seed_path

    def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL,
                    schedule TEXT NOT NULL,
                    max_participants INTEGER NOT NULL CHECK(max_participants > 0)
                );

                CREATE TABLE IF NOT EXISTS registrations (
                    activity_id INTEGER NOT NULL,
                    email TEXT NOT NULL,
                    PRIMARY KEY (activity_id, email),
                    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
                );
                """
            )

            activity_count = connection.execute(
                "SELECT COUNT(*) FROM activities"
            ).fetchone()[0]

            if activity_count == 0:
                self._seed(connection)

    def list_activities(self) -> dict[str, dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT a.name, a.description, a.schedule, a.max_participants, r.email
                FROM activities a
                LEFT JOIN registrations r ON r.activity_id = a.id
                ORDER BY a.id, r.rowid
                """
            ).fetchall()

        activities: dict[str, dict[str, object]] = {}
        for row in rows:
            name = row["name"]
            if name not in activities:
                activities[name] = {
                    "description": row["description"],
                    "schedule": row["schedule"],
                    "max_participants": row["max_participants"],
                    "participants": [],
                }

            if row["email"]:
                activities[name]["participants"].append(row["email"])

        return activities

    def signup(self, activity_name: str, email: str) -> None:
        normalized_email = email.strip().lower()
        if not normalized_email:
            raise ValueError("Student email is required")

        with self._connect() as connection:
            activity = connection.execute(
                "SELECT id FROM activities WHERE name = ?",
                (activity_name,),
            ).fetchone()

            if activity is None:
                raise KeyError("Activity not found")

            existing_registration = connection.execute(
                "SELECT 1 FROM registrations WHERE activity_id = ? AND email = ?",
                (activity["id"], normalized_email),
            ).fetchone()

            if existing_registration is not None:
                raise ValueError("Student is already signed up")

            connection.execute(
                "INSERT INTO registrations(activity_id, email) VALUES (?, ?)",
                (activity["id"], normalized_email),
            )

    def unregister(self, activity_name: str, email: str) -> None:
        normalized_email = email.strip().lower()
        if not normalized_email:
            raise ValueError("Student email is required")

        with self._connect() as connection:
            activity = connection.execute(
                "SELECT id FROM activities WHERE name = ?",
                (activity_name,),
            ).fetchone()

            if activity is None:
                raise KeyError("Activity not found")

            deleted_rows = connection.execute(
                "DELETE FROM registrations WHERE activity_id = ? AND email = ?",
                (activity["id"], normalized_email),
            ).rowcount

            if deleted_rows == 0:
                raise ValueError("Student is not signed up for this activity")

    def _seed(self, connection: sqlite3.Connection) -> None:
        seed_data = json.loads(self.seed_path.read_text())

        for name, details in seed_data.items():
            cursor = connection.execute(
                """
                INSERT INTO activities(name, description, schedule, max_participants)
                VALUES (?, ?, ?, ?)
                """,
                (
                    name,
                    details["description"],
                    details["schedule"],
                    details["max_participants"],
                ),
            )

            registrations = [
                (cursor.lastrowid, email.strip().lower())
                for email in details.get("participants", [])
            ]

            connection.executemany(
                "INSERT INTO registrations(activity_id, email) VALUES (?, ?)",
                registrations,
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection
