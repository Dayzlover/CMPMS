import discord
from discord import app_commands
from discord.ext import commands

from cmpms.managers.personnel_manager import PersonnelManager
from cmpms.database.database import DatabaseManager

RANK_CHOICES = [
    app_commands.Choice(name="Training", value="Training"),
    app_commands.Choice(name="OR-1", value="OR-1"),
    app_commands.Choice(name="OR-2", value="OR-2"),
    app_commands.Choice(name="OR-3", value="OR-3"),
    app_commands.Choice(name="OR-4", value="OR-4"),
    app_commands.Choice(name="OR-5", value="OR-5"),
    app_commands.Choice(name="OR-6", value="OR-6"),
    app_commands.Choice(name="OR-7", value="OR-7"),
    app_commands.Choice(name="OR-8", value="OR-8"),
    app_commands.Choice(name="OR-9", value="OR-9"),
    app_commands.Choice(name="OR-10", value="OR-10"),
    app_commands.Choice(name="OF-1", value="OF-1"),
    app_commands.Choice(name="OF-2", value="OF-2"),
    app_commands.Choice(name="OF-3", value="OF-3"),
    app_commands.Choice(name="OF-4", value="OF-4"),
    app_commands.Choice(name="OF-5", value="OF-5"),
    app_commands.Choice(name="OF-6", value="OF-6"),
    app_commands.Choice(name="OF-7", value="OF-7"),
    app_commands.Choice(name="OF-8", value="OF-8"),
    app_commands.Choice(name="OF-9", value="OF-9"),
    app_commands.Choice(name="OF-10", value="OF-10"),
]

JCS_RANK_CHOICES = [
    app_commands.Choice(
        name="General of the CGDF",
        value="JCS-CGDF"
    ),
    app_commands.Choice(
        name="General of the CADF",
        value="JCS-CADF"
    ),
    app_commands.Choice(
        name="Fleet Admiral",
        value="JCS-FLEET"
    ),
]

class IdentityEditModal(discord.ui.Modal, title="Edit Identity"):

    def __init__(self, cog, personnel):
        super().__init__()

        self.cog = cog
        self.personnel = personnel

        self.full_name = discord.ui.TextInput(
            label="Full Name",
            default=personnel["full_name"],
            required=True,
            max_length=100
        )

        self.display_name = discord.ui.TextInput(
            label="Display Name",
            default=personnel["display_name"],
            required=True,
            max_length=100
        )

        self.callsign = discord.ui.TextInput(
            label="Callsign",
            default=personnel["callsign"] or "",
            required=False,
            max_length=50
        )

        self.add_item(self.full_name)
        self.add_item(self.display_name)
        self.add_item(self.callsign)

    async def on_submit(self, interaction: discord.Interaction):

        try:
            self.cog.personnel_manager.update_personnel(
                personnel_id=self.personnel["personnel_id"],
                full_name=self.full_name.value,
                display_name=self.display_name.value,
                callsign=self.callsign.value or None,
                steam_username=self.personnel["steam_username"],
                steam_uid=self.personnel["steam_uid"],
                dayz_name=self.personnel["dayz_name"],
                position=self.personnel["position"],
                ambassador=self.personnel["ambassador"],
                status=self.personnel["status"],
                notes=self.personnel["notes"],
                performed_by=str(interaction.user)
            )

            await interaction.response.send_message(
                "Personnel identity information updated successfully."
            )

        except Exception as error:
            await interaction.response.send_message(
                f"Personnel update failed: {error}"
            )

class GameEditModal(discord.ui.Modal, title="Edit Game Information"):

    def __init__(self, cog, personnel):
        super().__init__()

        self.cog = cog
        self.personnel = personnel

        self.steam_username = discord.ui.TextInput(
            label="Steam Username",
            default=personnel["steam_username"] or "",
            required=True,
            max_length=100
        )

        self.steam_uid = discord.ui.TextInput(
            label="Steam64 ID",
            default=personnel["steam_uid"],
            required=True,
            max_length=30
        )

        self.dayz_name = discord.ui.TextInput(
            label="DayZ Username",
            default=personnel["dayz_name"],
            required=True,
            max_length=100
        )

        self.add_item(self.steam_username)
        self.add_item(self.steam_uid)
        self.add_item(self.dayz_name)

    async def on_submit(self, interaction: discord.Interaction):

        try:
            self.cog.personnel_manager.update_personnel(
                personnel_id=self.personnel["personnel_id"],
                full_name=self.personnel["full_name"],
                display_name=self.personnel["display_name"],
                callsign=self.personnel["callsign"],
                steam_username=self.steam_username.value,
                steam_uid=self.steam_uid.value,
                dayz_name=self.dayz_name.value,
                position=self.personnel["position"],
                ambassador=self.personnel["ambassador"],
                status=self.personnel["status"],
                notes=self.personnel["notes"],
                performed_by=str(interaction.user)
            )

            await interaction.response.send_message(
                "Game information updated successfully."
            )

        except Exception as error:
            await interaction.response.send_message(
                f"Personnel update failed: {error}"
            )

class MilitaryEditModal(discord.ui.Modal, title="Edit Military Information"):

    def __init__(self, cog, personnel):
        super().__init__()

        self.cog = cog
        self.personnel = personnel

        self.position = discord.ui.TextInput(
            label="Position",
            default=personnel["position"] or "",
            required=False,
            max_length=100
        )

        self.ambassador = discord.ui.TextInput(
            label="Ambassador (Yes or No)",
            default="Yes" if personnel["ambassador"] else "No",
            required=True,
            max_length=3
        )

        self.add_item(self.position)
        self.add_item(self.ambassador)

    async def on_submit(self, interaction: discord.Interaction):

        ambassador_value = self.ambassador.value.strip().lower()

        if ambassador_value not in ("yes", "no"):
            await interaction.response.send_message(
                "Ambassador must be either `Yes` or `No`."
            )
            return

        try:
            self.cog.personnel_manager.update_personnel(
                personnel_id=self.personnel["personnel_id"],
                full_name=self.personnel["full_name"],
                display_name=self.personnel["display_name"],
                callsign=self.personnel["callsign"],
                steam_username=self.personnel["steam_username"],
                steam_uid=self.personnel["steam_uid"],
                dayz_name=self.personnel["dayz_name"],
                position=self.position.value or None,
                ambassador=ambassador_value == "yes",
                status=self.personnel["status"],
                notes=self.personnel["notes"],
                performed_by=str(interaction.user)
            )

            await interaction.response.send_message(
                "Military information updated successfully."
            )

        except Exception as error:
            await interaction.response.send_message(
                f"Personnel update failed: {error}"
            )

class StatusEditModal(discord.ui.Modal, title="Edit Status & Notes"):

    def __init__(self, cog, personnel):
        super().__init__()

        self.cog = cog
        self.personnel = personnel

        self.status = discord.ui.TextInput(
            label="Status",
            default=personnel["status"],
            required=True,
            max_length=20
        )

        self.notes = discord.ui.TextInput(
            label="Notes",
            default=personnel["notes"] or "",
            required=False,
            style=discord.TextStyle.paragraph,
            max_length=1000
        )

        self.add_item(self.status)
        self.add_item(self.notes)

    async def on_submit(self, interaction: discord.Interaction):

        status = self.status.value.strip()

        valid_statuses = (
            "Active",
            "Inactive",
            "AWOL",
            "Discharged",
            "Deceased"
        )

        if status not in valid_statuses:
            await interaction.response.send_message(
                "Invalid status. Use one of:\n"
                "`Active`, `Inactive`, `AWOL`, "
                "`Discharged`, `Deceased`"
            )
            return

        try:
            self.cog.personnel_manager.update_personnel(
                personnel_id=self.personnel["personnel_id"],
                full_name=self.personnel["full_name"],
                display_name=self.personnel["display_name"],
                callsign=self.personnel["callsign"],
                steam_username=self.personnel["steam_username"],
                steam_uid=self.personnel["steam_uid"],
                dayz_name=self.personnel["dayz_name"],
                position=self.personnel["position"],
                ambassador=self.personnel["ambassador"],
                status=status,
                notes=self.notes.value or None,
                performed_by=str(interaction.user)
            )

            await interaction.response.send_message(
                "Status and notes updated successfully."
            )

        except Exception as error:
            await interaction.response.send_message(
                f"Personnel update failed: {error}"
            )

class PersonnelEditSelect(discord.ui.Select):

    def __init__(self, cog, personnel):

        self.cog = cog
        self.personnel = personnel

        options = [
            discord.SelectOption(
                label="Identity",
                description="Edit name, display name, and callsign.",
                emoji="👤"
            ),
            discord.SelectOption(
                label="Game Information",
                description="Edit Steam and DayZ information.",
                emoji="🎮"
            ),
            discord.SelectOption(
                label="Military",
                description="Edit position and ambassador status.",
                emoji="🎖️"
            ),
            discord.SelectOption(
                label="Status & Notes",
                description="Edit status and personnel notes.",
                emoji="📋"
            )
        ]

        super().__init__(
            placeholder="Select what you want to edit...",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        if self.values[0] == "Identity":
            await interaction.response.send_modal(
                IdentityEditModal(
                    self.cog,
                    self.personnel
                )
            )

        elif self.values[0] == "Game Information":
            await interaction.response.send_modal(
                GameEditModal(
                    self.cog,
                    self.personnel
                )
            )

        elif self.values[0] == "Military":
            await interaction.response.send_modal(
                MilitaryEditModal(
                    self.cog,
                    self.personnel
                )
            )

        elif self.values[0] == "Status & Notes":
            await interaction.response.send_modal(
                StatusEditModal(
                    self.cog,
                    self.personnel
                )
            )

class PersonnelEditView(discord.ui.View):

    def __init__(self, cog, personnel):
        super().__init__(timeout=120)

        self.add_item(
            PersonnelEditSelect(
                cog,
                personnel
            )
        )

class Personnel(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.database = DatabaseManager()
        self.database.initialize()

        self.personnel_manager = PersonnelManager(self.database)

    personnel = app_commands.Group(
        name="personnel",
        description="Personnel management commands."
    )

    @personnel.command(
        name="create",
        description="Create a new personnel record."
    )
    @app_commands.describe(
        member="The Discord member being enlisted.",
        full_name="The recruit's full legal name.",
        steam_username="The recruit's Steam username.",
        steam_uid="The recruit's Steam64 ID.",
        dayz_name="The recruit's DayZ username.",
        branch="The branch the recruit is joining."
    )
    @app_commands.choices(
        branch=[
            app_commands.Choice(
                name="Chernarus Defense Forces",
                value="CDF"
            ),
            app_commands.Choice(
                name="Chernarus Ground Defense Forces",
                value="CGDF"
            ),
            app_commands.Choice(
                name="Chernarus Air Defense Forces",
                value="CADF"
            ),
            app_commands.Choice(
                name="Chernarus Naval Defense Forces",
                value="CNDF"
            ),
            app_commands.Choice(
                name="Chernarus Special Operations Group",
                value="CSOG"
            ),
            app_commands.Choice(
                name="Chernarus State Security",
                value="CSS"
            )
        ]
    )
    async def create(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        full_name: str,
        steam_username: str,
        steam_uid: str,
        dayz_name: str,
        branch: app_commands.Choice[str]
    ):

        try:

            # Find the selected branch in the database.
            self.database.cursor.execute(
                """
                SELECT branch_id
                FROM branches
                WHERE prefix = ?
                """,
                (branch.value,)
            )

            branch_result = self.database.cursor.fetchone()

            if branch_result is None:
                await interaction.response.send_message(
                    "The selected branch could not be found in the database.",
                    ephemeral=False
                )
                return

            branch_id = branch_result[0]

            personnel_id, service_id = (
                self.personnel_manager.create_personnel(
                    discord_member=member,
                    full_name=full_name,
                    steam_username=steam_username,
                    steam_uid=steam_uid,
                    dayz_name=dayz_name,
                    branch_id=branch_id
                )
            )

            await interaction.response.send_message(
                (
                    "Personnel record successfully created.\n\n"
                    f"Personnel ID: `{personnel_id:06d}`\n"
                    f"Service ID: `{service_id}`\n"
                    f"Member: {member.mention}\n"
                    f"Branch: `{branch.value}`\n"
                    "Rank: `Training | Recruit in Training`\n"
                    "Status: `Active`"
                ),
                ephemeral=False
            )

        except ValueError as error:

            await interaction.response.send_message(
                f"Personnel creation failed: {error}",
                ephemeral=False
            )

        except Exception:

            await interaction.response.send_message(
                "An unexpected error occurred while creating the personnel record.",
                ephemeral=False
            )

            raise

    @personnel.command(
        name="view",
        description="View a personnel record."
    )
    @app_commands.describe(
        member="The personnel member to view."
    )
    async def view(
        self,
        interaction: discord.Interaction,
        member: discord.Member = None
       ):
        await interaction.response.defer()

        target = member or interaction.user

        personnel = self.personnel_manager.get_personnel(target.id)

        if personnel is None:
            await interaction.followup.send(
                f"No personnel record was found for {target.mention}."
            )
            return

        personnel_id = personnel[0]

        service_history = self.personnel_manager.get_service_history(
            personnel_id
        )

        previous_service_ids = []

        for service_id, branch, start_date, end_date in service_history:
            if end_date:
                previous_service_ids.append(
                    f"• `{service_id}` — {branch} "
                    f"({start_date} to {end_date})"
                )
            else:
                previous_service_ids.append(
                    f"• `{service_id}` — {branch} "
                    f"({start_date} to Present)"
                )

        if previous_service_ids:
            service_history_display = "\n".join(previous_service_ids)
        else:
            service_history_display = "None"

        (
            personnel_id,
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
            notes,
            branch_name,
            branch_prefix,
            rank_name,
            rank_code,
            rank_pay
        ) = personnel

        callsign_display = callsign if callsign else "None"
        position_display = position if position else "None"

        ambassador_display = "Yes" if ambassador else "No"

        payroll_display = "Yes" if payroll_eligible else "No"

        last_seen_display = last_seen if last_seen else "Never"

        steam_profile = (
            f"https://steamcommunity.com/profiles/{steam_uid}"
            if steam_uid
            else "None"
        )

        qualifications = (
            "None"
        )

        profile = (
            f"**Personnel ID:**\n"
            f"`{personnel_id:06d}`\n\n"

            f"**Discord**\n"
            f"--------\n"
            f"**Discord User:**\n"
            f"{target.mention}\n\n"
            f"**Discord Username:**\n"
            f"{discord_username}\n\n"
            f"**Discord ID:**\n"
            f"{discord_id}\n\n"

            f"**Military**\n"
            f"--------\n"
            f"**Full Name:**\n"
            f"{full_name}\n\n"
            f"**Display Name:**\n"
            f"{display_name}\n\n"
            f"**Callsign:**\n"
            f"{callsign_display}\n\n"
            f"**Branch:**\n"
            f"{branch_prefix} | {branch_name}\n\n"
            f"**Rank:**\n"
            f"{rank_code} | {rank_name}\n\n"
            f"**Current Service ID:**\n"
            f"{current_service_id}\n\n"
            f"**Service History:**\n"
            f"{service_history_display}\n\n"
            f"**Position:**\n"
            f"{position_display}\n\n"
            f"**Ambassador:**\n"
            f"{ambassador_display}\n\n"

            f"**Steam**\n"
            f"-----\n"
            f"**Steam Username:**\n"
            f"{steam_username or 'None'}\n\n"
            f"**Steam64 ID:**\n"
            f"{steam_uid}\n\n"
            f"**Steam Profile:**\n"
            f"{steam_profile}\n\n"

            f"**DayZ**\n"
            f"----\n"
            f"**DayZ Username:**\n"
            f"{dayz_name}\n\n"

            f"**Status**\n"
            f"------\n"
            f"**Status:**\n"
            f"{status}\n\n"
            f"**Date Joined:**\n"
            f"{date_joined}\n\n"
            f"**Last Seen:**\n"
            f"{last_seen_display}\n\n"

            f"**Activity**\n"
            f"--------\n"
            f"**Weekly Active Hours:**\n"
            f"{weekly_active_hours:.1f}\n\n"
            f"**Monthly Active Hours:**\n"
            f"{monthly_active_hours:.1f}\n\n"
            f"**Sessions This Week:**\n"
            f"{sessions_this_week}\n\n"
            f"**Payroll Eligible:**\n"
            f"{payroll_display}\n\n"
            f"**Payroll Balance:**\n"
            f"₽{payroll_balance:,}\n\n"

            f"**Qualifications**\n"
            f"--------------\n"
            f"{qualifications}\n\n"

            f"**Notes**\n"
            f"-----\n"
            f"{notes or 'None'}"
        )

        await interaction.followup.send(profile)
        
    @personnel.command(
        name="transfer",
        description="Transfer personnel to another branch."
    )
    @app_commands.describe(
        member="The personnel member to transfer.",
        branch="The prefix of the destination branch."
    )
    async def transfer(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        branch: str
    ):
        await interaction.response.defer()

        personnel = self.personnel_manager.get_personnel(member.id)

        if personnel is None:
            await interaction.followup.send(
                f"No personnel record was found for {member.mention}."
            )
            return

        personnel_id = personnel[0]

        self.database.cursor.execute(
            """
            SELECT
                branch_id,
                prefix,
                name
            FROM branches
            WHERE prefix = ?
              AND active = 1
            """,
            (branch.upper(),)
        )

        target_branch = self.database.cursor.fetchone()

        if target_branch is None:
            await interaction.followup.send(
                f"Branch `{branch.upper()}` does not exist "
                f"or is inactive."
            )
            return

        try:
            result = self.personnel_manager.transfer_personnel(
                personnel_id,
                target_branch["branch_id"],
                str(interaction.user)
            )

        except ValueError as error:
            await interaction.followup.send(
                f"Transfer failed: {error}"
            )
            return

        await interaction.followup.send(
            f"**Personnel Transfer Completed.**\n\n"
            f"**Personnel ID:**\n"
            f"`{personnel_id:06d}`\n\n"
            f"**Member:**\n"
            f"{member.mention}\n\n"
            f"**Previous Service ID:**\n"
            f"`{result['old_service_id']}`\n\n"
            f"**New Service ID:**\n"
            f"`{result['new_service_id']}`\n\n"
            f"**New Branch:**\n"
            f"{result['new_branch_name']}\n\n"
            f"**Transfer Date:**\n"
            f"{result['date']}\n\n"
            f"**Transferred By:**\n"
            f"{interaction.user.mention}"
        )

    @personnel.command(
        name="edit",
        description="Edit a personnel record."
    )
    @app_commands.describe(
        member="The personnel member to edit."
    )
    async def edit(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):

        await interaction.response.defer()

        personnel = self.personnel_manager.get_personnel(
            member.id
        )

        if personnel is None:
            await interaction.followup.send(
                f"No personnel record was found for "
                f"{member.mention}."
            )
            return

        personnel_data = {
            "personnel_id": personnel[0],
            "full_name": personnel[3],
            "display_name": personnel[4],
            "callsign": personnel[5],
            "steam_username": personnel[6],
            "steam_uid": personnel[7],
            "dayz_name": personnel[8],
            "position": personnel[11],
            "ambassador": personnel[12],
            "status": personnel[13],
            "notes": personnel[22]
        }

        await interaction.followup.send(
            f"**Edit Personnel Record**\n\n"
            f"Personnel ID: `{personnel[0]:06d}`\n"
            f"Member: {member.mention}\n\n"
            f"Select a category below to edit.",
            view=PersonnelEditView(
                self,
                personnel_data
            )
        )

    def _is_commander(self, discord_id):
        personnel = self.personnel_manager.get_personnel(discord_id)

        if personnel is None:
            return False

        return personnel[26] == "COMMANDER"

    @personnel.command(
        name="promote",
        description="Promote a personnel member."
    )
    @app_commands.describe(
        member="The personnel member to promote.",
        rank="The rank they are being promoted to."
    )
    @app_commands.choices(rank=RANK_CHOICES)
    async def promote(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        rank: app_commands.Choice[str]
    ):
        if not self._is_commander(interaction.user.id):
            await interaction.response.send_message(
                "Only the current Commander of the Chernarus Defense "
                "Forces may promote personnel.",
                ephemeral=True
            )
            return

        target = self.personnel_manager.get_personnel(member.id)

        if target is None:
            await interaction.response.send_message(
                f"No personnel record was found for {member.mention}.",
                ephemeral=True
            )
            return

        try:
            self.personnel_manager.change_rank(
                personnel_id=target[0],
                new_rank_code=rank.value,
                performed_by=str(interaction.user),
                change_type="Promotion"
            )

            await interaction.response.send_message(
                f"{member.mention} has been promoted to `{rank.value}` "
                f"by {interaction.user.mention}."
            )

        except ValueError as error:
            await interaction.response.send_message(
                f"Promotion failed: {error}",
                ephemeral=True
            )

    @personnel.command(
        name="demote",
        description="Demote a personnel member."
    )
    @app_commands.describe(
        member="The personnel member to demote.",
        rank="The rank they are being demoted to."
    )
    @app_commands.choices(rank=RANK_CHOICES)
    async def demote(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        rank: app_commands.Choice[str]
    ):
        if not self._is_commander(interaction.user.id):
            await interaction.response.send_message(
                "Only the current Commander of the Chernarus Defense "
                "Forces may demote personnel.",
                ephemeral=True
            )
            return

        target = self.personnel_manager.get_personnel(member.id)

        if target is None:
            await interaction.response.send_message(
                f"No personnel record was found for {member.mention}.",
                ephemeral=True
            )
            return

        try:
            self.personnel_manager.change_rank(
                personnel_id=target[0],
                new_rank_code=rank.value,
                performed_by=str(interaction.user),
                change_type="Demotion"
            )

            await interaction.response.send_message(
                f"{member.mention} has been demoted to `{rank.value}` "
                f"by {interaction.user.mention}."
            )

        except ValueError as error:
            await interaction.response.send_message(
                f"Demotion failed: {error}",
                ephemeral=True
            )

    @personnel.command(
        name="appoint",
        description="Appoint a member to a Joint Chiefs of Staff rank."
    )
    @app_commands.describe(
        member="The personnel member being appointed.",
        rank="The JCS appointment being granted."
    )
    @app_commands.choices(rank=JCS_RANK_CHOICES)
    async def appoint(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        rank: app_commands.Choice[str]
    ):
        if not self._is_commander(interaction.user.id):
            await interaction.response.send_message(
                "Only the current Commander of the Chernarus Defense "
                "Forces may make JCS appointments.",
                ephemeral=True
            )
            return

        target = self.personnel_manager.get_personnel(member.id)

        if target is None:
            await interaction.response.send_message(
                f"No personnel record was found for {member.mention}.",
                ephemeral=True
            )
            return

        try:
            self.personnel_manager.appoint_rank(
                personnel_id=target[0],
                new_rank_code=rank.value,
                performed_by=str(interaction.user)
            )

            await interaction.response.send_message(
                f"{member.mention} has been appointed to "
                f"**{rank.name}** by {interaction.user.mention}."
            )

        except ValueError as error:
            await interaction.response.send_message(
                f"Appointment failed: {error}",
                ephemeral=True
            )

    @personnel.command(
        name="bootstrap-commander",
        description="Assign the initial Commander of the CDF."
    )
    async def bootstrap_commander(
        self,
        interaction: discord.Interaction
    ):
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message(
                "Only the Discord bot owner may use this command.",
                ephemeral=True
            )
            return

        try:
            self.personnel_manager.bootstrap_commander(
                discord_id=interaction.user.id,
                performed_by=str(interaction.user)
            )

            await interaction.response.send_message(
                "The initial Commander of the Chernarus Defense Forces "
                "has been assigned to your personnel record."
            )

        except ValueError as error:
            await interaction.response.send_message(
                f"Commander assignment failed: {error}",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Personnel(bot))