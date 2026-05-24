# Extensions template

import logging
import interactions
import json
import pytz

from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

# Set logger
log = logging.getLogger(__name__)

# Pathing
_BASE = Path(__file__).parent.parent

# ======================================================================================================================
# EXTENSION
# ======================================================================================================================
class Volleyball(interactions.Extension):
    def __init__(self, bot: interactions.Client, config: dict) -> None:
        super().__init__()
        self.matches = []
        self.timezone = config.get("BOT", {}).get("TIMEZONE")
        self.general_channel = config.get("BOT", {}).get("CHANNELS", {}).get("GENERAL")
        self._load_matches()

        if not self.timezone:
            log.warning("No TIMEZONE configured, falling back to UTC.")
            self.timezone = "UTC"

    @dataclass
    class Match:
        dt: datetime
        court: int
        team: str

    def _load_matches(self) -> None:
        p = _BASE / "storage" / "volleyball_matches.json"
        if p.exists():
            with open(p, "r") as f:
                matches = json.load(f)
            for k,v in matches.items():
                self.matches.append(
                    self.Match(
                        dt=datetime.strptime(k, "%Y-%m-%d %H:%M:%S"), # 2025-05-23 14:30:00
                        court=v.get("court", -1),
                        team=v.get("team", "Unknown"),
                    )
                )
            log.info(f"Volleyball loaded {len(self.matches)} volleyball matches.")
        else:
            log.warning(f"No volleyball matches found at {p}.")

    """ LISTENERS ___________________________________________________________________________________________________"""
    @interactions.listen()
    async def on_startup(self):
        log.info("Volleyball Extension Ready.")
        self.match_notification.start()

    """ TASKS _______________________________________________________________________________________________________"""
    @interactions.Task.create(interactions.IntervalTrigger(minutes=1))
    async def match_notification(self):
        tz = pytz.timezone(self.timezone)
        now = datetime.now(tz=tz)

        if now.hour != 9 or now.minute != 0:
            return

        general_channel = self.bot.get_channel(self.general_channel)
        for match in list(self.matches):
            if now.date() == match.dt.date():
                await general_channel.send(
                    embed=match_embed(match),
                )
                log.info(f"Match notification sent for {match.dt.strftime('%Y-%m-%d %H:%M')}.")
                self.matches.remove(match)


    """ EXTENSION COMMANDS __________________________________________________________________________________________"""

# ======================================================================================================================
# FUNCTIONS
# ======================================================================================================================
def match_embed(match: Volleyball.Match) -> interactions.Embed:
    base = interactions.Embed(
        title=f"Hub Pub vs. {match.team}",
        description="",
        color=interactions.Color.random(),
    )
    base.add_field(
        name=f"Match Details 🏐",
        value=f"```Time: {match.dt.strftime('%H:%M')}\n"
              f"Court: {match.court}```"
    )
    base.set_footer(
        text="/volleyball"
    )
    return base

# ======================================================================================================================
# CLASSES
# ======================================================================================================================