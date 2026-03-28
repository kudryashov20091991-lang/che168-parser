#!/bin/bash
# Автоматическая настройка VPS для парсинга
# Запустить через веб-консоль Beget

echo "=== НАСТРОЙКА VPS ДЛЯ ПАРСИНГА ==="

# Обновление
apt update && apt upgrade -y

# Установка Python, pip, git
apt install -y python3 python3-pip git curl

# Создание директории
mkdir -p /root/che168-parser
cd /root/che168-parser

# Скачивание парсера с GitHub (замените URL на ваш)
git clone https://github.com/YOUR_USERNAME/che168-parser.git . 2>/dev/null || {
    echo "GitHub не доступен, создаю локальный парсер..."
}

# Установка зависимостей
pip3 install requests playwright
playwright install chromium

# Создание файла запуска
cat > /root/che168-parser/run.py << 'PYTHON'
#!/usr/bin/env python3
import requests
import re
import json
import time
from datetime import datetime

PROXIES = [
    {'http': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13851', 'https': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13851'},
    {'http': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13852', 'https': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13852'},
    {'http': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13853', 'https': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13853'},
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def parse():
    cars = []
    for i, proxy in enumerate(PROXIES):
        if len(cars) >= 10:
            break
        try:
            resp = requests.get('https://www.che168.com/beijing/', proxies=proxy, headers=HEADERS, timeout=30)
            if resp.status_code == 200:
                prices = re.findall(r'(\d+\.?\d*)\s*万', resp.text)
                for price in prices:
                    if len(cars) < 10:
                        cars.append({'price_cny': float(price)*10000, 'price_rub': round(float(price)*10000*13, 2)})
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(1)
    return cars

if __name__ == '__main__':
    print(f"Запуск: {datetime.now()}")
    cars = parse()
    print(f"Найдено авто: {len(cars)}")
    with open('/root/che168_result.json', 'w') as f:
        json.dump({'timestamp': datetime.now().isoformat(), 'cars': cars}, f, indent=2)
    print("Результат: /root/che168_result.json")
PYTHON

# Запуск парсера
echo "Запуск парсера..."
python3 /root/che168-parser/run.py

# Настройка cron (запуск каждые 15 минут)
echo "Настройка cron..."
(crontab -l 2>/dev/null; echo "*/15 * * * * /usr/bin/python3 /root/che168-parser/run.py >> /root/parse.log 2>&1") | crontab -

echo "=== ГОТОВО ==="
echo "Результат: /root/che168_result.json"
echo "Лог: /root/parse.log"
echo "Cron: каждые 15 минут"
