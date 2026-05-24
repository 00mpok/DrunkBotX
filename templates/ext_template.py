# Extensions template

import logging
import interactions
from pathlib import Path

# Set logger
log = logging.getLogger(__name__)

# Pathing
_BASE = Path(__file__).parent.parent


# ======================================================================================================================
# EXTENSION
# ======================================================================================================================
class DiscordExtension(interactions.Extension):
    def __init__(self, bot: interactions.Client, config: dict) -> None:
        super().__init__()

    """ LISTENERS ___________________________________________________________________________________________________"""
    @interactions.listen()
    async def on_startup(self):
        log.info("<Extension Name> Extension Loaded.")

    """ TASKS _______________________________________________________________________________________________________"""
    @interactions.Task.create(interactions.IntervalTrigger(minutes=1))
    async def example_task(self):
        pass

    """ EXTENSION COMMANDS __________________________________________________________________________________________"""
    @interactions.slash_command(
        name="example_slash_command",
        description="example_slash_command description"
    )
    async def example_slash_command(self, inter: interactions.SlashContext):
        pass

# ======================================================================================================================
# FUNCTIONS
# ======================================================================================================================

# ======================================================================================================================
# CLASSES
# ======================================================================================================================