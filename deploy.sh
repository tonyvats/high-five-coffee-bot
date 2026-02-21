#!/bin/bash

echo "🚀 Развёртывание High Five Coffee Bot + Админка на сервере"

# Если .env уже есть — подставляем старые значения для незаданных переменных (пароль не перетирается при повторном деплое)
if [ -f .env ]; then
    [ -z "$BOT_TOKEN" ]        && BOT_TOKEN=$(grep '^BOT_TOKEN=' .env 2>/dev/null | cut -d= -f2-)
    [ -z "$ADMIN_IDS" ]        && ADMIN_IDS=$(grep '^ADMIN_IDS=' .env 2>/dev/null | cut -d= -f2-)
    [ -z "$ADMIN_PASSWORD" ]  && ADMIN_PASSWORD=$(grep '^ADMIN_PASSWORD=' .env 2>/dev/null | cut -d= -f2-)
fi

# Проверяем наличие переменных окружения
if [ -z "$BOT_TOKEN" ]; then
    echo "❌ Ошибка: BOT_TOKEN не установлен"
    echo "💡 export BOT_TOKEN='ваш_прод_токен'"
    exit 1
fi

if [ -z "$ADMIN_IDS" ]; then
    echo "❌ Ошибка: ADMIN_IDS не установлен"
    echo "💡 export ADMIN_IDS='462076,306535565'"
    exit 1
fi

if [ -z "$ADMIN_PASSWORD" ]; then
    echo "❌ Ошибка: ADMIN_PASSWORD не установлен (пароль для входа в админку)"
    echo "💡 export ADMIN_PASSWORD='ваш_надёжный_пароль'"
    exit 1
fi

echo "✅ Переменные окружения проверены"

# Создаём .env для docker-compose
cat > .env << EOF
BOT_TOKEN=$BOT_TOKEN
ADMIN_IDS=$ADMIN_IDS
ADMIN_PASSWORD=$ADMIN_PASSWORD
ADMIN_SECRET_KEY=${ADMIN_SECRET_KEY:-$(openssl rand -hex 24 2>/dev/null || echo "change-me-in-production-$(date +%s)")}
EOF

echo "✅ Файл .env создан"

# docker compose (v2) или docker-compose (v1)
DC="docker compose"
docker compose version >/dev/null 2>&1 || DC="docker-compose"

echo "🐳 Собираем Docker образы..."
$DC build

echo "🚀 Запускаем сервисы..."
$DC up -d

echo ""
echo "✅ Развёртывание завершено!"
echo ""
echo "📊 Статус:  docker-compose ps"
echo "📝 Логи:    docker-compose logs -f"
echo "🛑 Стоп:    docker-compose down"
echo ""
echo "🤖 Бот:     работает (polling)"
echo "🌐 Админка: http://ВАШ_IP:5050  (пароль из ADMIN_PASSWORD)"
echo ""
echo "⚠️  Откройте порт 5050 в firewall для доступа к админке:"
echo "   sudo ufw allow 5050 && sudo ufw reload"
