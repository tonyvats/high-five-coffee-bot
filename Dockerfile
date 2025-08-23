FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота
COPY . .

# Создаём пользователя для безопасности
RUN useradd --create-home --shell /bin/bash bot
RUN chown -R bot:bot /app
USER bot

# Открываем порт для webhook (если понадобится)
EXPOSE 8000

# Запускаем бота
CMD ["python", "hfcbot.py"]
