import json


class RankManager:

    def __init__(self, database):
        self.database = database

    def synchronize(self):

        with open("config/ranks.json", "r", encoding="utf-8") as file:
            ranks = json.load(file)

        for rank in ranks:

            self.database.cursor.execute(
                """
                SELECT rank_id
                FROM ranks
                WHERE code = ?
                """,
                (rank["code"],)
            )

            if self.database.cursor.fetchone() is None:

                self.database.cursor.execute(
                    """
                    INSERT INTO ranks (
                        code,
                        name,
                        category,
                        pay,
                        promotion_limit,
                        approval_required
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        rank["code"],
                        rank["name"],
                        rank["category"],
                        rank["pay"],
                        rank["promotion_limit"],
                        rank["approval_required"]
                    )
                )

        self.database.connection.commit()