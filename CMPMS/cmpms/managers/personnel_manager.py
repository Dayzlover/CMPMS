from datetime import datetime

from cmpms.managers.id_manager import IDManager


class PersonnelManager:

    def __init__(self, database):
        self.database = database
        self.id_manager = IDManager(database)

    def personnel_exists(self, discord_id):

        self.database.cursor.execute(
            """
            SELECT personnel_id
            FROM personnel
            WHERE discord_id = ?
            """,
            (str(discord_id),)
        )

        return self.database.cursor.fetchone() is not None

    def create_personnel(
        self,
        discord_member,
        steam_uid,
        dayz_name,
        branch,
        rank,
        status
    ):

        if self.personnel_exists(discord_member.id):
            raise ValueError("Personnel record already exists.")

        service_id = self.id_manager.generate_service_id(branch)

        today = datetime.timezone.now().strftime("%d/%m/%Y")

        self.database.cursor.execute(
            """
            INSERT INTO personnel (
                discord_id,
                discord_username,
                display_name,
                dayz_name,
                steam_uid,
                current_service_id,
                branch,
                rank,
                status,
                join_date,
                last_active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(discord_member.id),
                str(discord_member),
                discord_member.display_name,
                dayz_name,
                steam_uid,
                service_id,
                branch,
                rank,
                status,
                today,
                today
            )
        )

        personnel_id = self.database.cursor.lastrowid

        self.database.cursor.execute(
            """
            INSERT INTO service_history (
                personnel_id,
                service_id,
                branch,
                start_date
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                personnel_id,
                service_id,
                branch,
                today
            )
        )

        self.database.cursor.execute(
            """
            INSERT INTO promotion_history (
                personnel_id,
                old_rank,
                new_rank,
                promoted_by,
                promotion_date
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                personnel_id,
                None,
                rank,
                "SYSTEM",
                today
            )
        )

        self.database.cursor.execute(
            """
            INSERT INTO audit_log (
                personnel_id,
                action,
                performed_by,
                action_date,
                details
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                personnel_id,
                "Personnel Created",
                "SYSTEM",
                today,
                f"Initial assignment to {branch} as {rank}"
            )
        )

        self.database.connection.commit()

        return service_id