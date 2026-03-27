#!/usr/bin/env python3
"""
Проверка файла на Beget через WebDAV
"""

import requests
from requests.auth import HTTPBasicAuth

BEGET_LOGIN = 'ahilesor'
BEGET_PASSWORD = 'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

# Проверяем файл через WebDAV
webdav_url = f'https://webdav.beget.com/public_html/che168_parse.php'

print("=" * 60)
print("ПРОВЕРКА ФАЙЛА НА BEGET")
print("=" * 60)

try:
    response = requests.get(
        webdav_url,
        auth=HTTPBasicAuth(BEGET_LOGIN, BEGET_PASSWORD),
        timeout=30
    )
    print(f"\nСтатус HTTP: {response.status_code}")
    print(f"Размер: {len(response.text)} байт")

    if response.status_code == 200:
        print("\n[OK] Файл существует!")
        print("\nПервые 500 символов:")
        print(response.text[:500])
    else:
        print(f"\n[ERR] Ответ сервера: {response.text[:200]}")

except Exception as e:
    print(f"\n[ERR] Ошибка: {e}")

# Также проверим через API список файлов
print("\n" + "=" * 60)
print("СПИСОК ФАЙЛОВ В public_html")
print("=" * 60)

session = requests.Session()
session.auth = (BEGET_LOGIN, BEGET_PASSWORD)

try:
    response = session.get(
        'https://cp.beget.com/api/filemanager/list?path=/public_html',
        timeout=30
    )
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.text[:500]}")
except Exception as e:
    print(f"Ошибка: {e}")
