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
        full_name,
        steam_username,
        steam_uid,
        dayz_name,
        branch_id
    ):

            if self.personnel_exists(discord_member.id):
                raise ValueError("Personnel record already exists.")

            # New personnel always enter service at Training.
            training_rank_code = "Training"

            self.database.cursor.execute(
            """
                SELECT rank_id
                FROM ranks
                WHERE code = ?
            """,
            (training_rank_code,)
        )

            rank_result = self.database.cursor.fetchone()

            if rank_result is None:
                raise ValueError(
                "Training rank was not found in the rank database."
                )

            rank_id = rank_result[0]

            # Get branch information.
            self.database.cursor.execute(
            """
                SELECT prefix, name
                FROM branches
                WHERE branch_id = ?
            """,
            (branch_id,)
        )

            branch_result = self.database.cursor.fetchone()

            if branch_result is None: raise ValueError(
                "The selected branch was not found."
            )

            branch_prefix = branch_result[0]
            branch_name = branch_result[1]

            # Generate the branch-specific Service ID.
            service_id = self.id_manager.generate_service_id(branch_prefix)

            # Current date.
            today = datetime.now().strftime("%d/%m/%Y")

            # Discord display name is captured when the record is created.
            display_name = discord_member.display_name

            self.database.cursor.execute(
            """
                INSERT INTO personnel (
                    discord_id,
                    discord_username,
                    full_name,
                    display_name,
                    callsign,
                    steam_username,
                    steam_uid,
                    dayz_name,
                    branch_id,
                    rank_id,
                    position,
                    ambassador,
                    status,
                    current_service_id,
                    date_joined,
                    last_seen,
                    weekly_active_hours,
                    monthly_active_hours,
                    sessions_this_week,
                    payroll_eligible,
                    payroll_balance,
                    notes
                )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                str(discord_member.id),
                str(discord_member),
                full_name,
                display_name,
                None,
                steam_username,
                steam_uid,
                dayz_name,
                branch_id,
                rank_id,
                None,
                0,
                "Active",
                service_id,
                today,
                today,
                0.0,
                0.0,
                0,
                0,
                0,
                "None"
            )
        )

            personnel_id = self.database.cursor.lastrowid

            # Initial Service History entry.
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
                branch_name,
                today
            )
        )

            # Initial rank history entry.
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
                training_rank_code,
                "SYSTEM",
                today
            )
        )

            # Initial name history entry.
            self.database.cursor.execute(
            """
                INSERT INTO name_history (
                    personnel_id,
                    name_type,
                    previous_value,
                    new_value,
                    changed_on,
                    changed_by
                )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                personnel_id,
                "Display Name",
                None,
                display_name,
                today,
                "SYSTEM"
            )
        )

            # Audit log.
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
                (
                    f"Initial assignment to {branch_name} "
                    f"({branch_prefix}) as {training_rank_code}"
                )
            )
        )

            self.database.connection.commit()

            return personnel_id, service_id


    def get_personnel(self, discord_id):

        self.database.cursor.execute(
            """
            SELECT
                p.*,

                b.name AS branch_name,
                b.prefix AS branch_prefix,

                r.name AS rank_name,
                r.code AS rank_code,
                r.pay AS rank_pay

            FROM personnel p

            LEFT JOIN branches b
                ON p.branch_id = b.branch_id

            LEFT JOIN ranks r
                ON p.rank_id = r.rank_id

            WHERE p.discord_id = ?
            """,
            (str(discord_id),)
        )

        return self.database.cursor.fetchone()