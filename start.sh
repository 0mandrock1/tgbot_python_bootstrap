#!/bin/sh
# Запуск бота на Linux/macOS. Просто виконай: sh start.sh

set -e
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Не знайдено Python 3. Встанови його з https://www.python.org/downloads/ і спробуй знову."
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "Перший запуск: створюю віртуальне оточення і ставлю залежності..."
    python3 -m venv .venv
    .venv/bin/pip install --quiet --upgrade pip
    .venv/bin/pip install --quiet -r requirements.txt
fi

if [ ! -f ".env" ]; then
    echo "Не знайдено .env. Копіюю .env.example у .env."
    cp .env.example .env
    echo "Відкрий файл .env у блокноті й встав туди токен бота, отриманий у @BotFather."
    exit 1
fi

.venv/bin/python bot.py
