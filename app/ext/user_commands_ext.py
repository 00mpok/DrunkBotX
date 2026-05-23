import interactions
import logging

log = logging.getLogger(__name__)

# ======================================================================================================================
# EXTENSION
# ======================================================================================================================
class UserCommands(interactions.Extension):
    def __init__(self, bot: interactions.Client, config: dict):
        super().__init__()
        self.bot = bot
        self.config = config

    """ LISTENERS ___________________________________________________________________________________________________"""
    @interactions.listen()
    async def on_startup(self):
        log.info("UserCommands Extension Loaded.")

    """ TASKS _______________________________________________________________________________________________________"""

    """ EXTENSION COMMANDS __________________________________________________________________________________________"""
    @interactions.slash_command(
        name="who",
        description="Automates Cody's Doctor Who pod file notification to Jake"
    )
    @interactions.slash_option(
        name="target_user",
        description="The user that will receive the command",
        required=True,
        opt_type=interactions.OptionType.USER,
    )
    async def who(self, inter: interactions.SlashContext, target_user: interactions.User):
        await inter.send(f"https://vault.nuenthel.com\n{target_user.mention} 👆 right there")

# ======================================================================================================================
# FUNCTIONS
# ======================================================================================================================

# ======================================================================================================================
# CLASSES
# ======================================================================================================================