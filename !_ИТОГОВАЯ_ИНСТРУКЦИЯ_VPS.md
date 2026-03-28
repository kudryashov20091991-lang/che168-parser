# ЗАПУСК ПАРСЕРА НА VPS BEGET - ПОЛНАЯ ИНСТРУКЦИЯ

## Проблема
VPN на вашем ПК блокирует SSH/FTP подключения к Beget VPS.
HTTP/HTTPS работают, но веб-консоль требует прямого подключения.

## Решение

### Вариант 1: Веб-консоль Beget (рекомендуется)

**Шаг 1:** Откройте браузер **БЕЗ VPN**

**Шаг 2:** Зайдите на https://cp.beget.com/vps
- Логин: `ahilesor`
- Пароль: `TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:`

**Шаг 3:** Найдите кнопку **"Консоль"** или **"Web SSH"**

**Шаг 4:** Скопируйте и вставьте этот скрипт в консоль:

```bash
#!/bin/bash
echo "=== УСТАНОВКА ПАРСЕРА ==="
apt update -y
apt install -y python3 python3-pip curl
pip3 install requests playwright
playwright install chromium --force

cat > /root/che168_parser.py << 'PYEOF'
#!/usr/bin/env python3
import requests, re, json, time
from datetime import datetime

PROXIES = [
    "http://Ek0G8F:GR0Fhj@45.32.56.105:13851",
    "http://Ek0G8F:GR0Fhj@45.32.56.105:13852",
    "http://Ek0G8F:GR0Fhj@45.32.56.105:13853",
]
HEADERS = {"User-Agent": "Mozilla/5.0"}

def parse():
    cars = []
    for proxy_url in PROXIES:
        if len(cars) >= 10: break
        proxy = {"http": proxy_url, "https": proxy_url}
        try:
            resp = requests.get("https://www.che168.com/beijing/", proxies=proxy, headers=HEADERS, timeout=30)
            if resp.status_code == 200:
                for p in re.findall(r"(\d+\.?\d*)\s*", resp.text):
                    if len(cars) < 10:
                        cars.append({"price_cny": float(p)*10000, "price_rub": round(float(p)*10000*13, 2)})
        except: pass
        time.sleep(1)
    return cars

if __name__ == "__main__":
    result = parse()
    print(f"Найдено: {len(result)}")
    with open("/root/che168_result.json", "w", encoding="utf-8") as f:
        json.dump({"time": datetime.now().isoformat(), "cars": result}, f, indent=2, ensure_ascii=False)
PYEOF

chmod +x /root/che168_parser.py
python3 /root/che168_parser.py
(crontab -l 2>/dev/null; echo "*/15 * * * * /usr/bin/python3 /root/che168_parser.py") | crontab -
echo "=== ГОТОВО ==="
```

**Шаг 5:** Нажмите Enter и дождитесь установки (2-3 минуты)

---

### Вариант 2: Локальный запуск (если VPN мешает)

Откройте PowerShell и выполните:

```powershell
cd "C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры"
python che168_github_action.py
```

Результат: `che168_result.json` в той же папке

---

### Вариант 3: GitHub Actions (полностью автономно)

1. Создайте репозиторий на GitHub
2. Запушите файлы из папки `Парсеры`
3. Actions → Che168 Parser → Run workflow

---

## Проверка результата

После запуска скрипта на VPS:

```bash
cat /root/che168_result.json
cat /root/parse.log
```

## Автономная работа

После настройки cron парсер запускается автоматически каждые 15 минут.
Вы можете быть не за ПК - VPS работает 24/7.

---

## Файлы для настройки

- `vps_run_this.sh` - готовый скрипт для копирования в консоль
- `VPS_ЗАПУСК_ИНСТРУКЦИЯ.md` - подробная инструкция
- `che168_github_action.py` - локальная версия парсера
