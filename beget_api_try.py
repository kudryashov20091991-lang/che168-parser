"""
Загрузка на Beget через правильный API
"""
import requests
import json

API_USER = 'ahilesor'
API_PASS = r'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

# Читаем файл
script_path = r'C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры\che168_beget_final.php'
with open(script_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Файл: {len(content)} байт")

session = requests.Session()
session.auth = (API_USER, API_PASS)
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/json',
})

# Пробуем разные endpoints API
endpoints = [
    'https://api.beget.com/filemanager/write',
    'https://api.beget.com/file/write',
    'https://api.beget.com/bulk/file_write',
    'https://cp.beget.com/api/filemanager/write',
]

for url in endpoints:
    print(f"\nПробую: {url}")

    # Пробуем с параметрами
    resp = session.post(url, params={
        'path': '/public_html/che168_parse.php',
        'content': content
    }, timeout=15)

    print(f"  Status: {resp.status_code}")
    if resp.status_code == 200:
        try:
            data = resp.json()
            print(f"  Response: {data}")
            if data.get('error') is None or data.get('result'):
                print("  УСПЕХ!")
                break
        except:
            print(f"  Response: {resp.text[:200]}")

print("\nГотово!")
