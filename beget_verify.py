#!/usr/bin/env python3
"""
Проверка содержимого файла на Beget
"""

import requests

BEGET_LOGIN = 'ahilesor'
BEGET_PASSWORD = 'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

# Логин
login_data = {
    'login': BEGET_LOGIN,
    'password': BEGET_PASSWORD,
    'remember': 1,
    'last_input': 'login'
}
session.post('https://cp.beget.com/login', data=login_data)

print("=" * 60)
print("ПРОВЕРКА ФАЙЛА che168_parse.php")
print("=" * 60)

# Читаем файл через файловый API
read_data = {
    'path': 'public_html/che168_parse.php',
    'action': 'read'
}

response = session.post(
    'https://cp.beget.com/api/filemanager/read',
    data=read_data,
    timeout=30
)

print(f"\nСтатус: {response.status_code}")
print(f"Ответ: {response.text[:1000]}")

if response.status_code == 200 and 'function' in response.text:
    print("\n[OK] PHP код на месте!")
else:
    print("\n[WARN] Нужно проверить вручную")
