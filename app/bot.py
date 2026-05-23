# Main operations for DrunkBot V2
# Interactions documentation can be found here:
# https://interactions-py.github.io/interactions.py/Guides/01%20Getting%20Started/
# Discord documentation can be found here:
# https://discordpy.readthedocs.io/en/stable/

import json
import sys
import logging
import dotenv
import os
from pathlib import Path
from interactions import (
    Client,
    Intents,
    listen,
)

# Dev .env loading
dotenv.load_dotenv()

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)-8s - %(filename)s:%(lineno)-5d - %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log", mode="w"),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger(__name__)


# DRUNKBOTX ------------------------------------------------------------------------------------------------------------
class DrunkBotX(Client):
    def __init__(self, **kwargs) -> None:
        token = os.getenv("BOT_TOKEN")
        super().__init__(
            token=token,
            intents=Intents.DEFAULT | Intents.MESSAGE_CONTENT,
            send_command_tracebacks = False,
            auto_defer = True,
            logger = log,
            **kwargs
        )

        self.config = None
        self._load_extensions()
        self.start()

    def _load_config(self):
        try:
            with open('config.json', 'r') as config_file:
                self.config = json.load(config_file)
        except FileNotFoundError:
            log.error("Configuration file missing. Please create a 'config.json' file in the root directory.")
            sys.exit(1)
        except json.decoder.JSONDecodeError:
            log.error("Config file 'config.json' is malformed, unable to parse JSON.")
            sys.exit(1)

    def _load_extensions(self):
        for fp in Path("ext").iterdir():
            if fp.suffix == ".py":
                self.load_extension(f"ext.{fp.stem}", config=self.config)

    @listen()
    async def on_startup(self):
        log.info("Initializing DrunkBotX")
        log.info("-------------------")


if __name__ == "__main__":
    DrunkBotX()
