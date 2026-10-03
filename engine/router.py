"""Build the aiogram Router from bot_config.py. Pure wiring, testable without network."""

import logging
import re

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import (
    ErrorEvent,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

from engine.text import split_text

logger = logging.getLogger("engine")

BUILTIN_DESCRIPTIONS = {
    "start": "Почати спілкування з ботом",
    "help": "Показати список команд",
    "id": "Дізнатись свій Telegram ID",
}


def build_reply_keyboard(rows):
    if not rows:
        return None
    keyboard_rows = [[KeyboardButton(text=btn["text"]) for btn in row] for row in rows]
    return ReplyKeyboardMarkup(keyboard=keyboard_rows, resize_keyboard=True)


def build_inline_keyboard(links):
    if not links:
        return None
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=link["text"], url=link["url"])] for link in links]
    )


def _reply_parts(reply):
    if isinstance(reply, str):
        return reply, None, None
    return reply.get("text", ""), reply.get("photo"), reply.get("links")


async def _send_chunks(message: Message, caption_chunk, photo, rest_chunks, keyboard, parse_mode):
    """Send photo (if any) + text chunks, attaching the link keyboard to the very last message."""
    last_is_photo = photo is not None and not rest_chunks
    if photo is not None:
        await message.answer_photo(
            photo=photo,
            caption=caption_chunk or None,
            parse_mode=parse_mode,
            reply_markup=keyboard if last_is_photo else None,
        )
    for i, chunk in enumerate(rest_chunks):
        markup = keyboard if i == len(rest_chunks) - 1 else None
        await message.answer(chunk, parse_mode=parse_mode, reply_markup=markup)


async def send_reply(message: Message, reply) -> None:
    """Send a config reply: text (HTML, split at 4096), optional photo, optional link buttons.

    Falls back to plain text if the configured HTML is malformed (Telegram 400).
    """
    text, photo, links = _reply_parts(reply)
    keyboard = build_inline_keyboard(links)
    chunks = split_text(text) if text else [""]
    caption_chunk, rest_chunks = (chunks[0], chunks[1:]) if photo else (None, chunks)

    try:
        await _send_chunks(message, caption_chunk, photo, rest_chunks, keyboard, "HTML")
    except TelegramBadRequest:
        logger.warning(
            "Telegram відхилив HTML-розмітку в тексті відповіді (перевір теги типу <3 чи a < b). "
            "Надсилаю як звичайний текст."
        )
        await _send_chunks(message, caption_chunk, photo, rest_chunks, keyboard, None)


def _build_help_text(cfg: dict) -> str:
    help_text = cfg["texts"]["help"]
    if not cfg["texts"].get("autoHelp"):
        return help_text

    lines = [help_text, ""]
    for name in ("start", "help", "id"):
        lines.append(f"/{name} - {BUILTIN_DESCRIPTIONS[name]}")
    for item in cfg["commands"]:
        lines.append(f"/{item['command']} - {item['description']}")
    return "\n".join(lines)


def _whole_word_match(words, text: str) -> bool:
    lowered = text.lower()
    for word in words:
        if re.search(r"(?<!\w)" + re.escape(word.lower()) + r"(?!\w)", lowered):
            return True
    return False


def build_router(cfg: dict, custom_module=None, bot=None) -> Router:
    router = Router()

    if custom_module is not None and hasattr(custom_module, "register"):
        custom_module.register(router, bot)

    @router.message(Command("start"))
    async def cmd_start(message: Message) -> None:
        keyboard = build_reply_keyboard(cfg["buttons"])
        chunks = split_text(cfg["texts"]["start"])
        try:
            for i, chunk in enumerate(chunks):
                markup = keyboard if i == len(chunks) - 1 else None
                await message.answer(chunk, parse_mode="HTML", reply_markup=markup)
        except TelegramBadRequest:
            for i, chunk in enumerate(chunks):
                markup = keyboard if i == len(chunks) - 1 else None
                await message.answer(chunk, parse_mode=None, reply_markup=markup)

    @router.message(Command("help"))
    async def cmd_help(message: Message) -> None:
        await send_reply(message, _build_help_text(cfg))

    @router.message(Command("id"))
    async def cmd_id(message: Message) -> None:
        await message.answer(str(message.from_user.id))

    for item in cfg["commands"]:
        def make_handler(reply):
            async def handler(message: Message) -> None:
                await send_reply(message, reply)
            return handler

        router.message.register(make_handler(item["reply"]), Command(item["command"]))

    button_replies = {}
    for row in cfg["buttons"]:
        for btn in row:
            button_replies[btn["text"]] = btn["reply"]

    if button_replies:
        @router.message(F.text.in_(button_replies.keys()))
        async def on_button(message: Message) -> None:
            await send_reply(message, button_replies[message.text])

    keyword_rules = cfg["keywords"]

    @router.message(F.text)
    async def on_text(message: Message) -> None:
        for rule in keyword_rules:
            if _whole_word_match(rule["words"], message.text):
                await send_reply(message, rule["reply"])
                return
        unknown = cfg["texts"].get("unknown", "")
        if unknown.strip():
            await send_reply(message, unknown)

    @router.error()
    async def on_error(event: ErrorEvent) -> None:
        logger.exception("Помилка під час обробки повідомлення", exc_info=event.exception)

    return router
