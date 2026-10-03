#!/usr/bin/env python3
"""Тонка точка входу. Вся логіка — у engine/."""

import asyncio
import sys

import bot_config
import custom
from engine.runner import check_only, run


def main() -> int:
    if "--check" in sys.argv:
        return check_only(bot_config)
    return asyncio.run(run(bot_config, custom))


if __name__ == "__main__":
    sys.exit(main())
