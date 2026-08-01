import json
from pathlib import Path


class BranchManager:
    def __init__(self, database):
        self.database = database

        root = Path(__file__).resolve().parents[2]
        self.config = root / "config" / "branches.json"

    def synchronize(self):
        with open(self.config, "r", encoding="utf-8") as file:
            data = json.load(file)

        for branch in data["branches"]:

            self.database.cursor.execute(
                """
                SELECT prefix
                FROM branches
                WHERE prefix = ?
                """,
                (branch["prefix"],)
            )

            if self.database.cursor.fetchone() is None:

                self.database.cursor.execute(
                    """
                    INSERT INTO branches
                    (prefix, name, active, next_service_number)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        branch["prefix"],
                        branch["name"],
                        branch["active"],
                        branch["next_service_number"]
                    )
                )

        self.database.connection.commit()