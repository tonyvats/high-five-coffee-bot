# 🚀 Развёртывание на Яндекс Облаке

## 📋 Предварительные требования

1. **Аккаунт в Яндекс Облаке** с квотой
2. **Доменное имя** (для webhook)
3. **SSL сертификат** (можно получить бесплатно через Let's Encrypt)

## 🖥 Создание VPS в Яндекс Облаке

### Шаг 1: Создание виртуальной машины

1. **Войдите в [консоль Яндекс Облака](https://console.cloud.yandex.ru/)**
2. **Выберите ваш облачный каталог**
3. **Создайте новую виртуальную машину:**
   - **Имя:** `high-five-coffee-bot`
   - **Операционная система:** Ubuntu 20.04 LTS
   - **Размер:** 2 vCPU, 2 GB RAM (достаточно для бота)
   - **Диск:** 20 GB SSD
   - **Сеть:** Выберите вашу VPC
   - **Публичный IP:** Да (для доступа к серверу)

### Шаг 2: Настройка безопасности

1. **Создайте группу безопасности:**
   - **SSH:** порт 22 (ваш IP)
   - **HTTP:** порт 80
   - **HTTPS:** порт 443
   - **Bot API:** порт 8000

2. **Настройте firewall на сервере:**
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000
sudo ufw enable
```

## 🔧 Настройка сервера

### Шаг 1: Подключение к серверу
```bash
ssh ubuntu@YOUR_SERVER_IP
```

### Шаг 2: Обновление системы
```bash
sudo apt update && sudo apt upgrade -y
```

### Шаг 3: Установка Docker
```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Перезагрузка сессии
exit
# Подключитесь заново
ssh ubuntu@YOUR_SERVER_IP

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Шаг 4: Установка Nginx (для webhook)
```bash
sudo apt install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx
```

## 📁 Развёртывание бота

### Шаг 1: Клонирование репозитория
```bash
git clone https://github.com/tonyvats/high-five-coffee-bot.git
cd high-five-coffee-bot
```

### Шаг 2: Настройка переменных окружения
```bash
export BOT_TOKEN="ваш_токен_бота"
export ADMIN_IDS="462076,306535565"
```

### Шаг 3: Запуск развёртывания
```bash
chmod +x deploy.sh
./deploy.sh
```

## 🌐 Настройка Webhook (опционально)

### Шаг 1: Настройка Nginx
```bash
sudo nano /etc/nginx/sites-available/bot
```

Добавьте конфигурацию:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /webhook {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Шаг 2: Активация сайта
```bash
sudo ln -s /etc/nginx/sites-available/bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Шаг 3: SSL сертификат (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## 📊 Мониторинг и управление

### Просмотр логов
```bash
docker-compose logs -f
```

### Перезапуск бота
```bash
docker-compose restart
```

### Обновление бота
```bash
git pull
docker-compose down
docker-compose up -d --build
```

### Статус сервисов
```bash
docker-compose ps
sudo systemctl status nginx
```

## 🔒 Безопасность

1. **Регулярно обновляйте систему**
2. **Используйте SSH ключи вместо паролей**
3. **Настройте fail2ban для защиты от брутфорса**
4. **Регулярно делайте бэкапы**

## 💰 Стоимость

- **VPS 2 vCPU, 2 GB RAM:** ~300-500₽/месяц
- **Доменное имя:** ~100-500₽/год
- **SSL сертификат:** Бесплатно (Let's Encrypt)

## 🆘 Устранение неполадок

### Бот не отвечает
```bash
docker-compose logs telegram-bot
docker-compose ps
```

### Проблемы с webhook
```bash
curl -X POST https://your-domain.com/webhook
sudo nginx -t
```

### Нехватка ресурсов
```bash
htop
df -h
docker system df
```
