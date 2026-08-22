import discord
from discord import app_commands
from discord.ext import commands

from cmpms.managers.personnel_manager import PersonnelManager
from cmpms.database.database import DatabaseManager


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
        target = member or interaction.user

        personnel = self.personnel_manager.get_personnel(target.id)

        if personnel is None:
            await interaction.response.send_message(
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

        await interaction.response.send_message(profile)


async def setup(bot):
    await bot.add_cog(Personnel(bot))