import os

from dotenv import load_dotenv

from cmpms.core.bot import CMPMSBot
from cmpms.utils.logger import setup_logger

from cmpms.config.manager import ConfigManager

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    raise RuntimeError("DISCORD_TOKEN was not found in the .env file.")

bot = CMPMSBot()

bot.run(TOKEN)

logger = setup_logger()

logger.info("CMPMS starting...")

config = ConfigManager()