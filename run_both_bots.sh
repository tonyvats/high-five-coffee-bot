#!/bin/bash

echo "🚀 Запуск обоих ботов..."

# Проверяем, что Python установлен
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python3 и попробуйте снова."
    exit 1
fi

# Проверяем, что файлы ботов существуют
if [ ! -f "hfcbot.py" ]; then
    echo "❌ Файл hfcbot.py не найден!"
    exit 1
fi

if [ ! -f "hfctbot.py" ]; then
    echo "❌ Файл hfctbot.py не найден!"
    exit 1
fi

# Проверяем, что токен второго бота заменен
if grep -q "YOUR_NEW_BOT_TOKEN_HERE" hfctbot.py; then
    echo "⚠️  ВНИМАНИЕ: В файле hfctbot.py не заменен токен!"
    echo "   Замените 'YOUR_NEW_BOT_TOKEN_HERE' на ваш новый токен от @BotFather"
    echo "   См. файл NEW_BOT_SETUP.md для инструкций"
    exit 1
fi

echo "✅ Все проверки пройдены"
echo "📱 Запуск первого бота (hfcbot.py)..."
echo "📱 Запуск второго бота (hfctbot.py)..."

# Запускаем оба бота в фоне
python3 hfcbot.py > bot1.log 2>&1 &
BOT1_PID=$!

python3 hfctbot.py > bot2.log 2>&1 &
BOT2_PID=$!

echo "✅ Боты запущены!"
echo "📊 PID первого бота: $BOT1_PID"
echo "📊 PID второго бота: $BOT2_PID"
echo ""
echo "📝 Логи первого бота: bot1.log"
echo "📝 Логи второго бота: bot2.log"
echo ""
echo "🛑 Для остановки ботов выполните:"
echo "   kill $BOT1_PID $BOT2_PID"
echo ""
echo "🔍 Для просмотра логов в реальном времени:"
echo "   tail -f bot1.log  # в одном терминале"
echo "   tail -f bot2.log  # в другом терминале"

# Ждем завершения
wait
