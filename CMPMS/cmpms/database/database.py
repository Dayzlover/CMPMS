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
        self.create_name_history_table()

        self.connection.commit()

    def create_personnel_table(self):
        self.cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS personnel (
            personnel_id INTEGER PRIMARY KEY AUTOINCREMENT,

            discord_id TEXT UNIQUE NOT NULL,
            discord_username TEXT NOT NULL,

            full_name TEXT NOT NULL,
            display_name TEXT NOT NULL,
            callsign TEXT,

            steam_username TEXT,
            steam_uid TEXT UNIQUE NOT NULL,

            dayz_name TEXT NOT NULL,

            branch_id INTEGER NOT NULL,
            rank_id INTEGER NOT NULL,

            position TEXT,
            ambassador INTEGER DEFAULT 0,

            status TEXT NOT NULL,

            current_service_id TEXT UNIQUE NOT NULL,

            date_joined TEXT NOT NULL,
            last_seen TEXT,

            weekly_active_hours REAL DEFAULT 0,
            monthly_active_hours REAL DEFAULT 0,
            sessions_this_week INTEGER DEFAULT 0,

            payroll_eligible INTEGER DEFAULT 0,
            payroll_balance INTEGER DEFAULT 0,

            notes TEXT DEFAULT 'None',

            FOREIGN KEY(branch_id)
                REFERENCES branches(branch_id),

            FOREIGN KEY(rank_id)
                REFERENCES ranks(rank_id)
            )
        """
    )

    def create_branches_table(self):
        self.cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS branches (
            branch_id INTEGER PRIMARY KEY AUTOINCREMENT,

            prefix TEXT UNIQUE NOT NULL,

            name TEXT NOT NULL,

            active INTEGER DEFAULT 1,

            next_service_number INTEGER DEFAULT 1
            )
        """
    )

    def create_ranks_table(self):
        self.cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS ranks (
            rank_id INTEGER PRIMARY KEY AUTOINCREMENT,

            code TEXT UNIQUE NOT NULL,

            name TEXT NOT NULL,

            category TEXT NOT NULL,

            pay INTEGER NOT NULL,

            promotion_limit TEXT,

            approval_required INTEGER DEFAULT 0
            )
        """
    )

    def create_certifications_table(self):
        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS certifications (
            certification_id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT UNIQUE NOT NULL
        )
        """)

    def create_member_certifications_table(self):
        self.cursor.execute(
            """
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

    def create_service_history_table(self):
        self.cursor.execute(
            """
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
            """
        )

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

    def create_name_history_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS name_history (
                name_history_id INTEGER PRIMARY KEY AUTOINCREMENT,

                personnel_id INTEGER NOT NULL,

                name_type TEXT NOT NULL,
                previous_value TEXT,
                new_value TEXT NOT NULL,

                changed_on TEXT NOT NULL,
                changed_by TEXT NOT NULL,

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