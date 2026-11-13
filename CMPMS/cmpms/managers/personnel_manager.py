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

    def update_personnel(
        self,
        personnel_id,
        full_name,
        display_name,
        callsign,
        steam_username,
        steam_uid,
        dayz_name,
        position,
        ambassador,
        status,
        notes,
        performed_by
    ):

        self.database.cursor.execute(
            """
            SELECT personnel_id
            FROM personnel
            WHERE personnel_id = ?
            """,
            (personnel_id,)
        )

        personnel = self.database.cursor.fetchone()

        if personnel is None:
            raise ValueError("Personnel record not found.")

        if status not in (
            "Active",
            "Inactive",
            "AWOL",
            "Discharged",
            "Deceased"
        ):
            raise ValueError(
                "Invalid personnel status."
            )

        self.database.cursor.execute(
            """
            UPDATE personnel
            SET
                full_name = ?,
                display_name = ?,
                callsign = ?,
                steam_username = ?,
                steam_uid = ?,
                dayz_name = ?,
                position = ?,
                ambassador = ?,
                status = ?,
                notes = ?
            WHERE personnel_id = ?
            """,
            (
                full_name,
                display_name,
                callsign,
                steam_username,
                steam_uid,
                dayz_name,
                position,
                1 if ambassador else 0,
                status,
                notes,
                personnel_id
            )
        )

        today = datetime.now().strftime("%d/%m/%Y")

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
                "Personnel Record Updated",
                performed_by,
                today,
                "Personnel record edited."
            )
        )

        self.database.connection.commit()


    
    def get_commander_count(self):
        self.database.cursor.execute(
            """
            SELECT COUNT(*)
            FROM personnel p
            JOIN ranks r ON p.rank_id = r.rank_id
            WHERE r.code = 'COMMANDER'
            """
        )
        return self.database.cursor.fetchone()[0]

    def get_rank_seniority(self, rank_code, rank_order):
        special_ranks = {
            "JCS-CGDF",
            "JCS-CADF",
            "JCS-FLEET",
            "COMMANDER"
        }

        if rank_code in special_ranks:
            return 200

        return rank_order

    def change_rank(
        self,
        personnel_id,
        new_rank_code,
        performed_by,
        change_type
    ):
        """
        Change an ordinary rank.

        Special ranks must be assigned through appoint_rank().
        """

        today = datetime.now().strftime("%d/%m/%Y")

        try:
            if change_type not in ("Promotion", "Demotion"):
                raise ValueError("Invalid rank change type.")

            special_ranks = {
                "JCS-CGDF",
                "JCS-CADF",
                "JCS-FLEET",
                "COMMANDER"
            }

            if new_rank_code.upper() in special_ranks:
                raise ValueError(
                    "Special ranks must be assigned through the "
                    "appointment process."
                )

            self.database.cursor.execute(
                """
                SELECT
                    p.personnel_id,
                    r.code AS old_rank_code,
                    r.name AS old_rank_name,
                    r.rank_order AS old_rank_order,
                    r.promotion_limit AS old_promotion_limit
                FROM personnel p
                JOIN ranks r ON p.rank_id = r.rank_id
                WHERE p.personnel_id = ?
                """,
                (personnel_id,)
            )

            personnel = self.database.cursor.fetchone()

            if personnel is None:
                raise ValueError("Personnel record not found.")

            self.database.cursor.execute(
                """
                SELECT
                    rank_id,
                    code,
                    name,
                    rank_order
                FROM ranks
                WHERE UPPER(code) = UPPER(?)
                """,
                (new_rank_code.strip(),)
            )

            target_rank = self.database.cursor.fetchone()

            if target_rank is None:
                raise ValueError("The requested rank does not exist.")

            old_code = personnel["old_rank_code"]
            old_name = personnel["old_rank_name"]
            old_order = self.get_rank_seniority(
                old_code,
                personnel["old_rank_order"]
            )

            new_code = target_rank["code"]
            new_name = target_rank["name"]
            new_order = self.get_rank_seniority(
                new_code,
                target_rank["rank_order"]
            )

            if old_code == new_code:
                raise ValueError("Personnel already holds this rank.")

            if change_type == "Promotion" and new_order <= old_order:
                raise ValueError(
                    "The selected rank is not higher than the current rank."
                )

            if change_type == "Demotion" and new_order >= old_order:
                raise ValueError(
                    "The selected rank is not lower than the current rank."
                )

            promotion_limit = personnel["old_promotion_limit"]

            if (
                change_type == "Promotion"
                and promotion_limit
                and new_code != promotion_limit
            ):
                raise ValueError(
                    f"Personnel holding {old_name} can only be "
                    f"promoted to {promotion_limit}."
                )

            self._record_rank_change(
                personnel_id,
                old_code,
                old_name,
                target_rank["rank_id"],
                new_code,
                new_name,
                performed_by,
                change_type,
                today
            )

            return {
                "personnel_id": personnel_id,
                "old_rank_code": old_code,
                "old_rank_name": old_name,
                "new_rank_code": new_code,
                "new_rank_name": new_name,
                "change_type": change_type,
                "date": today
            }

        except Exception:
            self.database.connection.rollback()
            raise

    def appoint_rank(
        self,
        personnel_id,
        new_rank_code,
        performed_by
    ):
        """
        Assign one of the special ranks through Commander authority.
        """

        special_ranks = {
            "JCS-CGDF",
            "JCS-CADF",
            "JCS-FLEET"
        }

        if new_rank_code.upper() not in special_ranks:
            raise ValueError(
                "This rank cannot be assigned through appointments."
            )

        today = datetime.now().strftime("%d/%m/%Y")

        try:
            self.database.cursor.execute(
                """
                SELECT
                    p.personnel_id,
                    r.code AS old_rank_code,
                    r.name AS old_rank_name
                FROM personnel p
                JOIN ranks r ON p.rank_id = r.rank_id
                WHERE p.personnel_id = ?
                """,
                (personnel_id,)
            )

            personnel = self.database.cursor.fetchone()

            if personnel is None:
                raise ValueError("Personnel record not found.")

            self.database.cursor.execute(
                """
                SELECT rank_id, code, name
                FROM ranks
                WHERE UPPER(code) = UPPER(?)
                """,
                (new_rank_code.strip(),)
            )

            target = self.database.cursor.fetchone()

            if target is None:
                raise ValueError("The requested rank does not exist.")

            if personnel["old_rank_code"] == target["code"]:
                raise ValueError("Personnel already holds this rank.")

            self._record_rank_change(
                personnel_id,
                personnel["old_rank_code"],
                personnel["old_rank_name"],
                target["rank_id"],
                target["code"],
                target["name"],
                performed_by,
                "Appointment",
                today
            )

            return {
                "personnel_id": personnel_id,
                "old_rank_code": personnel["old_rank_code"],
                "old_rank_name": personnel["old_rank_name"],
                "new_rank_code": target["code"],
                "new_rank_name": target["name"],
                "change_type": "Appointment",
                "date": today
            }

        except Exception:
            self.database.connection.rollback()
            raise

    def bootstrap_commander(self, discord_id, performed_by):
        """
        One-time initial Commander assignment for the bot owner.
        """

        today = datetime.now().strftime("%d/%m/%Y")

        try:
            if self.get_commander_count() > 0:
                raise ValueError(
                    "A Commander already exists. Initial setup is closed."
                )

            self.database.cursor.execute(
                """
                SELECT
                    p.personnel_id,
                    r.code AS old_rank_code,
                    r.name AS old_rank_name
                FROM personnel p
                JOIN ranks r ON p.rank_id = r.rank_id
                WHERE p.discord_id = ?
                """,
                (str(discord_id),)
            )

            personnel = self.database.cursor.fetchone()

            if personnel is None:
                raise ValueError(
                    "You need an existing personnel record before "
                    "you can become Commander."
                )

            self.database.cursor.execute(
                """
                SELECT rank_id, code, name
                FROM ranks
                WHERE code = 'COMMANDER'
                """
            )

            commander = self.database.cursor.fetchone()

            if commander is None:
                raise ValueError(
                    "COMMANDER rank is missing from the rank database."
                )

            self._record_rank_change(
                personnel["personnel_id"],
                personnel["old_rank_code"],
                personnel["old_rank_name"],
                commander["rank_id"],
                commander["code"],
                commander["name"],
                performed_by,
                "Initial Commander Appointment",
                today
            )

            return {
                "personnel_id": personnel["personnel_id"],
                "old_rank_code": personnel["old_rank_code"],
                "new_rank_code": commander["code"],
                "new_rank_name": commander["name"],
                "change_type": "Initial Commander Appointment",
                "date": today
            }

        except Exception:
            self.database.connection.rollback()
            raise

    def _record_rank_change(
        self,
        personnel_id,
        old_code,
        old_name,
        new_rank_id,
        new_code,
        new_name,
        performed_by,
        action,
        today
    ):
        self.database.cursor.execute(
            """
            UPDATE personnel
            SET rank_id = ?
            WHERE personnel_id = ?
            """,
            (new_rank_id, personnel_id)
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
                old_code,
                new_code,
                performed_by,
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
                action,
                performed_by,
                today,
                f"{old_code} ({old_name}) -> {new_code} ({new_name})"
            )
        )

        self.database.connection.commit()


    def get_service_history(self, personnel_id):

        self.database.cursor.execute(
            """
            SELECT
                service_id,
                branch,
                start_date,
                end_date
            FROM service_history
            WHERE personnel_id = ?
            ORDER BY history_id ASC
            """,
            (personnel_id,)
        )

        return self.database.cursor.fetchall()

    def transfer_personnel(
        self,
        personnel_id,
        new_branch_id,
        performed_by
    ):

        self.database.cursor.execute(
            """
            SELECT
                p.current_service_id,
                p.branch_id,
                b.prefix
            FROM personnel p
            LEFT JOIN branches b
                ON p.branch_id = b.branch_id
            WHERE p.personnel_id = ?
            """,
            (personnel_id,)
        )

        personnel = self.database.cursor.fetchone()

        if personnel is None:
            raise ValueError("Personnel record not found.")

        old_service_id = personnel["current_service_id"]
        old_branch_id = personnel["branch_id"]

        if old_branch_id == new_branch_id:
            raise ValueError(
                "Personnel is already assigned to this branch."
            )

        self.database.cursor.execute(
            """
            SELECT
                prefix,
                name
            FROM branches
            WHERE branch_id = ?
              AND active = 1
            """,
            (new_branch_id,)
        )

        new_branch = self.database.cursor.fetchone()

        if new_branch is None:
            raise ValueError(
                "Target branch does not exist or is inactive."
            )

        new_branch_prefix = new_branch["prefix"]
        new_branch_name = new_branch["name"]

        today = datetime.now().strftime("%d/%m/%Y")

        new_service_id = self.id_manager.generate_service_id(
            new_branch_prefix
        )

        self.database.cursor.execute(
            """
            UPDATE service_history
            SET end_date = ?
            WHERE personnel_id = ?
              AND service_id = ?
              AND end_date IS NULL
            """,
            (
                today,
                personnel_id,
                old_service_id
            )
        )

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
                new_service_id,
                new_branch_prefix,
                today
            )
        )

        self.database.cursor.execute(
            """
            UPDATE personnel
            SET
                branch_id = ?,
                current_service_id = ?
            WHERE personnel_id = ?
            """,
            (
                new_branch_id,
                new_service_id,
                personnel_id
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
                "Branch Transfer",
                performed_by,
                today,
                f"Transferred from {old_service_id} to ",
                f"{new_service_id} ({new_branch_name})"
            )
        )

        self.database.connection.commit()

        return {
            "old_service_id": old_service_id,
            "new_service_id": new_service_id,
            "new_branch_id": new_branch_id,
            "new_branch_name": new_branch_name,
            "date": today
        }