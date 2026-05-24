import datetime
import logging
import interactions
import dataclasses
import pytz

log = logging.getLogger(__name__)

# ======================================================================================================================
# EXTENSION
# ======================================================================================================================
class BoardGames(interactions.Extension):
    def __init__(self, bot: interactions.Client, config: dict) -> None:
        super().__init__()
        self.bot = bot
        self.config = config
        self.bgn = BoardGameNight()
        self.timezone = config.get("BOT", {}).get("TIMEZONE")
        self.general_channel = config.get("BOT", {}).get("CHANNELS", {}).get("GENERAL")

        if not self.timezone:
            log.warning("No TIMEZONE configured, unloading BoardGames extension...")
            self.bot.unload_extension(self.__module__)
        if not self.general_channel:
            log.warning("No CHANNELS.GENERAL configured, unloading BoardGames extension...")
            self.bot.unload_extension(self.__module__)

    """ LISTENERS ___________________________________________________________________________________________________"""
    @interactions.listen()
    async def on_startup(self):
        log.info("BoardGameNight Extension Ready.")
        # self.board_game_night_task.start() Disabled for the season

    @interactions.listen(interactions.api.events.Component)
    async def on_component(self, event: interactions.api.events.Component):
        ext, res = event.ctx.custom_id.split(".")
        if ext == "bgn":
            match res:
                case "attending":
                    self.bgn.add_attendee(event.ctx.user.display_name, True)
                    emb, com = self.bgn.build_board()
                    await event.ctx.edit_origin(embed=emb, components=com)

                case "declined":
                    self.bgn.add_attendee(event.ctx.user.display_name, False)
                    emb, com = self.bgn.build_board()
                    await event.ctx.edit_origin(embed=emb, components=com)

                case _:
                    log.warning("Unhandled board game night component event custom id: %s", event)

    """ TASKS _______________________________________________________________________________________________________"""
    @interactions.Task.create(interactions.IntervalTrigger(minutes=1))
    async def board_game_night_task(self):
        tz = pytz.timezone(self.timezone)
        base_date = tz.localize(datetime.datetime(year=2024, month=9, day=2))
        now = datetime.datetime.now(tz=tz)

        diff = now - base_date

        if diff.days % 14 == 0 and now.hour == 8 and now.minute == 0:
            general_channel = self.bot.get_channel(self.config["BOT"]["CHANNELS"]["GENERAL"])
            self.bgn.reset()
            base, components = self.bgn.build_board()
            msg = await general_channel.send(embed=base, components=components)
            self.bgn.set_message(msg)

    """ EXTENSION COMMANDS __________________________________________________________________________________________"""
    @interactions.slash_command(
        name="game_night",
        description="Display board game night board"
    )
    async def game_night(self, inter: interactions.SlashContext):
        self.bgn.reset()
        embed, components = self.bgn.build_board()
        msg = await inter.send(embed=embed, components=components)
        self.bgn.set_message(msg)

# ======================================================================================================================
# FUNCTIONS
# ======================================================================================================================


# ======================================================================================================================
# CLASSES
# ======================================================================================================================

class BoardGameNight:
    def __init__(self):
        self.attendees = []
        self.message = None

    @dataclasses.dataclass
    class Attendee:
        username: str
        status: str

    def add_attendee(self, username: str, status: bool):
        for attendee in self.attendees:
            if attendee.username == username:
                attendee.status = "Attending" if status else "Declined"
                return

        atd = self.Attendee(username=username, status="Attending" if status else "Declined")
        self.attendees.append(atd)

    def build_board(self):
        base = interactions.Embed(
            title="Boardgame Night",
            description="*Tempus tandem est.*",
            color=interactions.Color.random()
        )
        for attendee in self.attendees:
            base.add_field(name=attendee.username, value=attendee.status)

        components = [
            interactions.Button(
                custom_id="bgn.attending",
                style=interactions.ButtonStyle.GREEN,
                label="Attending",
            ),
            interactions.Button(
                custom_id="bgn.declined",
                style=interactions.ButtonStyle.RED,
                label="Decline"),
        ]
        return base, components

    def reset(self):
        self.attendees = []

    def set_message(self, message: interactions.Message):
        self.message = message