@echo off
chcp 65001 >nul
REM Запуск бота на Windows. Просто двічі клікни на цей файл.

cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Не знайдено Python. Встанови його з https://www.python.org/downloads/ ^(познач "Add python.exe to PATH"^) і спробуй знову.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo Перший запуск: створюю віртуальне оточення і ставлю залежності...
    python -m venv .venv
    .venv\Scripts\pip install --quiet --upgrade pip
    .venv\Scripts\pip install --quiet -r requirements.txt
)

if not exist ".env" (
    echo Не знайдено .env. Копіюю .env.example у .env.
    copy .env.example .env >nul
    echo Відкрий файл .env у блокноті й встав туди токен бота, отриманий у @BotFather.
    pause
    exit /b 1
)

.venv\Scripts\python bot.py
pause
