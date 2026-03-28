#!/usr/bin/env python3
"""
Автоматическая настройка GitHub репозитория и запуск парсера
"""

import requests
import base64
import json

# Данные GitHub
USERNAME = 'kudryashov20091991-lang'
PASSWORD = '!1Vbkkbfhl _4'
REPO_NAME = 'che168-parser'

# Парсер для GitHub Actions
PARSER_CODE = '''#!/usr/bin/env python3
import requests, re, json, time
from datetime import datetime

PROXIES = [
    {"http": "http://Ek0G8F:GR0Fhj@45.32.56.105:13851", "https": "http://Ek0G8F:GR0Fhj@45.32.56.105:13851"},
    {"http": "http://Ek0G8F:GR0Fhj@45.32.56.105:13852", "https": "http://Ek0G8F:GR0Fhj@45.32.56.105:13852"},
    {"http": "http://Ek0G8F:GR0Fhj@45.32.56.105:13853", "https": "http://Ek0G8F:GR0Fhj@45.32.56.105:13853"},
]
HEADERS = {"User-Agent": "Mozilla/5.0"}

def parse():
    cars = []
    for proxy in PROXIES:
        if len(cars) >= 10: break
        try:
            resp = requests.get("https://www.che168.com/beijing/", proxies=proxy, headers=HEADERS, timeout=30)
            if resp.status_code == 200:
                for p in re.findall(r"(\\d+\\.?\\d*)\\s*", resp.text):
                    if len(cars) < 10:
                        cars.append({"price_cny": float(p)*10000, "price_rub": round(float(p)*10000*13, 2), "proxy": proxy["http"].split("@")[1]})
        except: pass
        time.sleep(1)
    return cars

if __name__ == "__main__":
    result = parse()
    print(f"Found: {len(result)} cars")
    with open("che168_result.json", "w", encoding="utf-8") as f:
        json.dump({"time": datetime.now().isoformat(), "cars": result}, f, indent=2, ensure_ascii=False)
'''

WORKFLOW_CODE = '''name: Che168 Parser
on:
  workflow_dispatch:
  schedule:
    - cron: '0 */6 * * *'
jobs:
  parse:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with: {python-version: '3.12'}
    - run: pip install requests
    - run: python che168_parser.py
    - uses: actions/upload-artifact@v4
      with: {name: che168-result, path: che168_result.json, retention-days: 30}
'''

print("=" * 60)
print("НАСТРОЙКА GITHUB ACTIONS")
print("=" * 60)

session = requests.Session()
session.auth = (USERNAME, PASSWORD)

# 1. Создание репозитория
print("\n[1] Создание репозитория...")
repo_data = {
    "name": REPO_NAME,
    "private": False,
    "auto_init": True
}
r = session.post('https://api.github.com/user/repos', json=repo_data)
print(f"    Статус: {r.status_code}")
if r.status_code == 201:
    print("    Репозиторий создан!")
elif r.status_code == 422:
    print("    Репозиторий уже существует")
else:
    print(f"    Ошибка: {r.text[:200]}")

# 2. Загрузка парсера
print("\n[2] Загрузка парсера...")
parser_data = {
    "message": "Add che168 parser",
    "content": base64.b64encode(PARSER_CODE.encode()).decode()
}
r = session.put(f'https://api.github.com/repos/{USERNAME}/{REPO_NAME}/contents/che168_parser.py', json=parser_data)
print(f"    Статус: {r.status_code}")

# 3. Загрузка workflow
print("\n[3] Загрузка workflow...")
workflow_data = {
    "message": "Add GitHub Actions workflow",
    "content": base64.b64encode(WORKFLOW_CODE.encode()).decode()
}
r = session.put(f'https://api.github.com/repos/{USERNAME}/{REPO_NAME}/contents/.github/workflows/che168_parse.yml', json=workflow_data)
print(f"    Статус: {r.status_code}")

# 4. Загрузка requirements.txt
print("\n[4] Загрузка requirements.txt...")
req_data = {
    "message": "Add requirements",
    "content": base64.b64encode(b"requests").decode()
}
r = session.put(f'https://api.github.com/repos/{USERNAME}/{REPO_NAME}/contents/requirements.txt', json=req_data)
print(f"    Статус: {r.status_code}")

print("\n" + "=" * 60)
print("ГОТОВО!")
print("=" * 60)
print(f"\nРепозиторий: https://github.com/{USERNAME}/{REPO_NAME}")
print(f"Actions: https://github.com/{USERNAME}/{REPO_NAME}/actions")
print("\nДля запуска:")
print("1. Откройте Actions (ссылка выше)")
print("2. Click 'Che168 Parser' → 'Run workflow'")
print("3. Через 2 мин скачайте результат из артефактов")
