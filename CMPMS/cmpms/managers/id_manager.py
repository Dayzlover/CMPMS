class IDManager:
    def __init__(self, database):
        self.database = database

    def generate_service_id(self, branch_prefix):
        self.database.cursor.execute(
            """
            SELECT next_service_number
            FROM branches
            WHERE prefix = ?
            """,
            (branch_prefix,)
        )

        row = self.database.cursor.fetchone()

        if row is None:
            raise ValueError(f"Unknown branch prefix: {branch_prefix}")

        number = row["next_service_number"]

        service_id = f"{branch_prefix}-{number:06d}"

        self.database.cursor.execute(
            """
            UPDATE branches
            SET next_service_number = ?
            WHERE prefix = ?
            """,
            (number + 1, branch_prefix)
        )

        self.database.connection.commit()

        return service_id