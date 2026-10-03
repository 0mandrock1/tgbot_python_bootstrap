"""Load and validate the bot token from .env, without ever touching the network."""

import os
import re

from dotenv import dotenv_values

TOKEN_RE = re.compile(r"^\d+:[\w-]{30,}$")


class TokenError(Exception):
    """Raised when BOT_TOKEN is missing or clearly malformed."""


def load_token(env_path: str = ".env") -> str:
    if not os.path.exists(env_path):
        raise TokenError(
            "Не знайдено файл .env. Скопіюй .env.example у .env і встав туди "
            "токен бота, отриманий у @BotFather."
        )

    token = dotenv_values(env_path).get("BOT_TOKEN")

    if not token or token in ("", "вставте_токен_сюди", "your_token_here"):
        raise TokenError(
            "У файлі .env не вказано BOT_TOKEN. Відкрий .env у блокноті й встав "
            "токен, отриманий у @BotFather, у рядок BOT_TOKEN=..."
        )

    if not TOKEN_RE.match(token):
        raise TokenError(
            "Токен у .env виглядає неправильно. Токен має вигляд '123456789:AAAA...' "
            "— візьми коректний токен у @BotFather (команда /mybots → вибери бота → API Token)."
        )

    return token
