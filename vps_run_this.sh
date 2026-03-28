#!/bin/bash
# Запустить один раз через веб-консоль Beget VPS

echo "=== УСТАНОВКА ПАРСЕРА ==="

# Установка зависимостей
apt update -y
apt install -y python3 python3-pip curl
pip3 install requests playwright
playwright install chromium --force

# Создание парсера
cat > /root/che168_parser.py << 'PYEOF'
#!/usr/bin/env python3
import requests, re, json, time
from datetime import datetime

PROXIES = [
    "http://Ek0G8F:GR0Fhj@45.32.56.105:13851",
    "http://Ek0G8F:GR0Fhj@45.32.56.105:13852",
    "http://Ek0G8F:GR0Fhj@45.32.56.105:13853",
]
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def parse():
    cars = []
    for proxy_url in PROXIES:
        if len(cars) >= 10:
            break
        proxy = {"http": proxy_url, "https": proxy_url}
        try:
            resp = requests.get("https://www.che168.com/beijing/", proxies=proxy, headers=HEADERS, timeout=30)
            if resp.status_code == 200 and len(resp.text) > 1000:
                prices = re.findall(r"(\d+\.?\d*)\s*", resp.text)
                for p in prices:
                    if len(cars) < 10:
                        price_cny = float(p) * 10000
                        cars.append({"price_cny": price_cny, "price_rub": round(price_cny * 13, 2), "proxy": proxy_url.split("@")[1]})
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(1)
    return cars

if __name__ == "__main__":
    print(f"Запуск: {datetime.now()}")
    result = parse()
    print(f"Найдено авто: {len(result)}")
    output = {"timestamp": datetime.now().isoformat(), "source": "che168.com", "cars": result}
    with open("/root/che168_result.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Сохранено: /root/che168_result.json")
PYEOF

chmod +x /root/che168_parser.py

# Первый запуск
echo "Запуск парсера..."
python3 /root/che168_parser.py

# Настройка cron (каждые 15 минут)
echo "Настройка автозапуска..."
(crontab -l 2>/dev/null; echo "*/15 * * * * /usr/bin/python3 /root/che168_parser.py >> /root/parse.log 2>&1") | crontab -

echo "=== ГОТОВО ==="
echo "Результат: cat /root/che168_result.json"
echo "Лог: cat /root/parse.log"
echo "Cron: каждые 15 минут"
