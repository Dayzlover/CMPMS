import discord
from discord import app_commands
from discord.ext import commands


class Personnel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    personnel = app_commands.Group(
        name="personnel",
        description="Personnel management commands."
    )

    @personnel.command(
        name="create",
        description="Create a new personnel record."
    )
    async def create(
        self,
        interaction: discord.Interaction
    ):
        await interaction.response.send_message(
            "Personnel creation system is under construction.",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Personnel(bot))