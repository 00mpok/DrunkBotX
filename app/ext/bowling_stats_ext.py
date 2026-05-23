import datetime
import logging
import interactions
import os
import json
import dataclasses
import pytz

# Set logger
logger = logging.getLogger(__name__)

# ======================================================================================================================
# EXTENSION
# ======================================================================================================================
class BowlingStats(interactions.Extension):
    def __init__(self, bot: interactions.Client, config: dict) -> None:
        super().__init__()
        self.bot = bot
        self.config = config
        self.thursday_night_bowl_notification = True
        self.timezone = config.get("BOT", {}).get("TIMEZONE")
        self.general_channel = config.get("BOT", {}).get("CHANNELS", {}).get("GENERAL")

        if not self.timezone:
            logger.warning("No TIMEZONE configured, preventing Thursday night bowl beers task")
            self.thursday_night_bowl_notification = False
        if not self.general_channel:
            logger.warning("No CHANNELS.GENERAL configured, preventing Thursday night bowl beers task")
            self.thursday_night_bowl_notification = False

        if os.path.exists("storage/bowling_stats.json"):
            with open("storage/bowling_stats.json", "r") as f:
                stats = json.load(f)
                logger.info(f"BowlingStats loaded for {', '.join(stats.keys())}")

            self.bowlers = [BowlingStats.Bowler(k, v) for k, v in stats.items()]
            self.week = max([week for bowler in self.bowlers for week in bowler.weeks_purchased]) + 1
            logger.info(f"BowlingStats current week {self.week}")

        else:
            logger.info("No BowlingStats storage file detected, creating new file.")
            with open("storage/bowling_stats.json", "w") as f:
                json.dump({}, f, indent=2)
            logger.info("BowlingStats storage file created.")

            self.bowlers = []
            self.week = 1


    @dataclasses.dataclass()
    class Bowler:
        name: str
        weeks_purchased: list

    """ LISTENERS ___________________________________________________________________________________________________"""
    @interactions.listen()
    async def on_startup(self):
        logger.info("BowlingStats Extension Loaded")
        self.bowling_beers_task.start()

    @interactions.listen(interactions.api.events.Component)
    async def on_component(self, event: interactions.api.events.Component):
        ext, res = event.ctx.custom_id.split(".")
        if ext == "bowl":
            match res:
                case "bowler_beer_selector":
                    if event.ctx.values[0] == "Cancel":
                        await event.ctx.edit_origin(
                            embed=interactions.Embed(title="Bowling Beers", description="Canceled"),
                            components=[]
                        )
                        return

                    if event.ctx.values[0] == "New":
                        new_bowler_modal = interactions.Modal(
                            interactions.ShortText(label="Name", custom_id="name"),
                            title="Add New Bowler"
                        )
                        await event.ctx.send_modal(modal=new_bowler_modal)
                        modal_ctx: interactions.ModalContext = await event.ctx.bot.wait_for_modal(new_bowler_modal)

                        name = modal_ctx.responses["name"].title()
                        bowler = BowlingStats.Bowler(name=name, weeks_purchased=[self.week])
                        self.bowlers.append(bowler)

                        logger.info(f"New bowler {name} has been selected for beer round; week {self.week}.")
                        self.week += 1

                        base = build_bowler_beer_board(self.bowlers, bowler)
                        await modal_ctx.send(embed=base)
                        await event.ctx.delete()

                    else:
                        for bowler in self.bowlers:

                            if bowler.name == event.ctx.values[0]:
                                logger.info(f"{bowler.name} has been selected for beer round; week {self.week}.")
                                bowler.weeks_purchased.append(self.week)
                                self.week += 1

                                base = build_bowler_beer_board(self.bowlers, bowler.name)
                                await event.ctx.edit_origin(embed=base, components=[])
                                break

                    with open("storage/bowling_stats.json", "w") as f:
                        data = {bowler.name: bowler.weeks_purchased for bowler in self.bowlers}
                        json.dump(data, f)
                        logger.info(f"BowlingStats file updated. {data}")

    """ TASKS _______________________________________________________________________________________________________"""
    @interactions.Task.create(interactions.IntervalTrigger(minutes=1))
    async def bowling_beers_task(self):
        tz = pytz.timezone(self.timezone)
        now = datetime.datetime.now(tz=tz)
        general_channel = self.bot.get_channel(self.config["BOT"]["CHANNELS"]["GENERAL"])

        if now.weekday() == 3 and now.hour == 20 and now.minute == 35 and self.thursday_night_bowl_notification:
            await bowl_beers_selector_handler(
                bowlers=self.bowlers,
                inter=general_channel
            )

    """ EXTENSION COMMANDS __________________________________________________________________________________________"""
    @interactions.slash_command(
        name="bowl_beers",
        description="Tracks the counts of the bowler who has to pay on second round"
    )
    async def bowl_beers(self, inter: interactions.SlashContext):
        await bowl_beers_selector_handler(
            bowlers=self.bowlers,
            inter=inter
        )


# ======================================================================================================================
# FUNCTIONS
# ======================================================================================================================
async def bowl_beers_selector_handler(bowlers: list, inter):
    base = interactions.Embed(
        title="Bowling Beers",
        description="Well who is the shitter tonight?",
        color=interactions.Color.random()
    )

    options = [bowler.name for bowler in bowlers]
    options.append("New")  # Add a new bowler
    options.append("Cancel")  # Cancel selection

    components = interactions.StringSelectMenu(
        *options,
        custom_id="bowl.bowler_beer_selector",
        placeholder="Select a Beer Buyin' Bowler"
    )
    return await inter.send(embed=base, components=components)

def build_bowler_beer_board(
        bowlers: list[BowlingStats.Bowler],
        selected_bowler: BowlingStats.Bowler) -> interactions.Embed:
    stats = [f"{'Bowler':<9}{'Beers':>3}", "---------------"]
    stats.extend(
        f"{bowler.name:<7}{len(bowler.weeks_purchased):>5}"
        for bowler
        in bowlers
    )
    return interactions.Embed(
        title="",
        description=f"Yeesh, sorry {selected_bowler.name}... git gud.\n" + f"```{'\n'.join(stats)}```"
    )


# ======================================================================================================================
# CLASSES
# ======================================================================================================================
