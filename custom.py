# -*- coding: utf-8 -*-
"""
Цей файл — для тих, хто "виріс" з bot_config.py і хоче власну логіку на Python
(aiogram handlers), якій не місце в простому конфізі.

За замовчуванням файл порожній — рушій працює без жодних правок тут.
Функція register(router, bot) викликається рушієм один раз при старті,
ще ПЕРЕД тим, як підключаються команди/кнопки/keywords з bot_config.py —
тож твої власні обробники мають пріоритет.

Два приклади нижче закомічені. Щоб увімкнути — просто розкоментуй.
"""

from aiogram import Router, Bot


def register(router: Router, bot: Bot) -> None:
    """Реєстрація власних обробників. За потреби — додай свої нижче."""

    # Приклад 1: власна команда /roll — кидає кубик.
    #
    # import random
    # from aiogram.filters import Command
    # from aiogram.types import Message
    #
    # @router.message(Command("roll"))
    # async def roll_dice(message: Message) -> None:
    #     await message.answer(f"🎲 Випало: {random.randint(1, 6)}")

    # Приклад 2: власна реакція на фото від користувача.
    #
    # from aiogram.types import Message
    #
    # @router.message(lambda m: m.photo is not None)
    # async def on_photo(message: Message) -> None:
    #     await message.answer("Гарне фото! 📸")

    return None
