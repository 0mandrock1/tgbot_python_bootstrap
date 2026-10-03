import types

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

from engine.router import build_router
from tests.conftest import make_message

EMPTY_CUSTOM = types.SimpleNamespace()


def base_cfg(**overrides):
    cfg = {
        "texts": {"start": "Вітаю!", "help": "Довідка:", "unknown": "Не зрозумів", "autoHelp": True},
        "commands": [
            {"command": "about", "description": "про бота", "reply": "Простий бот"},
            {
                "command": "cat",
                "description": "котик",
                "reply": {
                    "text": "Міяу",
                    "photo": "http://example.com/cat.jpg",
                    "links": [{"text": "Сайт", "url": "http://example.com"}],
                },
            },
            {"command": "broken", "description": "зламаний html", "reply": "a < b"},
            {"command": "long", "description": "довгий текст", "reply": "x" * 5000},
        ],
        "buttons": [[{"text": "Кнопка", "reply": "Натиснуто"}]],
        "keywords": [{"words": ["дякую"], "reply": "Будь ласка"}],
        "adminIds": [],
        "notifyAdminsOnStart": False,
    }
    cfg.update(overrides)
    return cfg


async def feed(dispatcher_factory, bot, cfg, text, custom=EMPTY_CUSTOM):
    dp = dispatcher_factory(build_router(cfg, custom, bot))
    await dp.feed_update(bot, make_message(text))


async def test_start_sends_greeting_with_keyboard(dispatcher_factory, bot, fake_session):
    await feed(dispatcher_factory, bot, base_cfg(), "/start")
    assert "Вітаю!" in fake_session.sent_texts
    last_call = fake_session.calls[-1]
    assert isinstance(last_call.reply_markup, ReplyKeyboardMarkup)


async def test_help_lists_commands_when_autohelp(dispatcher_factory, bot, fake_session):
    await feed(dispatcher_factory, bot, base_cfg(), "/help")
    full_text = "\n".join(fake_session.sent_texts)
    assert "/about" in full_text
    assert "/start" in full_text
    assert "/id" in full_text


async def test_id_returns_numeric_user_id(dispatcher_factory, bot, fake_session):
    await feed(dispatcher_factory, bot, base_cfg(), "/id")
    assert fake_session.sent_texts[-1] == "111"


async def test_config_command_replies(dispatcher_factory, bot, fake_session):
    await feed(dispatcher_factory, bot, base_cfg(), "/about")
    assert fake_session.sent_texts[-1] == "Простий бот"


async def test_button_exact_match(dispatcher_factory, bot, fake_session):
    await feed(dispatcher_factory, bot, base_cfg(), "Кнопка")
    assert fake_session.sent_texts[-1] == "Натиснуто"


async def test_keyword_whole_word_case_insensitive(dispatcher_factory, bot, fake_session):
    await feed(dispatcher_factory, bot, base_cfg(), "Дякую")
    assert fake_session.sent_texts[-1] == "Будь ласка"


async def test_keyword_partial_word_does_not_match(dispatcher_factory, bot, fake_session):
    await feed(dispatcher_factory, bot, base_cfg(), "недякую")
    assert fake_session.sent_texts[-1] == "Не зрозумів"


async def test_unknown_message_gets_unknown_reply(dispatcher_factory, bot, fake_session):
    await feed(dispatcher_factory, bot, base_cfg(), "qwerty123")
    assert fake_session.sent_texts[-1] == "Не зрозумів"


async def test_empty_unknown_stays_silent(dispatcher_factory, bot, fake_session):
    cfg = base_cfg(texts={"start": "s", "help": "h", "unknown": "", "autoHelp": False})
    before = len(fake_session.calls)
    await feed(dispatcher_factory, bot, cfg, "qwerty123")
    assert len(fake_session.calls) == before


async def test_reply_with_photo_and_links(dispatcher_factory, bot, fake_session):
    await feed(dispatcher_factory, bot, base_cfg(), "/cat")
    photo_calls = [c for c in fake_session.calls if type(c).__name__ == "SendPhoto"]
    assert len(photo_calls) == 1
    assert photo_calls[0].caption == "Міяу"
    assert isinstance(photo_calls[0].reply_markup, InlineKeyboardMarkup)


async def test_broken_html_falls_back_to_plain_text(dispatcher_factory, bot, fake_session):
    fake_session.fail_html = True
    await feed(dispatcher_factory, bot, base_cfg(), "/broken")
    assert fake_session.sent_texts[-1] == "a < b"


async def test_long_text_is_split_under_limit(dispatcher_factory, bot, fake_session):
    await feed(dispatcher_factory, bot, base_cfg(), "/long")
    long_calls = [t for t in fake_session.sent_texts if len(t) > 0]
    assert len(long_calls) >= 2
    assert all(len(t) <= 4096 for t in long_calls)
