"""Validate bot_config.py content before touching the network. Pure functions, no I/O."""

import re

BUILTIN_COMMANDS = {"start", "help", "id"}
COMMAND_RE = re.compile(r"^[a-z0-9_]{1,32}$")
MAX_DESCRIPTION_LEN = 256


class ConfigError(Exception):
    """Raised with a Ukrainian, human-readable message naming the broken section/value."""


def _reply_is_empty(reply) -> bool:
    if reply is None:
        return True
    if isinstance(reply, str):
        return reply.strip() == ""
    if isinstance(reply, dict):
        return str(reply.get("text", "")).strip() == ""
    return True


def validate_config(cfg: dict) -> None:
    """Raise ConfigError on the first broken rule found."""
    _validate_texts(cfg.get("texts", {}))
    _validate_commands(cfg.get("commands", []))
    _validate_buttons(cfg.get("buttons", []))
    _validate_keywords(cfg.get("keywords", []))
    _validate_admin_ids(cfg.get("adminIds", []))


def _validate_texts(texts: dict) -> None:
    for key in ("start", "help", "unknown"):
        if key not in texts:
            raise ConfigError(f"Секція texts: відсутній обов'язковий ключ '{key}'.")
        if not isinstance(texts[key], str):
            raise ConfigError(f"Секція texts: значення '{key}' має бути текстом (рядком).")
    if "autoHelp" in texts and not isinstance(texts["autoHelp"], bool):
        raise ConfigError("Секція texts: 'autoHelp' має бути true або false.")
    if texts["start"].strip() == "":
        raise ConfigError("Секція texts: 'start' не може бути порожнім.")
    if texts["help"].strip() == "":
        raise ConfigError("Секція texts: 'help' не може бути порожнім.")


def _validate_commands(commands: list) -> None:
    seen = set()
    for item in commands:
        name = item.get("command", "")
        description = item.get("description", "")
        reply = item.get("reply")

        if not COMMAND_RE.match(name):
            raise ConfigError(
                f"Секція commands: назва команди '{name}' неправильна. "
                "Дозволені лише малі латинські літери, цифри та '_' (1-32 символи)."
            )
        if name in BUILTIN_COMMANDS:
            raise ConfigError(
                f"Секція commands: назва '{name}' уже використовується вбудованою командою "
                "(/start, /help або /id). Обери іншу назву."
            )
        if name in seen:
            raise ConfigError(f"Секція commands: команда '{name}' вказана двічі.")
        seen.add(name)

        if len(description) > MAX_DESCRIPTION_LEN:
            raise ConfigError(
                f"Секція commands: description команди '{name}' довший за "
                f"{MAX_DESCRIPTION_LEN} символів."
            )
        if _reply_is_empty(reply):
            raise ConfigError(f"Секція commands: у команди '{name}' порожня відповідь (reply).")


def _validate_buttons(rows: list) -> None:
    seen_texts = set()
    for row in rows:
        for btn in row:
            text = btn.get("text", "")
            reply = btn.get("reply")
            if text.strip() == "":
                raise ConfigError("Секція buttons: у кнопки порожній текст.")
            if _reply_is_empty(reply):
                raise ConfigError(f"Секція buttons: у кнопки '{text}' немає відповіді (reply).")
            if text in seen_texts:
                raise ConfigError(f"Секція buttons: текст кнопки '{text}' повторюється двічі.")
            seen_texts.add(text)


def _validate_keywords(keywords: list) -> None:
    for item in keywords:
        words = item.get("words", [])
        reply = item.get("reply")
        if not words:
            raise ConfigError("Секція keywords: у правила відсутній список 'words'.")
        if _reply_is_empty(reply):
            raise ConfigError(
                f"Секція keywords: для слів {words} немає відповіді (reply)."
            )


def _validate_admin_ids(admin_ids: list) -> None:
    for admin_id in admin_ids:
        if not isinstance(admin_id, int):
            raise ConfigError(
                f"Секція adminIds: значення '{admin_id}' має бути числом (Telegram ID), не текстом."
            )
