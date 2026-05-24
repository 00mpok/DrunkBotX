# DrunkBotX

## Install
```bash
git clone $directory; cd $directory
 ```

This project uses `uv` as for project management. Run `sync` to sync the project on your host.
```bash
uv sync
```

## Configuration
This bot requires a configuration file that must either be in the /src directory as config.json
Here is a sample config.json file. Items marked with an asterisk are required. Remove the 
asterisk once the value has been filled in.

```json
{
  "BOT": {
    "TIMEZONE*": "America/Chicago",
    "CHANNELS": {
      "GENERAL*": "<channel_id>"
    }
  },
  "MESSAGES": {
    "NICKNAMES": {
      "TOMMY": ["Nickname"],
      "LINDA": ["Nickname"]
    }
  },
  "OPENAI": {
    "PROMPT": "Your name is Drunkbot. Respond by..."
  }
}
```

 ## Bot Permissions
General Permissions:
 * applications.commands
 * bot

 board_game_night extension:
  * Send Messages
  * Manage Messages

 message_response extension:
  * Send Messages
  * Manage Messages

## Docker Compose File
Here is a sample docker-compose.yaml file.
```yaml
---
services:
  drunkbot:
    build: .
    container_name: drunkbot
    restart: always
```

## Build and Run Container
Build and start the container by executing the following command:
```bash
docker compose up -d
```

