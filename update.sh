#!/bin/bash

echo "🔄 Обновление High Five Coffee Bot..."

cd "$(dirname "$0")"

git pull || { echo "❌ Ошибка git pull"; exit 1; }

docker compose down
docker compose up -d --build

echo ""
echo "✅ Обновление завершено!"
echo ""
echo "📊 Статус:  docker compose ps"
echo "📝 Логи:    docker compose logs -f"
