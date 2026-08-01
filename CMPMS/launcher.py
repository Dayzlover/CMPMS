import os

from dotenv import load_dotenv

from cmpms.core.bot import CMPMSBot
from cmpms.utils.logger import setup_logger
from cmpms.config.manager import ConfigManager
from cmpms.database.database import DatabaseManager
from cmpms.managers.branch_manager import BranchManager

load_dotenv()

logger = setup_logger()
logger.info("[SYSTEM] CMPMS starting...")

config = ConfigManager()
logger.info("[CONFIG] Configuration loaded.")

database = DatabaseManager()
database.initialize()
logger.info("[DATABASE] SQLite initialized successfully.")
branches = BranchManager(database)
branches.synchronize()

logger.info("[BRANCHES] Branch database synchronized.")
TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    raise RuntimeError("DISCORD_TOKEN was not found in the .env file.")

bot = CMPMSBot()

bot.run(TOKEN)