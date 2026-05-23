import interactions
import logging
import random
import openai
import os
from functools import wraps
from typing import Callable

log = logging.getLogger(__name__)

# ======================================================================================================================
# EXTENSION
# ======================================================================================================================
class MessageResponse(interactions.Extension):
    def __init__(self, bot: interactions.Client, config: dict):
        super().__init__()
        self.bot = bot
        self.nicknames = {}
        self.response_val = 0
        self.openai_token = os.getenv("OPENAI_TOKEN")
        self.openai_model = "gpt-5.4-mini"
        self.openai_client = None

        if not config.get("MESSAGES", {}).get("NICKNAMES"):
            log.warning("No NICKNAMES configured, nickname responses will not be sent.")
        else:
            self.nicknames = config["MESSAGES"]["NICKNAMES"]

        if not config.get("OPENAI", {}).get("PROMPT"):
            log.warning("OPENAI prompt configuration missing, chatbot responses will not be sent.")
        elif not self.openai_token:
            log.warning("OPENAI_TOKEN not found in environment variables, chatbot responses will not be sent.")
        else:
            self.openai_prompt = config["OPENAI"]["PROMPT"]
            self.openai_client = openai.OpenAI(api_key=self.openai_token)

    @staticmethod
    def _block_bot_content(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, event: interactions.api.events.MessageCreate, *args, **kwargs):
            if event.message.author.bot:
                return None
            return await func(self, event, *args, **kwargs)
        return wrapper

    """ LISTENERS ___________________________________________________________________________________________________"""
    @interactions.listen()
    async def on_startup(self):
        log.info("MessageResponse Extension Loaded.")

    @interactions.listen()
    @_block_bot_content
    async def chatbot(self, event: interactions.api.events.MessageCreate):
        if not self.openai_client:
            return

        content = event.message.content
        author = event.message.author

        triggers = ["hey drunkbot", "hey db", "drunkbot"]
        if any(t in content.lower() for t in triggers):
            log.info(f"Chatbot Request by {author}: {content}")
            prompt = self.openai_prompt + content.lower()
            response = self.openai_client.responses.create(
                model=self.openai_model,
                input=prompt
            )
            await event.message.channel.send(response.output_text)

    @interactions.listen()
    @_block_bot_content
    async def replies(self, event: interactions.api.events.MessageCreate):
        emoji = random.choice(["👍","✨","💯","🧙","🦄","👆","🥹","🫠","🍆","🫦"])
        roll = random.randint(1, 100)
        if roll < self.response_val:
            log.info(f"Emoji reply triggered. rolled less than {self.response_val} with {roll}.")
            self.response_val = 0
            await event.message.add_reaction(emoji)
        self.response_val += 1

    @interactions.listen()
    @_block_bot_content
    async def absolutely_brilliant_nicknames(self, event: interactions.api.events.MessageCreate):
        if not self.nicknames:
            return

        content = event.message.content
        user_names = [name.lower() for name in self.nicknames.keys()]
        nickname = None
        for user_name in user_names:
            if user_name in [word.lower() for word in content.split(" ")]:
                nickname = random.choice(self.nicknames[user_name.upper()])

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