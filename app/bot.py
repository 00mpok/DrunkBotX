# Main operations for DrunkBot V2
# Interactions documentation can be found here:
# https://interactions-py.github.io/interactions.py/Guides/01%20Getting%20Started/
# Discord documentation can be found here:
# https://discordpy.readthedocs.io/en/stable/

import json
import sys
import interactions
import logging
import os

# Build Required Directories
for path in ["logs", "storage"]:
    if not os.path.exists(path):
        os.makedirs(path)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)-8s - %(filename)s:%(lineno)-5d - %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log", mode="w"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# SLASH COMMANDS _______________________________________________________________________________________________________
def main():
    try:
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        logger.error("Config file 'config.json' not found")
        sys.exit(1)
    except json.decoder.JSONDecodeError:
        logger.error("Config file 'config.json' is malformed, unable to parse JSON")
        sys.exit(1)

    # Create client
    bot = interactions.Client(
        token=config["BOT"]["TOKEN"],
        intents=interactions.Intents.DEFAULT | interactions.Intents.MESSAGE_CONTENT,
        send_command_tracebacks=False,
        auto_defer=True,
        logger=logger,
    )

    # Load ext
    for filename in os.listdir("ext"):
        if filename.endswith(".py"):
            bot.load_extension(f"ext.{filename[:-3]}", config=config)

    # Fire
    bot.start()


if __name__ == "__main__":
    main()
