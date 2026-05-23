import interactions
import logging
import random
import openai

logger = logging.getLogger(__name__)

# ======================================================================================================================
# EXTENSION
# ======================================================================================================================
class MessageResponse(interactions.Extension):
    def __init__(self, bot: interactions.Client, config: dict):
        super().__init__()
        self.bot = bot
        self.config = config
        self.respond_nicknames = True
        self.respond_chatbot = True
        self.response_val = 0

        if not self.config.get("MESSAGES", {}).get("NICKNAMES"):
            logger.warning("No NICKNAMES configured, preventing nickname responses...")
            self.respond_nicknames = False

        if not self.config.get("OPENAI", {}).get("TOKEN") or not self.config.get("OPENAI", {}).get("PROMPT"):
            logger.warning("OPENAI configurations missing, preventing chatbot responses...")
            self.respond_chatbot = False
        else:
            self.chatbot = openai.OpenAI(api_key=self.config["OPENAI"]["TOKEN"])

    """ LISTENERS ___________________________________________________________________________________________________"""
    @interactions.listen()
    async def on_startup(self):
        logger.info("MessageResponse Extension Loaded.")

    @interactions.listen()
    async def chatbot(self, event: interactions.api.events.MessageCreate):
        if not self.respond_chatbot:
            return

        content = event.message.content
        author = event.message.author

        if author.bot:
            return

        if "hey drunkbot" in content.lower() or "hey db" in content.lower():
            logger.info(f"Chatbot Request by {author}: {content}")
            prompt = self.config["OPENAI"]["PROMPT"] + content.lower()
            response = self.chatbot.responses.create(
                model="gpt-4o-mini",
                input=prompt
            )
            await event.message.channel.send(response.output_text)

    @interactions.listen()
    async def replies(self, event: interactions.api.events.MessageCreate):
        emoji = random.choice(["👍","👎","🥺","💯","🍆","🫦"])
        roll = random.randint(1, 100)
        if roll < self.response_val:
            logger.info(f"Message responded by {emoji} {roll} at {self.response_val}; Roll: {roll}")
            self.response_val = 0
            await event.message.add_reaction(emoji)
        self.response_val += 1

    @interactions.listen()
    async def nicknames(self, event: interactions.api.events.MessageCreate):
        if not self.respond_nicknames:
            return

        content = event.message.content
        author = event.message.author

        if author.bot:
            return

        nicknames = self.config["MESSAGES"]["NICKNAMES"]
        user_names = [name.lower() for name in nicknames.keys()]

        nickname = None
        for user_name in user_names:
            if user_name in [word.lower() for word in content.split(" ")]:
                nickname = random.choice(nicknames[user_name.upper()])

        if nickname:
            await event.message.channel.send(f"Oh, you mean {nickname}?")
    """ TASKS _______________________________________________________________________________________________________"""
    """ EXTENSION COMMANDS __________________________________________________________________________________________"""

# ======================================================================================================================
# FUNCTIONS
# ======================================================================================================================

# ======================================================================================================================
# CLASSES
# ======================================================================================================================