from discord import app_commands
from discord.ext import commands


class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="attention",
        description="Checks if the bot is online."
    )
    async def attention(self, interaction):
        await interaction.response.send_message(
            "READY",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(System(bot))