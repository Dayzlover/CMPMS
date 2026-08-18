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


async def setup(bot):
    await bot.add_cog(Personnel(bot))