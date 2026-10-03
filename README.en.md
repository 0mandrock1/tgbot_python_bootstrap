# Telegram bot without programming

A ready-made Telegram bot template. The entire bot is configured through one
file — `bot_config.py`. You never need to open the `engine/` folder.

Out of the box the bot can:
- Respond to commands (`/start`, `/help`, `/id`, plus your own from the config).
- Show a button keyboard and react to keywords in chat.

## Quick start

1. **Get a token.** In Telegram open [@BotFather](https://t.me/BotFather),
   send `/newbot`, give your bot a name — you'll get a token (a string like
   `123456789:AAAa-BBBcccDDDeee...`).
2. **Download the code.** Click the green `Code` button → `Download ZIP` on
   this repository (or `Use this template`) and unzip it.
3. **Paste the token.** In the bot folder find `.env.example`, make a copy
   named `.env`, and paste your token after `BOT_TOKEN=`.
4. **Run it.**
   - Windows: double-click `start.bat`.
   - macOS/Linux: open a terminal in the bot folder and run `sh start.sh`.
5. Message your bot in Telegram with `/start`.

### How to open a terminal if you've never done it

- **Windows**: in the bot folder, hold Shift, right-click empty space →
  "Open PowerShell window here" (or just double-click `start.bat` — no
  terminal needed).
- **macOS**: Finder → go to the bot folder → right-click the folder →
  "Services" → "New Terminal at Folder" (or Spotlight → "Terminal").
- **Linux**: in your file manager — right-click the folder → "Open in
  Terminal".

### If you don't have Python

Download and install it from
[python.org/downloads](https://www.python.org/downloads/). On Windows, make
sure to check "Add python.exe to PATH" during installation.

## "I want X → I edit Y"

| I want... | Edit this section in `bot_config.py` |
|---|---|
| Change the bot's greeting | `texts.start` |
| Change the help text | `texts.help` |
| Add a new command | `commands` |
| Add a button | `buttons` |
| Make the bot react to a word in chat | `keywords` |
| Get notified when the bot starts | `adminIds` + `notifyAdminsOnStart` |

## Recipes

After every change — **save the file and restart the bot**.

### A new command

```python
commands = [
    {
        "command": "weather",
        "description": "Show the weather",
        "reply": "It's sunny today ☀️",
    },
]
```

### A button

```python
buttons = [
    [
        {"text": "☀️ Weather", "reply": "It's sunny today ☀️"},
    ],
]
```

### Reacting to a word

```python
keywords = [
    {"words": ["weather"], "reply": "Want to know the weather? Send /weather"},
]
```

### A reply with an image

```python
commands = [
    {
        "command": "cat",
        "description": "A cat photo",
        "reply": {
            "text": "Here's a cat!",
            "photo": "https://placekitten.com/400/300",
        },
    },
]
```

### A link button

```python
commands = [
    {
        "command": "site",
        "description": "Our website",
        "reply": {
            "text": "Follow the link:",
            "links": [{"text": "Open website", "url": "https://example.com"}],
        },
    },
]
```

## Something broke

| Symptom | Cause | What to do |
|---|---|---|
| "File .env not found" | You forgot to create `.env` from `.env.example` | Copy `.env.example` → `.env`, paste your token |
| "The token in .env looks wrong" | Token doesn't look like a real one | Get the exact token from @BotFather, no extra spaces |
| "Token is invalid" | Wrong or revoked token | Get a new token from @BotFather |
| "Bot is already running elsewhere" | The bot is already running in another window/machine | Close the other copy of the bot |
| "Config error: ..." | A mistake in `bot_config.py` | The message names the section and value — fix exactly that |
| The bot doesn't respond | The process isn't running or crashed | Run `start.sh` / `start.bat` again, check the terminal messages |
| I changed the config but nothing happened | The bot wasn't restarted | Stop the bot (Ctrl+C) and start it again |

## Keeping the bot running 24/7

As long as `start.sh`/`start.bat` is running on your computer, the bot works.
Turn off your computer — the bot turns off too. To keep it running all the
time, host it on a server:

- **Linux server**: copy `deploy/tgbot.service` to `/etc/systemd/system/`,
  fix the paths inside, then run `systemctl enable --now tgbot`.
- **Any OS**: you can use [pm2](https://pm2.keymetrics.io/)
  (`pm2 start bot.py --interpreter .venv/bin/python`).

## Outgrew the config

Once `bot_config.py` isn't flexible enough, write your own code in
`custom.py` (it already has two commented-out examples inside). It's plain
Python using [aiogram](https://docs.aiogram.dev/) — the library that powers
the engine.

## Your token is a password

Never publish your token or share it with anyone. The `.env` file is
intentionally listed in `.gitignore` so it never ends up in git. If your
token ever leaks, revoke it in @BotFather (`/mybots` → your bot → "API
Token" → "Revoke current token") and get a new one.
