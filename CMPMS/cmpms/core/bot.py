import discord
from discord.ext import commands
import os
from cmpms.utils.logger import setup_logger


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
        # Initialize logger
        self.logger = setup_logger()

        # Automatically load all cogs
        for file in os.listdir("cmpms/cogs"):
            if file.endswith(".py") and not file.startswith("_"):
                await self.load_extension(f"cmpms.cogs.{file[:-3]}")
                self.logger.info(f"[COG] Loaded: {file[:-3]}")

               # Sync slash commands
        synced_commands = await self.tree.sync()

        self.logger.info("[SYSTEM] Slash commands synchronized.")

        for command in synced_commands:
            self.logger.info(f"[COMMAND] /{command.name}")

            if hasattr(command, "commands"):
                for subcommand in command.commands:
                    self.logger.info(
                        f"[COMMAND] /{command.name} {subcommand.name}"
                    )

    async def on_ready(self):
        self.logger.info("=" * 50)
        self.logger.info("CMPMS READY")
        self.logger.info(f"Logged in as: {self.user}")
        self.logger.info(f"User ID: {self.user.id}")
        self.logger.info("=" * 50)