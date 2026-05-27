# DrunkBotX

A Discord bot built for a friend group. It responds to chat messages with AI, handles RSVP boards for board game nights, tracks bowling beer-buying duty, and sends match-day reminders for volleyball.

## Features

| Extension | What it does |
|---|---|
| `message_response` | AI chat via OpenAI (`hey drunkbot` / `hey db`), random emoji reactions, nickname substitutions |
| `board_game_night` | Interactive RSVP board with Attend/Decline buttons; auto-posts every 2 weeks |
| `bowling_stats` | `/bowl_beers` — tracks which bowler owes the second-round beers each Thursday night |
| `volleyball` | Sends a match-day notification at 9 AM for scheduled volleyball games |
| `user_commands` | `/who` — pings a user with a file vault link |

## Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (package manager)
- Docker + Docker Compose (for container deployment)
- A Discord bot token with the required permissions (see below)
- An OpenAI API key (optional — only needed for AI chat responses)

## Setup

**1. Clone and install dependencies**

```bash
git clone <repo-url>
cd DrunkBotX
uv sync
```

**2. Create `app/config.json`**

```json
{
  "BOT": {
    "TIMEZONE": "America/Chicago",
    "CHANNELS": {
      "GENERAL": "<channel_id>"
    }
  },
  "MESSAGES": {
    "NICKNAMES": {
      "TOMMY": ["Big Tom", "The Tominator"],
      "LINDA": ["Lin-dawg"]
    }
  },
  "OPENAI": {
    "PROMPT": "Your name is Drunkbot. Respond by..."
  }
}
```

`BOT.TIMEZONE` and `BOT.CHANNELS.GENERAL` are required. Extensions that depend on them will unload at startup if they are missing. `MESSAGES.NICKNAMES` and `OPENAI.PROMPT` are optional.

**3. Set environment variables**

Create a `.env` file in the project root (used locally via `python-dotenv`):

```env
BOT_TOKEN=your_discord_bot_token
OPENAI_TOKEN=your_openai_api_key
```

**4. Create storage and log directories**

```bash
mkdir storage logs
```

The `bowling_stats` extension reads and writes `storage/bowling_stats.json`. The `volleyball` extension reads `storage/volleyball_matches.json` (see format below).

## Running Locally

```bash
uv run python app/bot.py
```

## Docker Deployment

The `docker-compose.yaml` expects:

- `./config/config.json` — mounted read-only into the container
- `./storage/` — persistent JSON storage
- `./logs/` — persistent log output
- `BOT_TOKEN` and `OPENAI_TOKEN` set in the environment or a `.env` file

Build and start:

```bash
docker compose up -d
```

## Discord Bot Permissions

**General:**
- `applications.commands`
- `bot`

**Required for `board_game_night` and `message_response`:**
- Send Messages
- Manage Messages

**Required intents:** `DEFAULT` + `MESSAGE_CONTENT`

## Storage File Formats

**`storage/bowling_stats.json`** — auto-managed by the bot:
```json
{
  "Tommy": [1, 3, 7],
  "Linda": [2, 4, 5, 6]
}
```

**`storage/volleyball_matches.json`** — manually maintained:
```json
{
  "2025-06-05 19:30:00": { "court": 3, "team": "The Spikers" },
  "2025-06-12 19:30:00": { "court": 1, "team": "Net Gains" }
}
```

## Adding Extensions

Use `templates/ext_template.py` as a starting point. Drop the new file into `app/ext/` and it will be loaded automatically on next startup.
