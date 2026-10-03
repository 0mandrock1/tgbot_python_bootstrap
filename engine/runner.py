"""Wire config + token into a running aiogram bot, or just validate (--check)."""

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramConflictError, TelegramUnauthorizedError
from aiogram.types import BotCommand

from engine.config_validation import ConfigError, validate_config
from engine.env import TokenError, load_token
from engine.router import BUILTIN_DESCRIPTIONS, build_router

logger = logging.getLogger("engine")


def config_to_dict(module) -> dict:
    return {
        "texts": module.texts,
        "commands": module.commands,
        "buttons": module.buttons,
        "keywords": module.keywords,
        "adminIds": getattr(module, "adminIds", []),
        "notifyAdminsOnStart": getattr(module, "notifyAdminsOnStart", False),
    }


def check_only(config_module) -> int:
    """Validate config without network or a token. Returns a process exit code."""
    cfg = config_to_dict(config_module)
    try:
        validate_config(cfg)
    except ConfigError as e:
        print(f"Помилка конфігурації: {e}")
        return 1
    print("Конфіг коректний.")
    return 0


async def _set_commands(bot: Bot, cfg: dict) -> None:
    commands = [
        BotCommand(command=name, description=BUILTIN_DESCRIPTIONS[name]) for name in ("start", "help", "id")
    ]
    commands += [BotCommand(command=i["command"], description=i["description"]) for i in cfg["commands"]]
    await bot.set_my_commands(commands)


async def _notify_admins(bot: Bot, cfg: dict) -> None:
    if not cfg.get("notifyAdminsOnStart"):
        return
    for admin_id in cfg.get("adminIds", []):
        try:
            await bot.send_message(admin_id, "Бот запущено ✅")
        except Exception:
            logger.exception("Не вдалось надіслати повідомлення адміну %s", admin_id)


async def run(config_module, custom_module, env_path: str = ".env") -> int:
    cfg = config_to_dict(config_module)

    try:
        validate_config(cfg)
    except ConfigError as e:
        print(f"Помилка конфігурації: {e}")
        return 1

    try:
        token = load_token(env_path)
    except TokenError as e:
        print(str(e))
        return 1

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(build_router(cfg, custom_module, bot))

    try:
        await _set_commands(bot, cfg)
        await _notify_admins(bot, cfg)
        await dp.start_polling(bot)
    except TelegramUnauthorizedError:
        print(
            "Токен невірний. Візьми новий токен у @BotFather "
            "(команда /mybots → вибери бота → API Token)."
        )
        return 1
    except TelegramConflictError:
        print("Бот уже запущений деінде (інша копія). Зупини другу копію й спробуй знову.")
        return 1
    except KeyboardInterrupt:
        pass
    finally:
        await bot.session.close()

    return 0
