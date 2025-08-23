#!/bin/bash

echo "🚀 Развёртывание High Five Coffee Bot на Яндекс Облаке"

# Проверяем наличие переменных окружения
if [ -z "$BOT_TOKEN" ]; then
    echo "❌ Ошибка: BOT_TOKEN не установлен"
    echo "💡 Установите переменную: export BOT_TOKEN='ваш_токен'"
    exit 1
fi

if [ -z "$ADMIN_IDS" ]; then
    echo "❌ Ошибка: ADMIN_IDS не установлен"
    echo "💡 Установите переменную: export ADMIN_IDS='462076,306535565'"
    exit 1
fi

echo "✅ Переменные окружения настроены"

# Создаём .env файл
cat > .env << EOF
BOT_TOKEN=$BOT_TOKEN
ADMIN_IDS=$ADMIN_IDS
EOF

echo "✅ Файл .env создан"

# Собираем и запускаем Docker контейнер
echo "🐳 Собираем Docker образ..."
docker-compose build

echo "🚀 Запускаем бота..."
docker-compose up -d

echo "✅ Бот запущен!"
echo "📊 Статус: docker-compose ps"
echo "📝 Логи: docker-compose logs -f"
echo "🛑 Остановить: docker-compose down"
