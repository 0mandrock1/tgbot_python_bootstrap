"""Shared test fixtures: a fake aiogram session that never touches the network."""

from datetime import datetime

import pytest
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.base import BaseSession
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.methods import TelegramMethod
from aiogram.types import Chat, Message, Update, User

TEST_TOKEN = "123456:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"


class FakeSession(BaseSession):
    """Records every API call instead of sending it, and fakes plausible replies."""

    def __init__(self):
        super().__init__()
        self.calls = []
        self.fail_html = False

    async def make_request(self, bot: Bot, method: TelegramMethod, timeout=None):
        if self.fail_html and getattr(method, "parse_mode", None) == ParseMode.HTML:
            self.calls.append(method)
            raise TelegramBadRequest(method=method, message="Bad Request: can't parse entities")

        self.calls.append(method)
        name = type(method).__name__

        if name in ("SendMessage", "SendPhoto"):
            text = getattr(method, "text", None) or getattr(method, "caption", None) or ""
            return Message(
                message_id=len(self.calls),
                date=datetime.now(),
                chat=Chat(id=1, type="private"),
                text=text,
            )
        if name == "GetMe":
            return User(id=1, is_bot=True, first_name="TestBot", username="test_bot")
        return True

    async def close(self) -> None:
        return None

    async def stream_content(self, url, headers=None, timeout=30, chunk_size=65536, raise_for_status=True):
        yield b""

    @property
    def sent_texts(self):
        texts = []
        for m in self.calls:
            t = getattr(m, "text", None) or getattr(m, "caption", None)
            if t is not None:
                texts.append(t)
        return texts


@pytest.fixture
def fake_session():
    return FakeSession()


@pytest.fixture
def bot(fake_session):
    return Bot(
        token=TEST_TOKEN,
        session=fake_session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def make_message(text: str, user_id: int = 111, chat_id: int = 111, message_id: int = 1) -> Update:
    return Update(
        update_id=message_id,
        message=Message(
            message_id=message_id,
            date=datetime.now(),
            chat=Chat(id=chat_id, type="private"),
            from_user=User(id=user_id, is_bot=False, first_name="Tester"),
            text=text,
        ),
    )


@pytest.fixture
def dispatcher_factory():
    def _make(router):
        dp = Dispatcher()
        dp.include_router(router)
        return dp

    return _make
