from pathlib import Path
import sqlite3


class DatabaseManager:
    def __init__(self):
        root = Path(__file__).resolve().parents[2]

        data_dir = root / "data" / "database"
        data_dir.mkdir(parents=True, exist_ok=True)

        self.database_path = data_dir / "cmpms.db"

        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def initialize(self):
        self.create_branches_table()
        self.create_personnel_table()
        self.create_service_history_table()
        self.create_ranks_table()
        self.create_certifications_table()
        self.create_member_certifications_table()
        self.create_promotion_history_table()
        self.create_audit_log_table()

        self.connection.commit()

    def create_personnel_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS personnel (
            personnel_id INTEGER PRIMARY KEY AUTOINCREMENT,

            discord_id TEXT UNIQUE NOT NULL,
            discord_username TEXT,

            display_name TEXT NOT NULL,
            dayz_name TEXT,
            steam_uid TEXT,

            current_service_id TEXT UNIQUE,

            branch TEXT NOT NULL,
            rank TEXT NOT NULL,

            status TEXT NOT NULL,

            join_date TEXT NOT NULL,
            last_active TEXT,

            activity_points INTEGER DEFAULT 0
        )
        """)

    def create_branches_table(self):
        self.cursor.execute("""
    CREATE TABLE IF NOT EXISTS branches (
        branch_id INTEGER PRIMARY KEY AUTOINCREMENT,

        prefix TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,

        active INTEGER DEFAULT 1,

        next_service_number INTEGER DEFAULT 1
    )
    """)

    def create_service_history_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,

            personnel_id INTEGER NOT NULL,

            service_id TEXT NOT NULL,

            branch TEXT NOT NULL,

            start_date TEXT NOT NULL,
            end_date TEXT,

            FOREIGN KEY(personnel_id)
                REFERENCES personnel(personnel_id)
        )
        """)

    def create_ranks_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS ranks (
            rank TEXT PRIMARY KEY,

            pay INTEGER NOT NULL,

            promotion_limit TEXT,

            approval_required INTEGER DEFAULT 0
        )
        """)

    def create_certifications_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS certifications (
            certification_id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT UNIQUE NOT NULL
        )
        """)

    def create_member_certifications_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS member_certifications (
            personnel_id INTEGER NOT NULL,

            certification_id INTEGER NOT NULL,

            awarded_by TEXT,

            awarded_date TEXT,

            PRIMARY KEY(personnel_id, certification_id),

            FOREIGN KEY(personnel_id)
                REFERENCES personnel(personnel_id),

            FOREIGN KEY(certification_id)
                REFERENCES certifications(certification_id)
        )
        """)

    def create_promotion_history_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS promotion_history (
            promotion_id INTEGER PRIMARY KEY AUTOINCREMENT,

            personnel_id INTEGER NOT NULL,

            old_rank TEXT,
            new_rank TEXT NOT NULL,

            promoted_by TEXT,

            promotion_date TEXT NOT NULL,

            FOREIGN KEY(personnel_id)
                REFERENCES personnel(personnel_id)
        )
        """)

    def create_audit_log_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            audit_id INTEGER PRIMARY KEY AUTOINCREMENT,

            personnel_id INTEGER,

            action TEXT NOT NULL,

            performed_by TEXT,

            action_date TEXT NOT NULL,

            details TEXT,

            FOREIGN KEY(personnel_id)
                REFERENCES personnel(personnel_id)
        )
        """)

    def close(self):
        self.connection.close()