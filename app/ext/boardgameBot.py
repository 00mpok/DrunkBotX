import discord
from discord.ext import commands
from discord import app_commands
import random
import json
import os
from dotenv import load_dotenv

# -----------------------------
# Views for interactive buttons
# -----------------------------

class PickAnotherView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Pick Another", style=discord.ButtonStyle.primary)
    async def pick_another(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not boardgames:
            await interaction.response.send_message("No board games have been added yet!", ephemeral=True)
            return

        game = random.choice(boardgames)

        msg = (
            f"🎲 **{game['name']}**\n"
            f"👥 Players: {game['players']}\n"
            f"⏱️ Playtime: {game['playtime']}\n"
            f"📝 {game['description']}\n"
        )

        if game.get("url"):
            msg += f"▶️ How to play: {game['url']}"

        await interaction.response.edit_message(content=msg, view=self)
        
class ConfirmDeleteView(discord.ui.View):
    def __init__(self, game_name):
        super().__init__(timeout=30)
        self.game_name = game_name

    @discord.ui.button(label="Confirm Delete", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        for game in boardgames:
            if game["name"].lower() == self.game_name.lower():
                boardgames.remove(game)
                save_game()
                await interaction.response.edit_message(
                    content=f"🗑️ Deleted **{self.game_name}**.",
                    view=None
                )
                return

        await interaction.response.edit_message(
            content=f"❌ Game **{self.game_name}** not found.",
            view=None
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❎ Deletion canceled.", view=None)
        
class GamesPaginator(discord.ui.View):
    def __init__(self, games, per_page=5):
        super().__init__(timeout=None)
        self.games = games
        self.per_page = per_page
        self.page = 0

    def format_page(self):
        start = self.page * self.per_page
        end = start + self.per_page
        chunk = self.games[start:end]

        msg = f"**🎲 Stored Board Games (Page {self.page + 1}/{self.total_pages})**\n\n"
        for i, game in enumerate(chunk, start=start + 1):
            msg += (
                f"**{i}. {game['name']}** — "
                f"{game['players']} players, "
                f"{game['playtime']} min\n"
                f"📝 {game['description']}\n\n"
            )
        return msg

    @property
    def total_pages(self):
        return (len(self.games) - 1) // self.per_page + 1

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(content=self.format_page(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page < self.total_pages - 1:
            self.page += 1
            await interaction.response.edit_message(content=self.format_page(), view=self)

# -----------------------------
# JSON SAVE / LOAD
# -----------------------------

def save_game():
    with open('Boardgame bot/boardgames.json', 'w') as f:
        json.dump(boardgames, f, indent=4)

def load_games():
    global boardgames
    try:
        with open('Boardgame bot/boardgames.json', 'r') as f:
            boardgames = json.load(f)
    except FileNotFoundError:
        boardgames = []

load_games()

# -----------------------------
# BOT SETUP
# -----------------------------

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree  # Slash command tree

# -----------------------------
# AUTOCOMPLETE HELPERS
# -----------------------------

async def game_name_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=game["name"], value=game["name"])
        for game in boardgames
        if current.lower() in game["name"].lower()
    ][:25]

# -----------------------------
# SLASH COMMANDS
# -----------------------------

# ADD GAME
@tree.command(name="addgame", description="Add a new board game")
@app_commands.describe(
    name="Name of the game",
    players="Number of players (e.g., 2-4)",
    playtime="Average playtime (e.g., 60-90)",
    description="Short description of the game",
    url="Optional how-to-play video URL"
)
async def addgame(interaction: discord.Interaction, name: str, players: str, playtime: str, description: str, url: str | None = None):

    # Duplicate check
    for game in boardgames:
        if game["name"].lower() == name.lower():
            await interaction.response.send_message(f"❌ A game named **{name}** already exists.", ephemeral=True)
            return

    game = {
        "name": name,
        "players": players,
        "playtime": playtime,
        "description": description,
        "url": url
    }

    boardgames.append(game)
    save_game()

    await interaction.response.send_message(f"Added **{name}** to the list!")
   
# BULK ADD 
@tree.command(name="bulkadd", description="Bulk add multiple board games at once")
@app_commands.describe(
    games_text="Paste multiple lines: name | players | playtime | description | optional URL #"
)
async def bulkadd(interaction: discord.Interaction, games_text: str):
    lines = games_text.split("#")
    added = []
    skipped = []

    for line in lines:
        parts = [p.strip() for p in line.split("|")]

        if len(parts) < 4:
            skipped.append((line, "Not enough fields"))
            continue

        name = parts[0]

        # Duplicate check
        if any(g["name"].lower() == name.lower() for g in boardgames):
            skipped.append((name, "Duplicate"))
            continue

        game = {
            "name": name,
            "players": parts[1],
            "playtime": parts[2],
            "description": parts[3],
            "url": parts[4] if len(parts) > 4 else None
        }

        boardgames.append(game)
        added.append(name)

    save_game()

    msg = f"📥 **Bulk Add Results**\n\n"
    if added:
        msg += "✅ Added:\n" + "\n".join(f"- {g}" for g in added) + "\n\n"
    if skipped:
        msg += "⚠️ Skipped:\n" + "\n".join(f"- {g} ({reason})" for g, reason in skipped)

    await interaction.response.send_message(msg)
    
@tree.command(name="bulkaddfile", description="Bulk add board games from an uploaded text file, format: name | players | playtime | description | optional URL")
@app_commands.describe(file="Upload a .txt file with one game per line, format: name | players | playtime | description | optional URL")
async def bulkaddfile(interaction: discord.Interaction, file: discord.Attachment):

    # Validate file type
    if not file.filename.lower().endswith(".txt"):
        await interaction.response.send_message(
            "❌ Please upload a `.txt` file containing your game list. Format: `name | players | playtime | description | optional URL` (one game per line).",
            ephemeral=True
        )
        return

    # Read file contents
    content = await file.read()
    text = content.decode("utf-8")

    lines = text.split("\n")
    added = []
    skipped = []

    for line in lines:
        if not line.strip():
            continue  # skip blank lines

        parts = [p.strip() for p in line.split("|")]

        # Must have at least: name | players | playtime | description
        if len(parts) < 4:
            skipped.append((line, "Not enough fields"))
            continue

        name = parts[0]
        players = parts[1]
        playtime = parts[2]
        description = parts[3]
        url = parts[4] if len(parts) > 4 and parts[4].strip() else None

        # Duplicate check
        if any(g["name"].lower() == name.lower() for g in boardgames):
            skipped.append((name, "Duplicate"))
            continue

        game = {
            "name": name,
            "players": players,
            "playtime": playtime,
            "description": playtime,
            "url": url
        }

        boardgames.append(game)
        added.append(name)

    save_game()

    # Build response
    msg = "📥 **Bulk Add Results**\n\n"

    if added:
        msg += "✅ **Added:**\n" + "\n".join(f"- {g}" for g in added) + "\n\n"

    if skipped:
        msg += "⚠️ **Skipped:**\n" + "\n".join(f"- {g} ({reason})" for g, reason in skipped)

    await interaction.response.send_message(msg)


# PICK GAME
@tree.command(name="pickgame", description="Pick a random board game")
async def pickgame(interaction: discord.Interaction):
    if not boardgames:
        await interaction.response.send_message("No board games have been added yet!")
        return

    game = random.choice(boardgames)

    msg = (
        f"🎲 **{game['name']}**\n"
        f"👥 Players: {game['players']}\n"
        f"⏱️ Playtime: {game['playtime']}\n"
        f"📝 {game['description']}\n"
    )

    if game.get("url"):
        msg += f"▶️ How to play: {game['url']}"

    await interaction.response.send_message(msg, view=PickAnotherView())

# LIST GAMES
@tree.command(name="listgames", description="List all stored board games")
async def listgames(interaction: discord.Interaction):
    if not boardgames:
        await interaction.response.send_message("No games have been added yet.")
        return

    view = GamesPaginator(boardgames, per_page=5)
    await interaction.response.send_message(view.format_page(), view=view)

# EDIT GAME (with working autocomplete + field dropdown)
@tree.command(name="editgame", description="Edit a game's field")
@app_commands.describe(
    field="Field to edit",
    game_name="Name of the game to edit",
    new_value="New value"
)
@app_commands.choices(field=[
    app_commands.Choice(name="Name", value="name"),
    app_commands.Choice(name="Players", value="players"),
    app_commands.Choice(name="Playtime", value="playtime"),
    app_commands.Choice(name="Description", value="description"),
    app_commands.Choice(name="URL", value="url")
])
@app_commands.autocomplete(game_name=game_name_autocomplete)
async def editgame(
    interaction: discord.Interaction,
    field: app_commands.Choice[str],
    game_name: str,
    new_value: str
):
    field_name = field.value

    for game in boardgames:
        if game["name"].lower() == game_name.lower():
            old_value = game[field_name]
            game[field_name] = new_value
            save_game()

            await interaction.response.send_message(
                f"Updated **{game['name']}**:\n"
                f"**{field_name.capitalize()}** changed from `{old_value}` to `{new_value}`"
            )
            return

    await interaction.response.send_message(
        f"❌ No game named **{game_name}** was found.",
        ephemeral=True
    )

# DELETE GAME
@tree.command(name="deletegame", description="Delete a game by name")
@app_commands.autocomplete(game_name=game_name_autocomplete)
async def deletegame(interaction: discord.Interaction, game_name: str):
    await interaction.response.send_message(
        f"Are you sure you want to delete **{game_name}**?",
        view=ConfirmDeleteView(game_name)
    )

# SEARCH BY NAME
@tree.command(name="searchgame", description="Search games by name")
async def searchgame(interaction: discord.Interaction, name: str):
    results = [
        game for game in boardgames
        if name.lower() in game["name"].lower()
    ]

    if not results:
        await interaction.response.send_message(f"No games found matching **{name}**.")
        return

    msg = f"🔍 **Games matching '{name}':**\n\n"
    for game in results:
        msg += f"**{game['name']}** — {game['players']} players, {game['playtime']} min\n"

    await interaction.response.send_message(msg)

# SEARCH BY PLAYERS
@tree.command(name="searchplayers", description="Search games by number of players")
async def searchplayers(interaction: discord.Interaction, player_query: str):
    results = []

    for game in boardgames:
        players = game["players"].replace(" ", "").replace("–", "-")
        query = player_query.replace(" ", "").replace("–", "-")

        # Exact number
        if query.isdigit():
            if "-" in players:
                low, high = players.split("-")
                if low.isdigit() and high.isdigit():
                    if int(low) <= int(query) <= int(high):
                        results.append(game)
            else:
                if players == query:
                    results.append(game)

        # Range search
        elif "-" in query:
            try:
                q_low, q_high = query.split("-")
                if q_low.isdigit() and q_high.isdigit():
                    if "-" in players:
                        low, high = players.split("-")
                        if low.isdigit() and high.isdigit():
                            if int(high) >= int(q_low) and int(low) <= int(q_high):
                                results.append(game)
            except:
                pass

    if not results:
        await interaction.response.send_message(f"No games found for **{player_query} players**.")
        return

    msg = f"👥 **Games for {player_query} players:**\n\n"
    for game in results:
        msg += f"**{game['name']}** — {game['players']} players\n"

    await interaction.response.send_message(msg)

# SEARCH BY TIME
@tree.command(name="searchtime", description="Search games by playtime")
async def searchtime(interaction: discord.Interaction, time_query: str):
    results = []

    def parse_range(value):
        value = value.replace(" ", "").replace("–", "-")
        if "-" in value:
            low, high = value.split("-")
            return int(low), int(high)
        return int(value), int(value)

    try:
        q_low, q_high = parse_range(time_query)
    except:
        await interaction.response.send_message("Use minutes or a range like `60` or `30-90`.")
        return

    for game in boardgames:
        try:
            g_low, g_high = parse_range(game["playtime"])
            if g_high >= q_low and g_low <= q_high:
                results.append(game)
        except:
            continue

    if not results:
        await interaction.response.send_message(f"No games found with playtime **{time_query} minutes**.")
        return

    msg = f"⏱️ **Games with playtime {time_query} minutes:**\n\n"
    for game in results:
        msg += f"**{game['name']}** — {game['playtime']} min\n"

    await interaction.response.send_message(msg)

# -----------------------------
# BOT READY
# -----------------------------

# @bot.event
# async def on_ready():
#     guild = discord.Object(id=705812118657695764)
#     # print(guild)
#     try:
#         await tree.sync()
#         #guild=guild
#         print("Commands synced")
#     except Exception as e:
#         print("Sync error:", e)
    
    # # DELETE all existing guild commands
    # tree.clear_commands(guild=guild)
    # await tree.sync(guild=guild)

    # print(f"Commands cleared and resynced for {bot.user}")

# -----------------------------
# RUN BOT
# -----------------------------

# load_dotenv()
# token = os.getenv("DISCORD_TOKEN")
# bot.run(token)
