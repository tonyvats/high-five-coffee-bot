#!/bin/bash
# Локальный запуск: админка + DEV-бот
# Использует venv и .env (DEV-токен)

cd "$(dirname "$0")"

echo "☕ High Five Coffee — локальный запуск"
echo ""

# Проверяем venv
if [ ! -d "venv" ]; then
    echo "❌ Папка venv не найдена. Создайте её:"
    echo "   python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Останавливаем старые процессы
echo "🔄 Останавливаем предыдущие процессы..."
pkill -f "hfctbot.py" 2>/dev/null
pkill -f "admin.app" 2>/dev/null
lsof -ti :5050 | xargs kill -9 2>/dev/null
sleep 2

# Проверяем .env для DEV-бота
if [ ! -f ".env" ]; then
    echo "⚠️  Файл .env не найден. Бот будет использовать прод-токен."
    echo "   Для DEV-бота создайте .env с BOT_TOKEN=ваш_DEV_токен"
else
    echo "✅ .env найден (DEV-режим)"
fi

# Активируем venv
source venv/bin/activate

# Запускаем админку в фоне
echo ""
echo "🌐 Запуск админ-панели на http://localhost:5050"
python3 -m admin.app > admin.log 2>&1 &
ADMIN_PID=$!
sleep 2

# Запускаем бота в фоне
echo "🤖 Запуск бота (hfctbot.py)..."
python3 hfctbot.py > bot.log 2>&1 &
BOT_PID=$!
sleep 2

# Проверяем, что всё стартовало
if kill -0 $ADMIN_PID 2>/dev/null; then
    echo "✅ Админка запущена (PID $ADMIN_PID)"
else
    echo "❌ Админка не запустилась. Смотрите admin.log"
fi

if kill -0 $BOT_PID 2>/dev/null; then
    echo "✅ Бот запущен (PID $BOT_PID)"
    grep -q "Run polling" bot.log 2>/dev/null && echo "   Polling активен"
else
    echo "❌ Бот не запустился. Смотрите bot.log"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Админка:  http://localhost:5050"
echo "  Пароль:   highfive2024"
echo "  DEV-бот:  @HighFiveCoffeeDevBot (если есть .env)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Логи: tail -f admin.log  |  tail -f bot.log"
echo "🛑 Остановка: ./stop_local.sh  или  kill $ADMIN_PID $BOT_PID"
echo ""
