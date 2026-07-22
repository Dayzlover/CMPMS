import discord
from discord.ext import commands
import os


class CMPMSBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True
        intents.message_content = True

        super().__init__(
            command_prefix="!",
            intents=intents
        )

    async def setup_hook(self):
        # Automatically load all cogs
        for file in os.listdir("cmpms/cogs"):
            if file.endswith(".py") and not file.startswith("_"):
                await self.load_extension(f"cmpms.cogs.{file[:-3]}")

        # Sync slash commands
        await self.tree.sync()

        print("Slash commands synchronized.")