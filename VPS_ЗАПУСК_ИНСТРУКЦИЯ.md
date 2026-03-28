# Запуск парсера на VPS Beget - АВТОМАТИЧЕСКИ

## Шаг 1: Открыть веб-консоль VPS

1. Зайдите на https://cp.beget.com/vps (через браузер **БЕЗ VPN**)
2. Найдите кнопку **"Консоль"** или **"Web SSH"**
3. Откроется терминал VPS

## Шаг 2: Выполнить команду установки

Скопируйте и вставьте в консоль VPS:

```bash
cd /root && curl -O https://raw.githubusercontent.com/YOUR_USERNAME/che168-parser/main/vps_auto_setup.sh && chmod +x vps_auto_setup.sh && bash vps_auto_setup.sh
```

**ИЛИ** (если GitHub не доступен):

```bash
apt update && apt upgrade -y
apt install -y python3 python3-pip git curl
mkdir -p /root/che168-parser && cd /root/che168-parser
pip3 install requests playwright
playwright install chromium
```

## Шаг 3: Создать файл парсера

В консоли VPS выполните:

```bash
cat > /root/che168-parser/run.py << 'EOF'
#!/usr/bin/env python3
import requests, re, json, time
from datetime import datetime

PROXIES = [
    {'http': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13851', 'https': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13851'},
    {'http': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13852', 'https': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13852'},
    {'http': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13853', 'https': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13853'},
]
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def parse():
    cars = []
    for proxy in PROXIES:
        if len(cars) >= 10: break
        try:
            resp = requests.get('https://www.che168.com/beijing/', proxies=proxy, headers=HEADERS, timeout=30)
            if resp.status_code == 200:
                for price in re.findall(r'(\d+\.?\d*)\s*万', resp.text):
                    if len(cars) < 10:
                        cars.append({'price_cny': float(price)*10000, 'price_rub': round(float(price)*10000*13, 2)})
        except: pass
        time.sleep(1)
    return cars

if __name__ == '__main__':
    cars = parse()
    print(f"Найдено: {len(cars)} авто")
    with open('/root/che168_result.json', 'w') as f:
        json.dump({'time': datetime.now().isoformat(), 'cars': cars}, f, indent=2, ensure_ascii=False)
EOF
```

## Шаг 4: Запустить парсер

```bash
python3 /root/che168-parser/run.py
```

## Шаг 5: Настроить автозапуск (cron)

```bash
(crontab -l 2>/dev/null; echo "*/15 * * * * /usr/bin/python3 /root/che168-parser/run.py >> /root/parse.log 2>&1") | crontab -
```

## Проверка результата

```bash
cat /root/che168_result.json
cat /root/parse.log
```

## Готово!

Парсер работает каждые 15 минут автоматически.
Результат: `/root/che168_result.json`

---

**Важно:** После настройки вы можете забрать результат через SFTP/FTP или настроить отправку в Telegram.
